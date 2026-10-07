"""
core.adaptador_imagenes
-----------------------
Integra imagenes legacy (JPG descriptivos) al flujo Sublitex SIN inventar
trazabilidad.

Cadena objetivo por imagen (todas verificadas o la imagen queda pendiente):

    JPG existente -> CDR original -> carpeta_origen -> archivo_original
    -> codigo SBX-NN-NNNN -> PNG publicado (SBX-NN-NNNN.png)

Reglas duras:

  1. NUNCA se asigna un codigo por orden (primero -> SBX-03-0001...). Un codigo
     solo se acepta si viene de una EVIDENCIA explicita que relacione el JPG
     con su CDR: el mismo contenido que ya llenan los disenadores en la
     planilla "Control de exportacion" (codigo, carpeta_origen,
     archivo_original, tipo, deporte, ocasion, estado, quien, fecha), ahora
     vinculado al nombre del JPG.
  2. Sin evidencia verificable, la imagen queda PENDIENTE y se registra
     exactamente que informacion falta. No se inventa codigo, carpeta_origen
     ni archivo_original y NO se genera PNG.
  3. El PNG publicado se genera desde el JPG (copia). El JPG NO se destruye y
     el CDR original NO se toca (politica de core.cdr_seguridad).
  4. El resultado integrado (PNG SBX-NN-NNNN.png + fila "Control de
     exportacion" de 9 columnas) es exactamente el insumo que consume
     scripts/cargador_sublitex.py.

Fuentes auxiliares (nunca asignan codigo por si solas):
  - EXIF del JPG: se registra (artista/descripcion/software) como dato de
    origen; las 44 imagenes actuales traen marcas de terceros
    (vectorsport.net, Zaugrafic, Ganshop, ClickArtz, Aimari Ec, ...), es
    decir, fueron descargadas, no son exportaciones planas de un CDR.
  - Mapa de carpetas (hoja Listas): carpeta_origen -> carpeta real del Drive,
    usada para reconstruir ruta_cdr del registro verificado.
"""

import json
import os

from PIL import Image  # pip install pillow

# Imagenes legitimas muy grandes (3 de las 44 tienen ~117M px) disparan el
# DecompressionBombError de Pillow al abrirse; se amplia el limite igual que
# en scripts/consolidar.py.
Image.MAX_IMAGE_PIXELS = None

from core.sublitex import (  # noqa: E402  (import tras tope del limite Pillow)
    COLUMNAS_PLANILLA,
    enriquecer_registro,
    validar_codigo,
)

# Columnas de la planilla "Control de exportacion" (contrato unico).
# EVIDENCIA: el mapeo imagen -> fila completa debe contener este mismo set,
# y la fila verificado se escribe solo con estas 9 columnas.
COLUMNA_IMAGEN = "imagen_jpg"

TAG_DESCRIPCION = 270  # EXIF ImageDescription
TAG_ARTISTA = 315  # EXIF Artist
TAG_SOFTWARE = 305  # EXIF Software


def origen_exif(ruta_jpg):
    """Datos EXIF de origen de un JPG (solo lectura). Devuelve artista,
    descripcion y software; vacios si no hay EXIF o no se puede leer."""
    resultado = {"artista": "", "descripcion": "", "software": ""}
    try:
        with Image.open(ruta_jpg) as imagen:
            exif = imagen.getexif()
        if exif:
            for tag, clave in (
                (TAG_ARTISTA, "artista"),
                (TAG_DESCRIPCION, "descripcion"),
                (TAG_SOFTWARE, "software"),
            ):
                valor = exif.get(tag)
                if valor not in (None, ""):
                    resultado[clave] = str(valor).strip()
    except Exception:
        pass
    return resultado


def leer_evidencia(ruta):
    """Lee la evidencia imagen -> fila de la planilla (JSON o CSV).

    JSON aceptado:
      - {"A.jpg": {<9 columnas>}, ...}
      - [{"imagen_jpg": "A.jpg", <9 columnas>}, ...]
      - {"evidencia": {A.jpg: {...}}}

    CSV (DictReader) debe tener una columna que identifique el JPG
    (imagen_jpg / jpg / imagen / nombre_archivo / render) y las columnas de
    la planilla.

    Devuelve { "<nombre_base_sin_extension>": fila, ... } donde fila tiene
    exactamente las 9 columnas del contrato. Lanza ErrorEvidencia si la
    evidencia no permite vincular imagen -> codigo.
    """
    ruta = str(ruta or "")
    if not ruta or not os.path.isfile(ruta):
        raise ErrorEvidencia("No se encontro el archivo de evidencia: {}".format(ruta))

    extension = os.path.splitext(ruta)[1].lower()
    crudas = []
    if extension in (".json",):
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
        if isinstance(datos, dict) and "evidencia" in datos:
            datos = datos["evidencia"]
        if isinstance(datos, dict):
            for clave, fila in datos.items():
                crudas.append((str(clave), _normalizar_fila(fila)))
        elif isinstance(datos, list):
            for fila in datos:
                if not isinstance(fila, dict):
                    continue
                nombre = fila.get(COLUMNA_IMAGEN) or fila.get("jpg") or fila.get("imagen")
                for clave_extra in ("nombre_archivo", "render", "archivo_imagen"):
                    if nombre is None and clave_extra in fila:
                        nombre = fila.get(clave_extra)
                if nombre is None:
                    raise ErrorEvidencia(
                        "Cada fila de evidencia debe indicar el JPG que vincula "
                        "(columna '{}').".format(COLUMNA_IMAGEN)
                    )
                crudas.append((str(nombre), _normalizar_fila(fila)))
        else:
            raise ErrorEvidencia("Evidencia JSON con estructura no soportada.")
    else:
        import csv

        with open(ruta, "r", encoding="utf-8-sig", newline="") as f:
            lector = csv.DictReader(f)
            columnas = [str(c or "").strip() for c in (lector.fieldnames or [])]
            for fila in lector:
                if not any(str(fila.get(c, "") or "").strip() for c in columnas):
                    continue
                crudas.append((_nombre_desde_csv(fila, columnas), _normalizar_fila(fila)))

    evidencia = {}
    for nombre, fila in crudas:
        if not nombre:
            continue
        base = os.path.splitext(str(nombre).strip())[0]
        evidencia[base] = fila
    return evidencia


def _nombre_desde_csv(fila, columnas):
    columnas_imagen = [COLUMNA_IMAGEN, "jpg", "imagen", "nombre_archivo", "render", "archivo_imagen"]
    for columna in columnas_imagen:
        if columna in fila and str(fila.get(columna, "") or "").strip():
            return str(fila.get(columna)).strip()
    for columna in columnas:
        texto = str(fila.get(columna, "") or "").strip()
        if columna.lower() != "codigo" and (".jpg" in texto.lower() or ".jpeg" in texto.lower()):
            return texto
    raise ErrorEvidencia(
        "La evidencia CSV no tiene una columna que identifique el JPG "
        "(se espera '{}', 'jpg', 'imagen', ...).".format(COLUMNA_IMAGEN)
    )


def _normalizar_fila(fila):
    out = {}
    for columna in COLUMNAS_PLANILLA:
        out[columna] = str(fila.get(columna, "") or "").strip()
    return out


class ErrorEvidencia(ValueError):
    """La evidencia no permite vincular un JPG con su CDR de forma verificable."""


def evaluar(jpg, evidencia=None, mapa=None):
    """Decide si un JPG se puede integrar sin inventar trazabilidad.

    Devuelve:
      verificado: {"estado","imagen","fila","registro","origen_exif"}
      pendiente : {"estado","imagen","motivo","info_faltante","origen_exif"}

    - evidencia: mapping nombre base JPG -> fila de 9 columnas (ver
      leer_evidencia). Una imagen sin evidencia queda pendiente.
    - mapa: {"entradas": {numero_carpeta: carpeta_real}, ...}; si falta o no
      resuelve la carpeta, el registro verificado se degrada a pendiente.
    """
    base = os.path.splitext(os.path.basename(jpg))[0]
    exif = origen_exif(jpg)
    prefijo = "imagen: {}".format(os.path.basename(jpg))

    fila = (evidencia or {}).get(base)
    if not fila:
        return {
            "estado": "pendiente",
            "imagen": os.path.basename(jpg),
            "motivo": "Sin evidencia que relacione este JPG con un CDR original.",
            "info_faltante": [
                "Fila de la planilla 'Control de exportacion' vinculada a este JPG "
                "con codigo, carpeta_origen y archivo_original (todas las 9 columnas).",
                "Numero de carpeta real en la hoja Listas (carpeta_origen -> carpeta).",
            ],
            "origen_exif": exif,
        }

    codigo = fila.get("codigo", "")
    if not validar_codigo(codigo):
        return {
            "estado": "pendiente",
            "imagen": os.path.basename(jpg),
            "motivo": "La evidencia no aporta un codigo SBX-NN-NNNN valido.",
            "info_faltante": [
                "Codigo SBX-NN-NNNN valido en la fila de evidencia (se recibio '{}').".format(codigo),
            ],
            "origen_exif": exif,
        }

    if not str(fila.get("carpeta_origen", "") or "").strip():
        return {
            "estado": "pendiente",
            "imagen": os.path.basename(jpg),
            "motivo": prefijo,
            "info_faltante": ["carpeta_origen vacio en la evidencia."],
            "origen_exif": exif,
        }
    if not str(fila.get("archivo_original", "") or "").strip():
        return {
            "estado": "pendiente",
            "imagen": os.path.basename(jpg),
            "motivo": prefijo,
            "info_faltante": ["archivo_original vacio en la evidencia."],
            "origen_exif": exif,
        }

    try:
        registro = enriquecer_registro(fila, mapa or {}, png=None)
    except ValueError as error:
        return {
            "estado": "pendiente",
            "imagen": os.path.basename(jpg),
            "motivo": "La evidencia esta incompleta frente al contrato.",
            "info_faltante": [str(error)],
            "origen_exif": exif,
        }

    registro["jpg"] = os.path.basename(jpg)
    registro["png"] = codigo + ".png"
    return {
        "estado": "verificado",
        "imagen": os.path.basename(jpg),
        "fila": dict(fila),
        "registro": registro,
        "origen_exif": exif,
    }


def generar_png(jpg, codigo, carpeta_destino):
    """Genera SBX-NN-NNNN.png desde el JPG (copia de trabajo).

    - Valida el codigo (nunca publica un nombre sin SBX-NN-NNNN).
    - NO borra ni modifica el JPG original.
    - NO toca ningun CDR (solo lee el JPG fuente).
    Devuelve la ruta del PNG generado.
    """
    if not validar_codigo(codigo):
        raise ValueError("No se puede publicar PNG sin codigo SBX-NN-NNNN: '{}'".format(codigo))
    if not os.path.isfile(jpg):
        raise FileNotFoundError(jpg)
    if carpeta_destino:
        os.makedirs(carpeta_destino, exist_ok=True)
    destino = os.path.join(carpeta_destino, codigo + ".png")
    with Image.open(jpg) as imagen:
        imagen.convert("RGB").save(destino, "PNG")
    if not os.path.isfile(jpg):
        raise RuntimeError("El JPG original desaparecio; abortando por seguridad.")
    return destino


def escribir_planilla(verificados, salida_csv):
    """Escribe la planilla 'Control de exportacion' (solo filas verificadas,
    exactamente las 9 columnas del contrato). Devuelve la ruta."""
    import csv

    with open(salida_csv, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS_PLANILLA)
        escritor.writeheader()
        for item in verificados:
            escritor.writerow({col: item["fila"].get(col, "") for col in COLUMNAS_PLANILLA})
    return salida_csv


def escribir_pendientes(pendientes, salida_json):
    """Registra en JSON las imagenes pendientes y que informacion les falta."""
    if pendientes:
        os.makedirs(os.path.dirname(salida_json), exist_ok=True)
    with open(salida_json, "w", encoding="utf-8") as f:
        json.dump(pendientes, f, ensure_ascii=False, indent=2)
    return salida_json


def escribir_informe(informe, salida_json):
    """Resumen del informe de integracion."""
    os.makedirs(os.path.dirname(salida_json), exist_ok=True)
    with open(salida_json, "w", encoding="utf-8") as f:
        json.dump(informe, f, ensure_ascii=False, indent=2)
    return salida_json