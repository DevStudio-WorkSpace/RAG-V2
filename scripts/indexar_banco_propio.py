"""
indexar_banco_propio.py  -  Indexa el banco de imagenes propio en Qdrant.
--------------------------------------------------------------------
Genera los embeddings del banco nuevo (por defecto data/imagenes_normalized)
con el MISMO pipeline de produccion (YOLO + rembg + SigLIP, 768 dim) y los
persiste en una coleccion Qdrant independiente ("banco_propio_v1").

Es re-ejecutable: cuando agregues mas imagenes a la carpeta, volve a correrlo
y hace upsert (no duplica). NO toca las colecciones de Aimari ni de Sublitex.

Uso:
    python scripts/indexar_banco_propio.py
    python scripts/indexar_banco_propio.py --carpetas data/imagenes_normalized \
        data/demo_sublitex/png_publicados
    python scripts/indexar_banco_propio.py --recrear   # borra y reindexa de cero

Nota: para poder escribir en qdrant_data/ el servidor uvicorn debe estar
detenido (Qdrant local bloquea la carpeta mientras corre).
"""

import argparse
import os
import sys
import time
import uuid

import numpy as np
from PIL import Image

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from core.base_datos import QdrantManager
from core.vision_pipeline import VisionPipeline
from qdrant_client.http.models import PointStruct

COLECCION = "banco_propio_v1"
CARPETAS_POR_DEFECTO = [os.path.join("data", "imagenes_normalized")]
EXTENSIONES = (".jpg", ".jpeg", ".png", ".webp")


def _imagenes_de(carpeta, recursivo=False):
    """Devuelve las rutas de imagenes de una carpeta (no recursivo por defecto)."""
    if not os.path.isdir(carpeta):
        return []
    rutas = []
    if recursivo:
        for raiz, _, archivos in os.walk(carpeta):
            for nombre in archivos:
                if nombre.lower().endswith(EXTENSIONES):
                    rutas.append(os.path.join(raiz, nombre))
    else:
        for nombre in os.listdir(carpeta):
            ruta = os.path.join(carpeta, nombre)
            if os.path.isfile(ruta) and nombre.lower().endswith(EXTENSIONES):
                rutas.append(ruta)
    return sorted(rutas)


def _ids_existentes(manager):
    """IDs de puntos ya presentes en la coleccion (para indexado incremental)."""
    existentes = set()
    offset = None
    while True:
        puntos, offset = manager.client.scroll(
            collection_name=manager.collection_name,
            limit=256,
            offset=offset,
            with_payload=False,
            with_vectors=False,
        )
        if not puntos:
            break
        existentes.update(str(punto.id) for punto in puntos)
        if offset is None:
            break
    return existentes


def indexar(carpetas, coleccion, recursivo, recrear, batch, solo_nuevas=False):
    rutas = []
    for carpeta in carpetas:
        encontradas = _imagenes_de(carpeta, recursivo)
        print("Carpeta {}: {} imagenes.".format(carpeta, len(encontradas)))
        rutas.extend(encontradas)

    if not rutas:
        print("No se encontraron imagenes en: {}".format(", ".join(carpetas)))
        return 1

    print("Inicializando pipeline (YOLO + rembg + SigLIP)...")
    pipeline = VisionPipeline()

    print("Conectando a Qdrant (coleccion: {})...".format(coleccion))
    if recrear:
        print("--recrear: eliminando coleccion previa...")
        previo = QdrantManager(collection_name=coleccion)
        previo.client.delete_collection(collection_name=coleccion)
    manager = QdrantManager(collection_name=coleccion)

    ids_existentes = set()
    if solo_nuevas and not recrear:
        ids_existentes = _ids_existentes(manager)
        print("--solo-nuevas: {} puntos ya indexados; se omiten.".format(len(ids_existentes)))

    pendientes = []
    vectores = []
    ids = []
    omitidas = 0
    t0 = time.perf_counter()

    for indice, ruta in enumerate(rutas, start=1):
        nombre = os.path.basename(ruta)
        original_id = os.path.splitext(nombre)[0]
        rel = os.path.relpath(ruta, BASE_DIR).replace(os.sep, "/")
        punto_id = str(uuid.uuid5(uuid.NAMESPACE_OID, rel))

        if punto_id in ids_existentes:
            omitidas += 1
            continue

        try:
            imagen = Image.open(ruta).convert("RGB")
        except Exception as error:
            print("AVISO: no se pudo abrir {}: {}".format(ruta, error))
            continue

        resultado = pipeline.process_image(imagen)
        vector = np.asarray(resultado["embedding"], dtype=np.float32)
        color = resultado["color"]

        pendientes.append(PointStruct(
            id=punto_id,
            vector=vector.tolist(),
            payload={
                "filename": nombre,
                "original_id": original_id,
                "color": color,
                "source": rel,
            },
        ))
        vectores.append(vector)
        ids.append(original_id)
        print("[{}/{}] {} -> color={}".format(indice, len(rutas), nombre, color))

        if len(pendientes) >= batch:
            manager.upsert_vectors(pendientes)
            pendientes = []

    if pendientes:
        manager.upsert_vectors(pendientes)

    np.save(
        os.path.join(BASE_DIR, "data", "embeddings_banco_propio.npy"),
        np.array(vectores, dtype=np.float32),
    )
    np.save(
        os.path.join(BASE_DIR, "data", "ids_banco_propio.npy"),
        np.array(ids),
    )

    total = manager.client.count(manager.collection_name).count
    if omitidas:
        print("Se omitieron {} imagenes ya indexadas (--solo-nuevas).".format(omitidas))
    print("\nListo. Se indexaron {} vectores nuevos en '{}' (total en la coleccion: {}).".format(
        len(ids), coleccion, total))
    print("Tiempo total: {:.1f} s".format(time.perf_counter() - t0))
    print("Para buscar con esto, el servidor debe usar la coleccion '{}'.".format(coleccion))
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Indexa el banco de imagenes propio en una coleccion Qdrant."
    )
    parser.add_argument(
        "--carpetas", type=str, nargs="+", default=CARPETAS_POR_DEFECTO,
        help="Carpetas con imagenes del banco (defecto: data/imagenes_normalized)",
    )
    parser.add_argument(
        "--coleccion", type=str, default=COLECCION,
        help="Nombre de la coleccion Qdrant (defecto: banco_propio_v1)",
    )
    parser.add_argument(
        "--recursivo", action="store_true",
        help="Buscar imagenes tambien en subcarpetas",
    )
    parser.add_argument(
        "--recrear", action="store_true",
        help="Eliminar la coleccion antes de indexar (reindexado limpio)",
    )
    parser.add_argument(
        "--solo-nuevas", action="store_true", dest="solo_nuevas",
        help="Omitir imagenes ya indexadas (indexado incremental, mucho mas rapido)",
    )
    parser.add_argument(
        "--batch", type=int, default=64,
        help="Tamano de lote de upsert (defecto: 64)",
    )
    args = parser.parse_args()

    carpetas = [c if os.path.isabs(c) else os.path.join(BASE_DIR, c) for c in args.carpetas]
    sys.exit(indexar(
        carpetas, args.coleccion, args.recursivo, args.recrear, args.batch,
        solo_nuevas=args.solo_nuevas,
    ))


if __name__ == "__main__":
    main()
