"""
cargador_sublitex.py  -  Tarea 1 · Pipeline de indexacion (Sublitex)
--------------------------------------------------------------------
Genera los vectores de los disenos de Sublitex SIN tocar el indice de Aimari.

Contrato de datos aplicado (SECCION 00 / core.sublitex):
  - codigo:     SBX-NN-NNNN (^SBX-\\d{2}-\\d{4}$), derivado del nombre del PNG.
                NN = carpeta de origen (01..99), NNNN = correlativo (0001..9999).
  - planilla:   "Control de exportacion" (CSV o XLSX) con 9 columnas:
                codigo, carpeta_origen, archivo_original, tipo, deporte,
                ocasion, estado, quien, fecha
  - hoja Listas: numero de carpeta -> carpeta real del Drive (o CSV --mapa).

Trazabilidad que garantiza:
  imagen publicada (PNG) -> codigo -> carpeta_origen + archivo_original
  -> carpeta real (Listas) + archivo_original -> CDR original.

Reglas:
  - Un PNG cuyo codigo no tenga fila completa en la planilla se rechaza y se
    reporta; jamas se fabrican carpeta_origen ni archivo_original.
  - Un registro incompleto (sin carpeta_origen o archivo_original) no se indexa.
  - No se toca ni un solo CDR (ver core.cdr_seguridad). Solo se genera la ruta.
  - Los vectores se persisten en una coleccion Qdrant independiente
    (sublitex_fashion_v1) y respaldos .npy, mas un catalogo JSON con la
    trazabilidad completa.

Uso:
    python scripts/cargador_sublitex.py --image_folder ruta/png \
        --csv_path "ruta/Control de exportacion.xlsx"
    python scripts/cargador_sublitex.py --image_folder ruta/png \
        --csv_path ruta/control_exportacion.csv --mapa ruta/listas.csv
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime

import numpy as np
from PIL import Image

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from core.base_datos import QdrantManager
from core.sublitex import (
    COLUMNAS_PLANILLA,
    ErrorTrazabilidad,
    enriquecer_registro,
    filas_por_codigo,
    leer_mapa,
    leer_planilla,
    validar_codigo,
)
from core.vision_pipeline import VisionPipeline
from qdrant_client.http.models import PointStruct

COLECCION = "sublitex_fashion_v1"


class ErrorIntegridad(Exception):
    """Longitud(vectores) != longitud(IDs) u otra corrupcion del indice."""


def _pngs_de(image_folder):
    return sorted(
        nombre
        for nombre in os.listdir(image_folder)
        if nombre.lower().endswith(".png")
    )


def _extraer_embeddings(candidatos, pipeline):
    vectores = []
    ids = []
    for ruta, codigo in candidatos:
        imagen = Image.open(ruta).convert("RGB")
        vector = pipeline.process_image(imagen)["embedding"]
        vectores.append(vector)
        ids.append(codigo)
        print("Vectorizado correctamente: {}".format(codigo))
    return np.array(vectores, dtype=np.float32), ids


def verificar_integridad(vectores, ids):
    """Regla 12: cantidad_de_vectores == cantidad_de_IDs (fallo claro si no).

    Devuelve el par (vectores, ids) si todo cuadra; en otro caso eleva
    ErrorIntegridad indicando ambos contadores y la dimension de cada vector.
    """
    if len(vectores) != len(ids):
        raise ErrorIntegridad(
            "Longitud(vectores)={} != Longitud(IDs)={}. ".format(len(vectores), len(ids))
            + "Abortando: el indice quedaria corrupto."
        )
    if len(vectores) == 0:
        raise ErrorIntegridad("No hay vectores ni IDs que persistir.")
    if not all(v.shape == vectores[0].shape for v in vectores):
        raise ErrorIntegridad(
            "Dimension de los vectores inconsistente: {}.".format(
                sorted({v.shape for v in vectores})
            )
        )
    return vectores, ids


def _persistir(vectores, ids, catalogo, errores, salida_catalogo, salida_errores):
    qdrant_manager = QdrantManager(collection_name=COLECCION)
    puntos = [
        PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_OID, registro["codigo"])),
            vector=vector.tolist(),
            payload=registro,
        )
        for vector, registro in zip(vectores, catalogo)
    ]
    qdrant_manager.upsert_vectors(puntos)

    np.save(os.path.join(BASE_DIR, "data", "embeddings_sublitex.npy"), vectores)
    np.save(os.path.join(BASE_DIR, "data", "ids_sublitex.npy"), np.array(ids))

    informe_catalogo = {
        "coleccion_qdrant": COLECCION,
        "modelo": "YOLO + rembg + SigLIP (google/siglip-base-patch16-224, 768 dim) "
                  "- mismo pipeline de produccion, indice separado",
        "generado": datetime.now().isoformat(timespec="seconds"),
        "registros": catalogo,
    }
    with open(salida_catalogo, "w", encoding="utf-8") as f:
        json.dump(informe_catalogo, f, ensure_ascii=False, indent=2)

    with open(salida_errores, "w", encoding="utf-8") as f:
        json.dump(errores, f, ensure_ascii=False, indent=2)


def _guardar_errores(errores, salida_errores):
    with open(salida_errores, "w", encoding="utf-8") as f:
        json.dump(errores, f, ensure_ascii=False, indent=2)


def process_sublitex(image_folder, planilla_path, hoja, mapa_path,
                     salida_catalogo, salida_errores):
    print("Iniciando cargador de indexacion para Sublitex...")

    if not os.path.isdir(image_folder):
        print("Error: No se encontro la carpeta de imagenes en {}".format(image_folder))
        return 1
    if not os.path.isfile(planilla_path):
        print("Error: No se encontro la planilla de control en {}".format(planilla_path))
        return 1

    lectura = leer_planilla(planilla_path)
    filas = lectura["filas"]
    for indice, fila in enumerate(filas, start=2):
        fila["_fila"] = indice
    faltantes = [c for c in COLUMNAS_PLANILLA if c not in lectura["columnas"]]
    print("Planilla: {} - {} filas, {} columnas.".format(
        lectura["formato"], len(filas), len(lectura["columnas"])))
    if faltantes:
        print("AVISO: faltan columnas en la planilla: {}".format(", ".join(faltantes)))

    try:
        mapa = leer_mapa(planilla_path, hoja, mapa_path)
    except ErrorTrazabilidad as error:
        print("Error: No se puede construir el mapa de carpetas: {}".format(error))
        return 1
    print("Mapa de carpetas ({}): {} entradas.".format(mapa["origen"], len(mapa["entradas"])))

    indice_filas, codigos_duplicados = filas_por_codigo(filas)
    if codigos_duplicados:
        print("AVISO: codigos duplicados en la planilla: {}".format(", ".join(codigos_duplicados)))

    pipeline = VisionPipeline()
    errores = []
    catalogo = []
    candidatos = []
    codigos_png = set()

    for nombre in _pngs_de(image_folder):
        codigo = os.path.splitext(nombre)[0]
        codigos_png.add(codigo)
        if not validar_codigo(codigo):
            errores.append({
                "tipo": "png_invalido",
                "codigo": codigo,
                "archivo": nombre,
                "detalle": "El nombre no cumple SBX-NN-NNNN (^SBX-\\d{2}-\\d{4}$).",
            })
            continue
        if codigo not in indice_filas:
            errores.append({
                "tipo": "png_sin_fila",
                "codigo": codigo,
                "archivo": nombre,
                "detalle": "El PNG no tiene fila en la planilla.",
            })
            continue
        if codigo in codigos_duplicados:
            errores.append({
                "tipo": "codigo_duplicado",
                "codigo": codigo,
                "archivo": nombre,
                "detalle": "Codigo duplicado en la planilla; se omite por ambiguedad.",
            })
            continue
        fila = indice_filas[codigo]
        try:
            registro = enriquecer_registro(fila, mapa, png=nombre)
        except ErrorTrazabilidad as error:
            errores.append({
                "tipo": "registro_incompleto",
                "codigo": codigo,
                "archivo": nombre,
                "detalle": str(error),
            })
            continue
        catalogo.append(registro)
        candidatos.append((os.path.join(image_folder, nombre), codigo))

    for codigo in sorted(set(indice_filas) - codigos_png):
        errores.append({
            "tipo": "fila_sin_png",
            "codigo": codigo,
            "archivo": "",
            "detalle": "La planilla tiene el codigo pero no se encontro su PNG.",
        })

    if not candidatos:
        print("No se procesaron vectores validos.")
        _guardar_errores(errores, salida_errores)
        return 1

    print("Comprobacion de integridad: longitud(vectores) == longitud(IDs).")
    vectores, ids = _extraer_embeddings(candidatos, pipeline)
    try:
        vectores, ids = verificar_integridad(vectores, ids)
    except ErrorIntegridad as error:
        print("ALERTA CRITICA: {} Abortando exportacion.".format(error))
        return 1

    print("Persistiendo en Qdrant (coleccion: {})...".format(COLECCION))
    _persistir(vectores, ids, catalogo, errores, salida_catalogo, salida_errores)

    print("\nFinalizado exitosamente. Se insertaron {} vectores.".format(len(ids)))
    print("Catalogo trazable: {}".format(salida_catalogo))
    print("Reporte de errores: {}".format(salida_errores))
    if errores:
        print("\nErrores y omisiones ({}):".format(len(errores)))
        for error in errores:
            print("- [{}] {}{}".format(
                error["tipo"],
                error["codigo"] or error.get("archivo", ""),
                " -> " + error["detalle"] if error.get("detalle") else "",
            ))
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de indexacion Sublitex con trazabilidad completa."
    )
    parser.add_argument("--image_folder", type=str, required=True,
                        help="Ruta a la carpeta con archivos SBX-NN-NNNN.png")
    parser.add_argument("--csv_path", type=str, required=True,
                        help="Ruta al archivo Control de exportacion (CSV o XLSX)")
    parser.add_argument("--hoja", type=str, default="Listas",
                        help="Nombre de la hoja del mapa de carpetas (defecto: Listas)")
    parser.add_argument("--mapa", type=str, default=None,
                        help="Ruta a un CSV del mapa numero->carpeta (si la planilla es CSV)")
    parser.add_argument("--salida_catalogo", type=str,
                        default=os.path.join(BASE_DIR, "data", "catalogo_sublitex.json"),
                        help="JSON con el catalogo trazable")
    parser.add_argument("--salida_errores", type=str,
                        default=os.path.join(BASE_DIR, "data", "errores_carga_sublitex.json"),
                        help="JSON con PNG/filas rechazados")
    args = parser.parse_args()

    sys.exit(process_sublitex(
        args.image_folder,
        args.csv_path,
        args.hoja,
        args.mapa,
        args.salida_catalogo,
        args.salida_errores,
    ))


if __name__ == "__main__":
    main()