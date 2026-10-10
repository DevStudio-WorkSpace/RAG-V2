#!/usr/bin/env python
"""Hoja de contactos (Task 2 B)
Genera una cuadrícula de 20 imágenes PNG aleatorias del día anterior,
valida ancho, fondo blanco y firma PNG, y marca en rojo las que no cumplen.
Guarda la cuadrícula como `docs/hoja_contactos_YYYYMMDD.png`.
"""

import argparse
import datetime
import os
import random
import sys
from pathlib import Path

from PIL import Image, ImageStat
import matplotlib.pyplot as plt

# PNG signature (first 8 bytes)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

def is_real_png(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(8) == PNG_SIGNATURE
    except OSError:
        return False

def has_white_background(img: Image.Image, threshold: float = 250) -> bool:
    # Convert to RGB and compute average brightness of the border pixels.
    if img.mode != "RGB":
        img = img.convert("RGB")
    # Sample a 5‑pixel wide border.
    top = img.crop((0, 0, img.width, 5))
    bottom = img.crop((0, img.height - 5, img.width, img.height))
    left = img.crop((0, 5, 5, img.height - 5))
    right = img.crop((img.width - 5, 5, img.width, img.height - 5))
    border = Image.new("RGB", (img.width, img.height))
    # Not actually needed to combine; we can compute stats directly.
    stat = ImageStat.Stat([top, bottom, left, right])
    avg = sum(stat.mean) / 3
    return avg >= threshold

def valid_image(path: Path) -> bool:
    if path.suffix.lower() != ".png":
        return False
    if not is_real_png(path):
        return False
    try:
        img = Image.open(path)
        if img.width < 2000:
            return False
        if not has_white_background(img):
            return False
        return True
    except Exception:
        return False

def select_images(png_dir: Path, count: int = 20) -> list[Path]:
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    start_ts = datetime.datetime(yesterday.year, yesterday.month, yesterday.day)
    end_ts = start_ts + datetime.timedelta(days=1)
    candidates = []
    for p in png_dir.iterdir():
        if p.is_file() and p.suffix.lower() == ".png":
            mtime = datetime.datetime.fromtimestamp(p.stat().st_mtime)
            if start_ts <= mtime < end_ts:
                candidates.append(p)
    return random.sample(candidates, min(count, len(candidates)))

def extract_code(filename: str) -> str:
    return Path(filename).stem

def draw_grid(images: list[Path], output_path: Path):
    cols, rows = 5, 4
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3))
    axes = axes.flatten()
    for ax, img_path in zip(axes, images):
        img = Image.open(img_path)
        ax.imshow(img)
        code = extract_code(img_path.name)
        ok = valid_image(img_path)
        color = "black" if ok else "red"
        ax.set_title(code, color=color, fontsize=8)
        ax.axis('off')
    for ax in axes[len(images):]:
        ax.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Genera hoja de contactos (Task 2 B)")
    parser.add_argument("--png_dir", type=str, required=True,
                        help="Carpeta donde buscar PNGs exportados")
    parser.add_argument("--output", type=str, default=None,
                        help="Archivo de salida (PNG). Por defecto en docs/hoja_contactos_YYYYMMDD.png")
    args = parser.parse_args()
    png_dir = Path(args.png_dir)
    if not png_dir.is_dir():
        sys.exit(f"Error: {png_dir} no es una carpeta válida")
    selected = select_images(png_dir)
    if not selected:
        sys.exit("No se encontraron PNG del día anterior.")
    today = datetime.datetime.now().strftime("%Y%m%d")
    output_path = Path(args.output) if args.output else Path.cwd() / "docs" / f"hoja_contactos_{today}.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    draw_grid(selected, output_path)
    print(f"✅ Hoja de contactos guardada en {output_path}")

if __name__ == "__main__":
    main()
