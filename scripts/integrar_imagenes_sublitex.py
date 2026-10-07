#!/usr/bin/env python3
"""
Integra las imagenes legacy (JPG descriptivos de data/imagenes_normalized) al
flujo Sublitex sin inventar trazabilidad.

Para cada JPG intenta construir:

    JPG -> CDR original -> carpeta_origen -> archivo_original
          -> codigo SBX-XXXXX -> PNG publicado (SBX-XXXXX.png)

La relacion JPG -> CDR SOLO se acepta si hay EVIDENCIA (core.adaptador_imagenes):
un JSON/CSV que mapee el nombre del JPG a su fila completa de la planilla
"Control de exportacion" (codigo, carpeta_origen, archivo_original, tipo,
deporte, ocasion, estado, quien, fecha). Sin evidencia, la imagen queda
PENDIENTE y se registra exactamente que informacion falta.

El resultado integrado (PNG SBX-XXXXX.png + fila de 9 columnas) es el insumo
exacto que consume scripts/cargador_sublitex.py.

Uso:
    python scripts/integrar_imagenes_sublitex.py
        [--imagenes data/imagenes_normalized]
        [--evidencia ruta/{evidencia.json,evidencia.csv}]
        [--mapa ruta/listas.csv]
        [--salida data/integracion_sublitex]
        [--no-png]            # solo decide, no publica PNG
"""

import argparse
import json
import os
import sys

from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from core.adaptador_imagenes import (
    ErrorEvidencia,
    evaluar,
    escribir_informe,
    escribir_pendientes,
    escribir_planilla,
    generar_png,
    leer_evidencia,
)
from core.sublitex import leer_mapa

CARPETA_IMAGENES = os.path.join(BASE_DIR, "data", "imagenes_normalized")
SALIDA_POR_DEFECTO = os.path.join(BASE_DIR, "data", "integracion_sublitex")


def main():
    parser = argparse.ArgumentParser(
        description="Integra los JPG legacy al flujo Sublitex sin inventar trazabilidad."
    )
    parser.add_argument("--imagenes", type=str, default=CARPETA_IMAGENES,
                        help="Carpeta con las imagenes JPG a integrar.")
    parser.add_argument("--evidencia", type=str, default=None,
                        help="JSON/CSV que relaciona cada JPG con su fila de la planilla.")
    parser.add_argument("--mapa", type=str, default=None,
                        help="CSV mapa de la hoja Listas (numero de carpeta -> carpeta real).")
    parser.add_argument("--salida", type=str, default=SALIDA_POR_DEFECTO,
                        help="Carpeta de salida (planilla, pendientes, informe, PNG).")
    parser.add_argument("--no-png", action="store_true",
                        help="Solo decidir, no generar PNG para las imagenes verificadas.")
    args = parser.parse_args()

    if not os.path.isdir(args.imagenes):
        print("Error: No se encontro la carpeta de imagenes en {}".format(args.imagenes))
        return 1

    imagenes = sorted(
        os.path.join(args.imagenes, nombre)
        for nombre in os.listdir(args.imagenes)
        if nombre.lower().endswith((".jpg", ".jpeg"))
    )
    print("Imagenes JPG encontradas: {}".format(len(imagenes)))

    try:
        evidencia = leer_evidencia(args.evidencia) if args.evidencia else {}
    except ErrorEvidencia as error:
        print("Error de evidencia: {}".format(error))
        return 1
    print("Evidencia: {} archivo(s) vinculado(s) por nombre.".format(len(evidencia)))
    if not evidencia:
        print("Sin evidencia: ninguna imagen recibe codigo (todo quedara pendiente).")

    mapa = {}
    if args.mapa:
        try:
            mapa = leer_mapa(args.mapa)
        except ValueError as error:
            print("Error del mapa de Listas: {}".format(error))
            return 1
    print("Mapa de Listas: {} carpeta(s).".format(len(mapa.get("entradas", {}))))

    os.makedirs(args.salida, exist_ok=True)
    verificados = []
    pendientes = []
    generados = []
    sin_la_planilla_fuente = False

    for jpg in imagenes:
        resultado = evaluar(jpg, evidencia, mapa)
        if resultado["estado"] == "verificado":
            codigo = resultado["registro"]["codigo"]
            print("  OK  {} -> {} (carpeta {}, CDR {})".format(
                resultado["imagen"], codigo,
                resultado["registro"]["carpeta_origen"],
                resultado["registro"]["archivo_original"],
            ))
            if not args.no_png:
                png = generar_png(jpg, codigo, os.path.join(args.salida, "png"))
                generados.append({"jpg": resultado["imagen"], "codigo": codigo, "png": os.path.basename(png)})
            verificados.append(resultado)
        else:
            pendientes.append(resultado)
            print("  PENDIENTE {} - {}".format(resultado["imagen"], resultado["motivo"]))

    ruta_planilla = os.path.join(args.salida, "Control de exportacion.csv")
    if verificados:
        escribir_planilla(verificados, ruta_planilla)
    else:
        _planilla_vacia(ruta_planilla)
    ruta_pendientes = escribir_pendientes(pendientes, os.path.join(args.salida, "pendientes.json"))

    informe = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "imagenes_evaluadas": len(imagenes),
        "relacionadas_con_cdr": len(verificados),
        "con_codigo_sbx": len(verificados),
        "png_generados": len(generados),
        "pendientes": len(pendientes),
        "imagenes_pendientes": [p["imagen"] for p in pendientes],
        "ruta_planilla": ruta_planilla,
        "ruta_pendientes": ruta_pendientes,
        "nota": ("Ningun codigo fue asignado por orden: solo se acepta evidencia "
                 "verificable que relacione el JPG con su CDR original."),
    }
    ruta_informe = escribir_informe(informe, os.path.join(args.salida, "informe.json"))

    print("\n=== Resumen de integracion ===")
    print("Imagenes evaluadas       : {}".format(len(imagenes)))
    print("Relacionadas con CDR     : {}".format(len(verificados)))
    print("Con codigo SBX-XXXXX     : {}".format(len(verificados)))
    print("PNG publicados           : {}".format(len(generados)))
    print("Pendientes               : {}".format(len(pendientes)))
    print("Planilla (control)       : {}".format(ruta_planilla))
    print("Pendientes (detalle)     : {}".format(ruta_pendientes))
    print("Informe                  : {}".format(ruta_informe))
    return 0


def _planilla_vacia(ruta):
    import csv

    from core.sublitex import COLUMNAS_PLANILLA

    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerow(COLUMNAS_PLANILLA)


if __name__ == "__main__":
    sys.exit(main())