# -*- coding: utf-8 -*-
"""
crear_csv_data_new.py
---------------------
Genera data/products.csv a partir de las imágenes en data/DATA_NEW.

Nomenclatura esperada: SBX-###-NNNN.png (ej: SBX-01-0001.png)
El ID del producto es el nombre del archivo sin extensión.

Uso:
    python scripts/crear_csv_data_new.py
"""

import csv
import os
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_NEW = os.path.join(BASE_DIR, "data", "DATA_NEW")
CSV_PATH = os.path.join(BASE_DIR, "data", "products.csv")

# Patrón: SBX-01-0001.png -> id = "SBX-01-0001"
PATRON = re.compile(r"^(SBX-\d{2}-\d{4})\.png$")


def main():
    if not os.path.isdir(DATA_NEW):
        print(f"ERROR: No existe la carpeta {DATA_NEW}")
        return

    archivos = sorted(os.listdir(DATA_NEW))
    filas = []
    omitidos = []

    for archivo in archivos:
        m = PATRON.match(archivo)
        if not m:
            omitidos.append(archivo)
            continue

        producto_id = m.group(1)
        filas.append({
            "id": producto_id,
            "proveedor": "SBX",
            "pagina": "1",
            "imagen": archivo,
            "nombre_original": producto_id,
            "url": f"https://ejemplo.com/{producto_id}",
        })

    # Verificar IDs duplicados
    ids = [f["id"] for f in filas]
    duplicados = [x for x in ids if ids.count(x) > 1]
    if duplicados:
        print(f"ERROR: IDs duplicados: {set(duplicados)}")
        return

    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "proveedor", "pagina", "imagen", "nombre_original", "url"],
        )
        writer.writeheader()
        writer.writerows(filas)

    print(f"CSV creado: {CSV_PATH}")
    print(f"Productos: {len(filas)}")
    if omitidos:
        print(f"Omitidos (no cumplen nomenclatura): {len(omitidos)}")
        for a in omitidos:
            print(f"  - {a}")


if __name__ == "__main__":
    main()
