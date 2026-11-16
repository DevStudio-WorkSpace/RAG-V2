"""Valida datos comerciales y referencias de imagen del catálogo."""

import csv
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "products.csv"
IMAGES_DIR = ROOT / "data" / "images_normalized"
REQUIRED_COLUMNS = {"id", "imagen", "nombre_original", "url"}


def main() -> int:
    if not CSV_PATH.is_file():
        print(f"ERROR: no existe el catálogo: {CSV_PATH}")
        return 2
    if not IMAGES_DIR.is_dir():
        print(f"ERROR: no existe el directorio de imágenes: {IMAGES_DIR}")
        return 2

    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as catalog_file:
        reader = csv.DictReader(catalog_file)
        columns = set(reader.fieldnames or ())
        missing_columns = sorted(REQUIRED_COLUMNS - columns)
        if missing_columns:
            print(f"ERROR: faltan columnas requeridas: {', '.join(missing_columns)}")
            return 2

        rows = list(reader)

    url_issues: list[tuple[int, str, str]] = []
    name_issues: list[tuple[int, str]] = []
    missing_images: list[tuple[int, str, str]] = []
    ids_by_row: list[tuple[int, str]] = []

    for row_number, row in enumerate(rows, start=2):
        product_id = (row["id"] or "").strip()
        image_name = (row["imagen"] or "").strip()
        commercial_name = (row["nombre_original"] or "").strip()
        url = (row["url"] or "").strip()
        ids_by_row.append((row_number, product_id))

        if not url or "ejemplo.com" in url.casefold():
            url_issues.append((row_number, product_id, url))
        if product_id and commercial_name == product_id:
            name_issues.append((row_number, product_id))

        image_exists = False
        if image_name:
            image_path = (IMAGES_DIR / image_name).resolve()
            try:
                image_path.relative_to(IMAGES_DIR.resolve())
            except ValueError:
                pass
            else:
                image_exists = image_path.is_file()
        if not image_exists:
            missing_images.append((row_number, product_id, image_name))

    id_counts = Counter(product_id for _, product_id in ids_by_row if product_id)
    duplicates = {
        product_id
        for product_id, count in id_counts.items()
        if count > 1
    }
    duplicate_rows = [
        (row_number, product_id)
        for row_number, product_id in ids_by_row
        if product_id in duplicates
    ]

    for row_number, product_id, url in url_issues:
        print(f"URL inválida/vacía: fila {row_number}, id={product_id!r}, url={url!r}")
    for row_number, product_id in name_issues:
        print(f"Nombre igual al ID: fila {row_number}, id={product_id!r}")
    for row_number, product_id, image_name in missing_images:
        print(
            f"Imagen inexistente: fila {row_number}, "
            f"id={product_id!r}, imagen={image_name!r}"
        )
    for row_number, product_id in duplicate_rows:
        print(f"ID duplicado: fila {row_number}, id={product_id!r}")

    issue_count = (
        len(url_issues)
        + len(name_issues)
        + len(missing_images)
        + len(duplicates)
    )
    print(
        "Resumen: "
        f"registros={len(rows)}, "
        f"URLs_inválidas_o_vacías={len(url_issues)}, "
        f"nombres_iguales_al_ID={len(name_issues)}, "
        f"imágenes_inexistentes={len(missing_images)}, "
        f"IDs_duplicados={len(duplicates)}"
    )
    return 1 if issue_count else 0


if __name__ == "__main__":
    sys.exit(main())
