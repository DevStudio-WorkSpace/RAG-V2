"""
crear_plantilla_sublitex.py
---------------------------
Genera las plantillas oficiales del contrato de datos (SECCION 00):

  - data/Control de exportacion.xlsx
        hoja "Control de exportación": encabezado de 9 columnas
        hoja "Listas": encabezado  numero,carpeta
  - data/control_exportacion.csv       (mismo encabezado, sin filas)
  - data/listas.csv                    (encabezado numero,carpeta)

NO se inventan filas de datos ni carpetas reales: la planilla la completa el
equipo Sublitex; el mapa de la hoja Listas se rellena con la realidad del
Drive. El generador solo crea las estructuras vacias validas.

Uso:
    python scripts/crear_plantilla_sublitex.py
"""

import csv
import os
import sys
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from core.sublitex import COLUMNAS_PLANILLA, HOJA_LISTAS, HOJA_PRINCIPAL


def generar_planilla(salida_xlsx, planilla_csv, mapa_csv):
    from openpyxl import Workbook

    libro = Workbook()
    hoja_principal = libro.active
    hoja_principal.title = HOJA_PRINCIPAL
    hoja_principal.append(COLUMNAS_PLANILLA)
    hoja_listas = libro.create_sheet(HOJA_LISTAS)
    hoja_listas.append(["numero", "carpeta"])
    libro.save(salida_xlsx)

    with open(planilla_csv, "w", encoding="utf-8-sig", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(COLUMNAS_PLANILLA)

    with open(mapa_csv, "w", encoding="utf-8-sig", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(["numero", "carpeta"])


def main():
    salida_xlsx = os.path.join(BASE_DIR, "data", "Control de exportacion.xlsx")
    planilla_csv = os.path.join(BASE_DIR, "data", "control_exportacion.csv")
    mapa_csv = os.path.join(BASE_DIR, "data", "listas.csv")

    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    generar_planilla(salida_xlsx, planilla_csv, mapa_csv)

    print("Plantillas Sublitex generadas ({}):".format(
        datetime.now().strftime("%Y-%m-%d %H:%M")))
    print("- {}".format(salida_xlsx))
    print("    hoja '{}': {}".format(HOJA_PRINCIPAL, ", ".join(COLUMNAS_PLANILLA)))
    print("    hoja '{}': numero, carpeta".format(HOJA_LISTAS))
    print("- {}".format(planilla_csv))
    print("- {}".format(mapa_csv))
    print("\nEstructuras creadas vacias. El equipo completa las filas reales;")
    print("no se rellenan datos de ejemplo.")


if __name__ == "__main__":
    main()