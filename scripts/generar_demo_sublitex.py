#!/usr/bin/env python3
"""
generar_demo_sublitex.py  -  SECCION 00 / Tarea 1 · Conjunto DEMO reproducibile
--------------------------------------------------------------------------------
Construye el set de DEMOSTRACION de 40 diseños usando EXACTAMENTE las imagenes
que ya estan en el proyecto (data/imagenes_normalized/, 44 JPG) y deja listo el
insumo del cargador:

    data/demo_sublitex/
    ├── asignacion_demo.json                 # codigo -> jpg + archivo_original (DEMO)
    ├── extras_excluidos.json                # 4 JPG no usados + motivo (DEMO)
    ├── cdr_real/Demostracion/03/<archivo>.cdr
    ├── png_publicados/SBX-03-0001.png ...   # PNG real convertido desde el JPG
    ├── planilla/Control de exportacion.xlsx # 9 columnas + hoja Listas
    └── planilla/control_exportacion.csv     # version CSV (mismo contenido)
        planilla/listas.csv                  # mapa numero -> carpeta real (demo)

REGLAS (todas DEMO_GENERADO, nunca presentadas como datos reales del Drive):
  1. De los 44 JPG existentes se usan 40; 4 quedan EXCLUIDOS con su motivo y
     se documentan (presuntos duplicados del mismo kit).
  2. Codigos: carpeta demo 03, correlativo SBX-03-0001..SBX-03-0040 asignado
     por orden alfabetico de nombre (regla reproducible, NO evidencia real).
  3. archivo_original = nombre del JPG sanitizado + ".cdr" (DEMO).
  4. Los CDR de demostracion se CREAN con contenido que los marca DEMO.
  5. El JPG original NO se borra ni se modifica. El PNG se genera por
     conversion real (jamás renombrado con extension cambiada).

Uso:
    python scripts/generar_demo_sublitex.py [--force]
"""

import argparse
import json
import os
import re
import shutil
import sys
import unicodedata
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from core.adaptador_imagenes import generar_png  # reutiliza la conversion real
from core.sublitex import COLUMNAS_PLANILLA, generar_codigo

ORIGEN_JPG = os.path.join(BASE_DIR, "data", "imagenes_normalized")
SALIDA = os.path.join(BASE_DIR, "data", "demo_sublitex")
CARPETA_DEMO = "03"
CDR_ROOT = os.path.join(SALIDA, "cdr_real", "Demostracion")

# DEMO: presuntos duplicados del mismo kit (motivo de exclusion, dato generado).
EXCLUIDOS_PRESUNTOS = [
    "Qatar Home Kit 26.jpg",
    "ESPAÑA HOME.jpg",
    "Inglaterra World Cup 26.jpg",
    "Colombia Amarillo 2026.jpg",
]


def sanitizar(nombre):
    """nombre_jpg -> nombre ASCII reproducible para archivo_original."""
    normalizado = unicodedata.normalize("NFKD", nombre)
    normalizado = "".join(c for c in normalizado if not unicodedata.combining(c))
    base = os.path.splitext(normalizado)[0]
    base = re.sub(r"[^A-Za-z0-9]+", "_", base).strip("_")
    return base + ".cdr"


def _columnas_demo(codigo, jpg, fecha):
    return {
        "codigo": codigo,
        "carpeta_origen": CARPETA_DEMO,
        "archivo_original": sanitizar(jpg),
        "tipo": "cdr",
        "deporte": "futbol",
        "ocasion": "demostracion",
        "estado": "DEMO_GENERADO",
        "quien": "DEMO (Tarea 1)",
        "fecha": fecha,
    }


def main():
    parser = argparse.ArgumentParser(description="Genera el conjunto DEMO de 40 disenos para Sublitex.")
    parser.add_argument("--force", action="store_true", help="Recrea todo aunque ya exista.")
    args = parser.parse_args()

    todos = sorted(os.listdir(ORIGEN_JPG))
    jpgs = [n for n in todos if n.lower().endswith((".jpg", ".jpeg"))]
    excluidos = [n for n in EXCLUIDOS_PRESUNTOS if n in jpgs]
    seleccion = [n for n in sorted(jpgs, key=str.lower) if n not in excluidos]

    if len(jpgs) != 44:
        print("AVISO: la carpeta de imagenes tiene {} JPG (se esperaba 44).".format(len(jpgs)))
    if len(seleccion) != 40:
        print("ERROR: con la regla actual quedan {} seleccionados (esperado 40).".format(len(seleccion)))
        return 1
    faltantes = [n for n in EXCLUIDOS_PRESUNTOS if n not in jpgs]
    if faltantes:
        print("ERROR: los excluidos presuntos no estan en la carpeta: {}".format(faltantes))
        return 1

    fecha = datetime.now().date().isoformat()
    filas = []
    asignacion = {}
    png_dir = os.path.join(SALIDA, "png_publicados")
    cdr_carpeta = os.path.join(CDR_ROOT, CARPETA_DEMO)

    for indice, jpg in enumerate(seleccion, start=1):
        codigo = generar_codigo(int(CARPETA_DEMO), indice)
        fila = _columnas_demo(codigo, jpg, fecha)
        filas.append(fila)
        asignacion[codigo] = {
            "imagen_jpg": jpg,
            "archivo_original": fila["archivo_original"],
            "origen": "DEMO_GENERADO (orden alfabetico, sin evidencia real del Drive)",
        }

        archivo_original = fila["archivo_original"]
        cdr_demo = os.path.join(cdr_carpeta, archivo_original)
        if not os.path.exists(cdr_demo):
            os.makedirs(cdr_carpeta, exist_ok=True)
            with open(cdr_demo, "wb") as f:
                f.write((
                    "DEMO_GENERADO\nEste archivo .cdr es una FIXTURE de demostracion; no es el "
                    "CDR real del Drive. Su proposito es permitir probar la cadena de trazabilidad "
                    "y la politica CDR SOLO LECTURA.\nOrigen del codigo: {}\n".format(codigo)
                ).encode("utf-8"))

        png = os.path.join(png_dir, codigo + ".png")
        if not os.path.exists(png) or args.force:
            generar_png(os.path.join(ORIGEN_JPG, jpg), codigo, png_dir)

    # ---- Planilla XLSX (9 columnas + hoja Listas) ----
    os.makedirs(os.path.join(SALIDA, "planilla"), exist_ok=True)
    carpeta_real_demo = os.path.abspath(cdr_carpeta)
    _escribir_xlsx(filas, carpeta_real_demo)
    _escribir_csv(filas, carpeta_real_demo)

    with open(os.path.join(SALIDA, "asignacion_demo.json"), "w", encoding="utf-8") as f:
        json.dump({
            "nota": "DEMO_GENERADO: codigos, carpetas, archivos y CDR son sinteticos y "
                    "reproducibles; no representan datos reales del Drive de Sublitex.",
            "n_imagenes": len(seleccion),
            "carpeta_demo": CARPETA_DEMO + " -> " + carpeta_real_demo,
            "asignacion": asignacion,
        }, f, ensure_ascii=False, indent=2)

    with open(os.path.join(SALIDA, "extras_excluidos.json"), "w", encoding="utf-8") as f:
        json.dump({
            "nota": "DEMO_GENERADO: la Tarea 1 habla de 40 imagenes; la carpeta tiene 44 JPG. "
                    "Estas 4 se excluyeron por presunto duplicado del mismo kit (regla reproducible).",
            "excluidos": [{"archivo": n, "motivo": "DEMO: presunto duplicado"} for n in excluidos],
            "restantes_en_carpeta": [n for n in sorted(jpgs, key=str.lower) if n in excluidos],
        }, f, ensure_ascii=False, indent=2)

    pngs = sorted(n for n in os.listdir(png_dir) if n.lower().endswith(".png")) if os.path.isdir(png_dir) else []
    cdrs = sorted(n for n in os.listdir(cdr_carpeta) if n.lower().endswith(".cdr")) if os.path.isdir(cdr_carpeta) else []

    print("JPG en la carpeta origen : {}".format(len(jpgs)))
    print("Seleccionados (40)       : {}".format(len(seleccion)))
    print("Extras excluidos (4)     : {}".format(", ".join(excluidos)))
    print("Codigos generados        : {} (carpeta demo {})".format(len(asignacion), CARPETA_DEMO))
    print("PNG publicados           : {}".format(len(pngs)))
    print("CDR de demostracion      : {} ({})".format(len(cdrs), cdr_carpeta))
    print("Planilla XLSX/CSV        : {}".format(os.path.join(SALIDA, "planilla")))
    return 0


def _escribir_xlsx(filas, carpeta_real_demo):
    from openpyxl import Workbook

    ruta = os.path.join(SALIDA, "planilla", "Control de exportacion.xlsx")
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Control de exportación"
    hoja.append(COLUMNAS_PLANILLA)
    for fila in filas:
        hoja.append([fila.get(c, "") for c in COLUMNAS_PLANILLA])
    listas = libro.create_sheet("Listas")
    listas.append(["numero", "carpeta"])
    listas.append([CARPETA_DEMO, carpeta_real_demo])
    libro.save(ruta)
    return ruta


def _escribir_csv(filas, carpeta_real_demo):
    import csv

    ruta = os.path.join(SALIDA, "planilla", "control_exportacion.csv")
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNAS_PLANILLA)
        writer.writeheader()
        writer.writerows(filas)
    ruta_listas = os.path.join(SALIDA, "planilla", "listas.csv")
    with open(ruta_listas, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["numero", "carpeta"])
        writer.writerow([CARPETA_DEMO, carpeta_real_demo])
    return ruta


if __name__ == "__main__":
    sys.exit(main())