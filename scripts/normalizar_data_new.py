# -*- coding: utf-8 -*-
"""
normalizar_data_new.py
----------------------
Copia las imágenes de data/DATA_NEW a data/images_normalized/
conservando el formato PNG nativo de las descargas (sin recomponer).

Las imágenes originales en DATA_NEW NO se modifican.

Uso:
    python scripts/normalizar_data_new.py
"""

import os
import re
import shutil

from PIL import Image

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_NEW = os.path.join(BASE_DIR, "data", "DATA_NEW")
IMAGES_NORM = os.path.join(BASE_DIR, "data", "images_normalized")

PATRON = re.compile(r"^(SBX-\d{2}-\d{4})\.png$")


def main():
    if not os.path.isdir(DATA_NEW):
        print(f"ERROR: No existe la carpeta {DATA_NEW}")
        return

    os.makedirs(IMAGES_NORM, exist_ok=True)

    archivos = sorted(os.listdir(DATA_NEW))
    copiadas = 0
    omitidos = []
    errores = []

    for archivo in archivos:
        m = PATRON.match(archivo)
        if not m:
            omitidos.append(archivo)
            continue

        id_base = m.group(1)
        ruta_origen = os.path.join(DATA_NEW, archivo)
        ruta_destino = os.path.join(IMAGES_NORM, id_base + ".png")

        try:
            img = Image.open(ruta_origen).convert("RGB")
            img.save(ruta_destino, "PNG")
            copiadas += 1
        except Exception as e:
            errores.append((archivo, str(e)))

    print(f"Normalizadas: {copiadas} imágenes en {IMAGES_NORM}")
    if omitidos:
        print(f"Omitidos (no cumplen nomenclatura): {len(omitidos)}")
        for a in omitidos:
            print(f"  - {a}")
    if errores:
        print(f"Errores: {len(errores)}")
        for a, e in errores:
            print(f"  - {a}: {e}")


if __name__ == "__main__":
    main()
