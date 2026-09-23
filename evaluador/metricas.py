# -*- coding: utf-8 -*-
import csv
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CSV = BASE_DIR / "resultados_set_original.csv"


def cargar_resultados(ruta_csv: str | Path) -> list[dict]:
    """Lee el CSV de resultados y devuelve una lista de dicts."""
    ruta = Path(ruta_csv)
    if not ruta.exists():
        print(f"Error: No existe el archivo {ruta}")
        print("Aun no hay resultados guardados. Evalua algunos casos primero.")
        sys.exit(1)
    with open(ruta, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def calcular_metricas(resultados: list[dict], casos_csv: str | Path | None = None) -> dict:
    """
    Calcula las tres metricas principales a partir de los juicios.

    Parametros:
        resultados: lista de dicts con columnas de resultados.csv
        casos_csv: ruta a casos/casos.csv (para obtener el tipo de cada caso)

    Devuelve:
        dict con top1, top5, utilidad y desglose por tipo.
    """
    if not resultados:
        return {
            "total_casos_evaluados": 0,
            "top1": 0.0,
            "top5": 0.0,
            "utilidad": 0.0,
            "por_tipo": {},
        }

    # Cargar tipos desde casos.csv si se proporciona
    tipos_map: dict[str, str] = {}
    if casos_csv:
        ruta_casos = Path(casos_csv)
        if ruta_casos.exists():
            with open(ruta_casos, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tipos_map[row["caso"]] = row.get("tipo", "desconocido")

    # Agrupar juicios por caso
    casos_map: dict[str, list[dict]] = {}
    for r in resultados:
        caso_id = r.get("caso", "")
        if caso_id not in casos_map:
            casos_map[caso_id] = []
        casos_map[caso_id].append(r)

    total_casos = len(casos_map)
    casos_top1 = 0
    casos_top5 = 0
    suma_utilidad = 0.0

    tipo_stats: dict[str, dict] = {}

    for caso_id, juicios in casos_map.items():
        tipo = tipos_map.get(caso_id, "desconocido")

        # Top 1: posicion 1 con "Acierto"
        pos1 = [j for j in juicios if j.get("posicion") == "1"]
        hit_top1 = pos1 and pos1[0].get("juicio") == "Acierto"
        if hit_top1:
            casos_top1 += 1

        # Top 5: algun "Acierto" en posiciones 1-5
        hit_top5 = any(
            j.get("juicio") == "Acierto"
            and j.get("posicion") in ("1", "2", "3", "4", "5")
            for j in juicios
        )
        if hit_top5:
            casos_top5 += 1

        # Utilidad: cuantos de los 5 recibieron "Acierto" o "Sirve"
        utiles = sum(
            1 for j in juicios
            if j.get("juicio") in ("Acierto", "Sirve")
            and j.get("posicion") in ("1", "2", "3", "4", "5")
        )
        suma_utilidad += utiles

        # Acumular por tipo
        if tipo not in tipo_stats:
            tipo_stats[tipo] = {"total": 0, "top1": 0, "top5": 0, "suma_utilidad": 0.0}
        tipo_stats[tipo]["total"] += 1
        if hit_top1:
            tipo_stats[tipo]["top1"] += 1
        if hit_top5:
            tipo_stats[tipo]["top5"] += 1
        tipo_stats[tipo]["suma_utilidad"] += utiles

    # Calcular porcentajes por tipo
    por_tipo = {}
    for tipo, stats in tipo_stats.items():
        n = stats["total"]
        por_tipo[tipo] = {
            "total": n,
            "top1": round(100 * stats["top1"] / n, 1) if n else 0.0,
            "top5": round(100 * stats["top5"] / n, 1) if n else 0.0,
            "utilidad": round(stats["suma_utilidad"] / n, 2) if n else 0.0,
        }

    return {
        "total_casos_evaluados": total_casos,
        "top1": round(100 * casos_top1 / total_casos, 1) if total_casos else 0.0,
        "top5": round(100 * casos_top5 / total_casos, 1) if total_casos else 0.0,
        "utilidad": round(suma_utilidad / total_casos, 2) if total_casos else 0.0,
        "por_tipo": por_tipo,
    }


def imprimir_reporte(metricas: dict):
    """Imprime el reporte de metricas en la terminal."""
    print("=" * 60)
    print("REPORTE DE METRICAS — EVALUADOR (Ficha 03-A)")
    print("=" * 60)
    print()
    print(f"Total de casos evaluados: {metricas['total_casos_evaluados']}")
    print()
    print("Metricas globales:")
    print(f"  Top 1:    {metricas['top1']}%")
    print(f"  Top 5:    {metricas['top5']}%")
    print(f"  Utilidad: {metricas['utilidad']} / 5.00")
    print()

    por_tipo = metricas.get("por_tipo", {})
    if por_tipo:
        print("Desglose por tipo de foto:")
        print(f"  {'Tipo':<15} {'n':>4} {'Top 1':>8} {'Top 5':>8} {'Utilidad':>10}")
        print(f"  {'-'*15} {'-'*4} {'-'*8} {'-'*8} {'-'*10}")
        for tipo, stats in sorted(por_tipo.items()):
            print(
                f"  {tipo:<15} {stats['total']:>4} "
                f"{stats['top1']:>7.1f}% {stats['top5']:>7.1f}% "
                f"{stats['utilidad']:>9.2f}"
            )
    print()
    print("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Calcula metricas del Evaluador (Ficha 03-A)"
    )
    parser.add_argument(
        "--csv",
        default=str(DEFAULT_CSV),
        help="Ruta a resultados_set_original.csv (default: evaluador/resultados_set_original.csv)",
    )
    parser.add_argument(
        "--casos",
        default=str(BASE_DIR / "casos_set_original.csv"),
        help="Ruta a casos_set_original.csv (default: evaluador/casos_set_original.csv)",
    )
    args = parser.parse_args()

    resultados = cargar_resultados(args.csv)
    metricas = calcular_metricas(resultados, casos_csv=args.casos)
    imprimir_reporte(metricas)


if __name__ == "__main__":
    main()
