# -*- coding: utf-8 -*-
"""cruce.py

Cross‑check utility for the Sublitex export control.

- Detects codes in the control sheet that lack a PNG file.
- Detects PNG files that are not present in the control sheet.
- Finds duplicate codes in the sheet.
- Reports missing sequential numbers per folder (e.g. SBX‑03‑0001 …).
- Flags rows with empty `carpeta_origen` or `archivo_original`.
- Flags rows where the folder prefix (second component of the code) does not match
  the `carpeta_origen` column.

The script reads the control sheet (Excel or CSV) from ``data/Control de exportacion.xlsx``
or ``data/control_exportacion.csv`` and scans the PNG directory
``data/demo_sublitex/png_publicados``.

A CSV report ``data/report_cruce.csv`` is written with the findings.
"""

import pathlib
import pandas as pd
import csv
from collections import Counter

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_ROOT = pathlib.Path(__file__).resolve().parents[1] / "data"
PLANILLA_XLSX = DATA_ROOT / "Control de exportacion.xlsx"
PLANILLA_CSV = DATA_ROOT / "control_exportacion.csv"
PNG_DIR = DATA_ROOT / "demo_sublitex" / "png_publicados"
REPORT_CSV = DATA_ROOT / "report_cruce.csv"

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def load_planilla():
    """Load the control sheet.

    Preference is given to the Excel version if it exists; otherwise the CSV
    placeholder is used.
    """
    if PLANILLA_XLSX.exists():
        df = pd.read_excel(PLANILLA_XLSX, dtype=str)
    elif PLANILLA_CSV.exists():
        df = pd.read_csv(PLANILLA_CSV, dtype=str)
    else:
        raise FileNotFoundError("No control sheet found in the data folder.")
    # Normalise column names (strip whitespace, lower case)
    df.columns = [c.strip().lower() for c in df.columns]
    return df

def list_png_codes():
    """Return a set of codes derived from PNG filenames.

    Expected filename pattern: ``SBX-XX-NNNN.png`` where the code is the part
    before the extension.
    """
    png_files = PNG_DIR.glob("*.png")
    return {p.stem for p in png_files}

def missing_png(df, png_codes):
    return df[~df["codigo"].isin(png_codes)]["codigo"].tolist()

def png_without_row(png_codes, df):
    return [code for code in png_codes if code not in set(df["codigo"])]

def duplicate_codes(df):
    cnt = Counter(df["codigo"].dropna())
    return [code for code, c in cnt.items() if c > 1]

def missing_sequential_numbers(df):
    """Detect gaps in the numeric part per folder.

    Returns a dict ``{folder_prefix: [missing_numbers]}`` where missing numbers
    are formatted as zero‑padded four‑digit strings.
    """
    missing = {}
    # Keep only rows with a well‑formed code like SBX-03-0012
    df_valid = df.dropna(subset=["codigo"]).copy()
    # Extract prefix, folder and numeric part using regex capture groups
    extracted = df_valid["codigo"].str.extract(r"^([A-Z]+)-(\d{2})-(\d{4})$")
    extracted.columns = ["_pref", "_folder", "_num"]
    df_valid = pd.concat([df_valid, extracted], axis=1)
    # Ensure numeric part is integer
    df_valid["_num"] = df_valid["_num"].astype(int)
    for folder, group in df_valid.groupby("_folder"):
        numbers = group["_num"].astype(int)
        if numbers.empty:
            continue
        full_range = set(range(numbers.min(), numbers.max() + 1))
        missing_nums = sorted(full_range - set(numbers))
        if missing_nums:
            missing[folder] = [f"{n:04d}" for n in missing_nums]
    return missing

def rows_with_blank_fields(df):
    blank_mask = (
        df["carpeta_origen"].isna()
        | (df["carpeta_origen"].str.strip() == "")
        | df["archivo_original"].isna()
        | (df["archivo_original"].str.strip() == "")
    )
    return df[blank_mask]["codigo"].tolist()

def mismatched_prefix(df):
    # Keep rows with both a code and a folder origin
    df = df.dropna(subset=["codigo", "carpeta_origen"]).copy()
    # Extract the folder component (second part) from codes like SBX-03-0012
    extracted = df["codigo"].str.extract(r"^[A-Z]+-(\d{2})-\d{4}$")
    extracted.columns = ["_folder"]
    df = pd.concat([df, extracted], axis=1)
    # Compare extracted folder with carpeta_origen (zero‑padded to 2 digits)
    mismatched = df[df["_folder"] != df["carpeta_origen"].str.zfill(2)]
    return mismatched["codigo"].tolist()

# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------
def main():
    df = load_planilla()
    png_codes = list_png_codes()

    report = {
        "missing_png": missing_png(df, png_codes),
        "png_without_row": png_without_row(png_codes, df),
        "duplicate_codes": duplicate_codes(df),
        "missing_sequential": missing_sequential_numbers(df),
        "blank_fields": rows_with_blank_fields(df),
        "prefix_mismatch": mismatched_prefix(df),
    }

    # Write a simple CSV where each section is a separate block.
    with open(REPORT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for key, value in report.items():
            writer.writerow([key.upper()])
            if isinstance(value, dict):
                for folder, miss in value.items():
                    writer.writerow([folder, ", ".join(miss)])
            else:
                for item in value:
                    writer.writerow([item])
            writer.writerow([])  # blank line between sections
    print(f"Report written to {REPORT_CSV}")

if __name__ == "__main__":
    main()
