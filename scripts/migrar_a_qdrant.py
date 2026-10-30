# -*- coding: utf-8 -*-
"""
scripts/migrar_a_qdrant.py
--------------------------
Migra los embeddings existentes (.npy) y los metadatos de products.csv a Qdrant.

Este script lee:
  - data/products.csv        (metadatos de productos: id, nombre, url, proveedor, imagen)
  - data/embeddings.npy      (embeddings CLIP, N x 512)
  - data/ids.npy             (IDs alineados con los embeddings)

Y los sube a la colección de Qdrant configurada en .env (default: sublitex_fashion_v1).

Uso:
    python scripts/migrar_a_qdrant.py
    python scripts/migrar_a_qdrant.py --coleccion camisetas_fashion_v3
    python scripts/migrar_a_qdrant.py --recrear  (elimina la colección y la crea de nuevo)
"""

import argparse
import os
import sys

import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from api.qdrant_engine import indexar_productos_desde_csv
from core.config import settings


def main():
    parser = argparse.ArgumentParser(description="Migrar embeddings a Qdrant")
    parser.add_argument(
        "--coleccion",
        type=str,
        default=None,
        help="Nombre de la colección Qdrant (default: settings.QDRANT_COLLECTION_NAME)",
    )
    parser.add_argument(
        "--recrear",
        action="store_true",
        help="Eliminar la colección existente antes de indexar",
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Ruta al CSV de productos (default: data/products.csv)",
    )
    parser.add_argument(
        "--embeddings",
        type=str,
        default=None,
        help="Ruta al archivo .npy de embeddings (default: data/embeddings.npy)",
    )
    args = parser.parse_args()

    # Sobrescribir la colección si se indica por línea de comandos
    if args.coleccion:
        settings.QDRANT_COLLECTION_NAME = args.coleccion
        print(f"Usando colección: {args.coleccion}")

    csv_path = args.csv or os.path.join(BASE_DIR, "data", "products.csv")
    emb_path = args.embeddings or os.path.join(BASE_DIR, "data", "embeddings.npy")

    print("=" * 60)
    print("MIGRACIÓN DE EMBEDDINGS A QDRANT")
    print("=" * 60)
    print(f"CSV       : {csv_path}")
    print(f"Embeddings: {emb_path}")
    print(f"Colección : {settings.QDRANT_COLLECTION_NAME}")
    print("=" * 60)

    if not os.path.exists(csv_path):
        print(f"ERROR: No se encontró {csv_path}")
        print("Primero ejecute scripts/generar_embeddings.py o confirme que existe el CSV.")
        sys.exit(1)

    if not os.path.exists(emb_path):
        print(f"ERROR: No se encontró {emb_path}")
        print("Primero ejecute scripts/generar_embeddings.py para generar embeddings.")
        sys.exit(1)

    if args.recrear:
        from core.qdrant_service import QdrantService
        qs = QdrantService(collection_name=settings.QDRANT_COLLECTION_NAME)
        qs.vaciar_coleccion()
        print(f"Colección '{settings.QDRANT_COLLECTION_NAME}' recreada.")

    try:
        total = indexar_productos_desde_csv(
            csv_path=csv_path,
            embeddings_path=emb_path,
        )
        print("=" * 60)
        print(f"MIGRACIÓN COMPLETADA: {total} productos indexados en Qdrant")
        print(f"Colección: {settings.QDRANT_COLLECTION_NAME}")
        print("=" * 60)
    except Exception as e:
        print(f"ERROR durante la migración: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
