#!/usr/bin/env python
"""Convenient wrapper for the Sección 00 auditor (Tarea 2 A – Cruce).
It re‑uses `scripts/auditoria_seccion00.py` but writes the report to a
more explicit filename (`docs/CRUCE_YYYYMMDD.md`).
"""

import argparse
import datetime
import os
import sys
from pathlib import Path

# Import the main audit function from the existing script.
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(BASE_DIR))

# Import auditor module.
from scripts import auditoria_seccion00 as auditor

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cruce de PNG y planilla (Tarea 2 A)")
    parser.add_argument("--png_dir", type=str, default=None,
                        help="Carpeta con los PNG exportados (por defecto busca en data/)")
    parser.add_argument("--planilla", type=str, default=None,
                        help="Ruta al CSV/XLSX del Control de exportación")
    parser.add_argument("--hoja", type=str, default=auditor.HOJA_LISTAS,
                        help="Hoja del mapa de carpetas (defecto: Listas)")
    parser.add_argument("--mapa", type=str, default=None,
                        help="CSV alternativo del mapa número → carpeta")
    parser.add_argument("--salida", type=str, default=None,
                        help="Ruta del informe Markdown a generar")
    return parser.parse_args()

def main():
    args = parse_args()
    if not args.salida:
        today = datetime.datetime.now().strftime("%Y%m%d")
        args.salida = str(BASE_DIR / "docs" / f"CRUCE_{today}.md")
    # Build argv for auditor.
    argv = ["auditoria_seccion00.py"]
    if args.png_dir:
        argv += ["--png_dir", args.png_dir]
    if args.planilla:
        argv += ["--planilla", args.planilla]
    if args.hoja:
        argv += ["--hoja", args.hoja]
    if args.mapa:
        argv += ["--mapa", args.mapa]
    argv += ["--salida", args.salida]
    sys.argv = argv
    auditor.main()
    print(f"✅ Informe de cruce generado en {args.salida}")

if __name__ == "__main__":
    main()
