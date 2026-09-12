# -*- coding: utf-8 -*-
"""
calcular.py (Grupo A - El evaluador del buscador)
--------------------------------------------------
Lee evaluador/resultados.csv (generado en tiempo real por la interfaz de
evaluacion) y calcula las 3 metricas pedidas, en total y por tipo de foto:

    - Top 1    (%): casos donde la posicion 1 fue "Acierto".
    - Top 5    (%): casos donde al menos un resultado del top 5 fue "Acierto".
    - Utilidad (0-5): promedio por caso de resultados "Acierto" o "Sirve".

El corte por tipo usa la tabla evaluador/casos.csv (caso -> tipo), con tipos
persona, producto, captura o dificil. Los casos que no estan en casos.csv se
agrupan como "desconocido".

Regla de deduplicacion: si un (caso, posicion) se califico varias veces, se usa
el ultimo juicio registrado. Un caso cuenta como evaluado si tiene al menos un
veredicto guardado.

Uso (desde la raiz del repositorio):
    python evaluador/calcular.py

Salida en consola y en evaluador/metricas.txt
"""

import os
import unicodedata

import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVALUADOR_DIR = os.path.join(BASE_DIR, "evaluador")
RESULTADOS_CSV = os.path.join(EVALUADOR_DIR, "resultados.csv")
CASOS_CSV = os.path.join(EVALUADOR_DIR, "casos.csv")
SALIDA_TXT = os.path.join(EVALUADOR_DIR, "metricas.txt")

JUICIOS_VALIDOS = {"acierto", "sirve", "no_sirve"}
JUICIOS_UTILES = {"acierto", "sirve"}
POSICIONES = [1, 2, 3, 4, 5]
ORDEN_TIPOS = ["persona", "producto", "captura", "dificil", "desconocido"]


def _normalizar_tipo(tipo) -> str:
    """Unifica tipos con/sin acentos y espacios: 'Difícil' -> 'dificil'."""
    tipo = unicodedata.normalize("NFKD", str(tipo).strip().lower())
    tipo = "".join(c for c in tipo if not unicodedata.combining(c))
    return tipo.replace(" ", "_") or "desconocido"


def _leer_resultados() -> pd.DataFrame:
    if not os.path.isfile(RESULTADOS_CSV) or os.path.getsize(RESULTADOS_CSV) == 0:
        return pd.DataFrame()
    df = pd.read_csv(RESULTADOS_CSV, encoding="utf-8", dtype=str)
    for col in ("caso", "posicion", "juicio", "fecha"):
        if col not in df.columns:
            df[col] = ""
    df = df[df["caso"].str.strip() != ""]
    df["posicion"] = pd.to_numeric(df["posicion"], errors="coerce")
    df = df[df["posicion"].isin(POSICIONES)]
    df = df[df["juicio"].isin(JUICIOS_VALIDOS)]
    df = df.sort_values("fecha").drop_duplicates(
        subset=["caso", "posicion"], keep="last"
    )
    df["posicion"] = df["posicion"].astype(int)
    return df.reset_index(drop=True)


def _leer_tipos_casos() -> dict:
    tipos: dict[str, str] = {}
    if not os.path.isfile(CASOS_CSV) or os.path.getsize(CASOS_CSV) == 0:
        return tipos
    df = pd.read_csv(CASOS_CSV, encoding="utf-8", dtype=str)
    if "caso" in df.columns and "tipo" in df.columns:
        df = df[df["caso"].str.strip() != ""]
        tipos = dict(zip(df["caso"].str.strip(), df["tipo"].map(_normalizar_tipo)))
    return tipos


def _por_caso(df: pd.DataFrame) -> pd.DataFrame:
    """Reorganiza los juicios en una tabla caso x posicion (1-5)."""
    if df.empty:
        return pd.DataFrame()
    pivot = df.pivot(index="caso", columns="posicion", values="juicio")
    pivot = pivot.reindex(columns=POSICIONES)
    return pivot


def _metricas(casos: pd.DataFrame) -> dict:
    if casos.empty:
        return {"casos": 0, "top1": None, "top5": None, "utilidad": None}

    n = len(casos)
    aciertos = casos == "acierto"
    utiles = casos.isin(JUICIOS_UTILES)

    top1 = int(aciertos[1].sum()) if 1 in aciertos.columns else 0
    top5 = int(aciertos.any(axis=1).sum())
    utilidad = float(utiles.sum(axis=1).mean())

    return {
        "casos": n,
        "top1": 100.0 * top1 / n,
        "top5": 100.0 * top5 / n,
        "utilidad": utilidad,
    }


def _linea_total(m: dict, header: bool = False) -> str:
    if header:
        return f"{'Tipo':<14}{'Casos':>6}{'Top 1':>9}{'Top 5':>9}{'Utilidad':>11}"
    return (
        f"Total".ljust(14)
        + f"{m['casos']:>6}"
        + f"{m['top1']:>8.1f}%"
        + f"{m['top5']:>8.1f}%"
        + f"{m['utilidad']:>9.2f}/5"
    )


def _linea_tipo(nombre, m: dict) -> str:
    return (
        f"{nombre:<14}"
        + f"{m['casos']:>6}"
        + f"{m['top1']:>8.1f}%"
        + f"{m['top5']:>8.1f}%"
        + f"{m['utilidad']:>9.2f}/5"
    )


def main():
    resultados = _leer_resultados()
    if resultados.empty:
        msg = ("No hay filas en evaluador/resultados.csv.\n"
               "Evalua primero desde la interfaz y vuelve a correr este script.")
        print(msg)
        return

    casos = _por_caso(resultados)
    tipos = _leer_tipos_casos()
    casos["tipo"] = casos.index.map(lambda c: tipos.get(str(c), "desconocido"))

    total = _metricas(casos)

    lineas = [
        "METRICAS DEL BUSCADOR - GRUPO A",
        "=" * 50,
        f"Filas en resultados.csv : {len(resultados)}",
        f"Casos evaluados         : {total['casos']}",
        "",
        f"Top 1    (% acierto en posicion 1)        : {total['top1']:.1f}%",
        f"Top 5    (% acierto en el top 5)          : {total['top5']:.1f}%",
        f"Utilidad (promedio 0-5 de acierto + sirve): {total['utilidad']:.2f} / 5",
        "",
        _linea_total(total, header=True),
        _linea_tipo("Total", total),
    ]

    tipos_presentes = [t for t in ORDEN_TIPOS if t in set(casos["tipo"])]
    tipos_presentes += sorted(set(casos["tipo"]) - set(ORDEN_TIPOS))
    for tipo in tipos_presentes:
        grupo = casos[casos["tipo"] == tipo]
        lineas.append(_linea_tipo(tipo, _metricas(grupo)))

    salida = "\n".join(lineas)
    with open(SALIDA_TXT, "w", encoding="utf-8") as f:
        f.write(salida + "\n")

    print(salida)
    print(f"\nGuardado: {SALIDA_TXT}")


if __name__ == "__main__":
    main()