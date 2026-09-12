import csv
import json
import os
import threading
from datetime import datetime
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVALUADOR_DIR = os.path.join(BASE_DIR, "evaluador")
CASOS_DIR = os.path.join(EVALUADOR_DIR, "casos")
RESULTADOS_CSV = os.path.join(EVALUADOR_DIR, "resultados.csv")
CASOS_CSV = os.path.join(EVALUADOR_DIR, "casos.csv")
COMPLETADOS_FILE = os.path.join(EVALUADOR_DIR, "completados.json")
COLUMNAS = [
    "caso", "id_correcto", "posicion", "id_resultado",
    "score", "juicio", "quien", "fecha",
]

# Si todavía no hay evaluador/casos/, usamos las imágenes que ya existen en
# data/Search-10 (los 10 casos del grupo). Cuando se cree evaluador/casos/
# con la nomenclatura caso-XXX.jpg, se usa esa carpeta en su lugar.
if not os.path.isdir(CASOS_DIR):
    CASOS_DIR = os.path.join(BASE_DIR, "data", "Search-10")

_lock = threading.Lock()

router = APIRouter(prefix="/evaluacion", tags=["evaluacion"])


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------

class GuardarBody(BaseModel):
    caso: str
    id_correcto: str = ""
    posicion: int
    id_resultado: str
    score: float
    juicio: str  # "acierto" | "sirve" | "no_sirve"
    quien: str = "evaluador"


class CompletarBody(BaseModel):
    caso: str


JUICIOS_VALIDOS = {"acierto", "sirve", "no_sirve"}


# ---------------------------------------------------------------------------
# Helpers CSV
# ---------------------------------------------------------------------------

def _leer_resultados() -> list[dict]:
    if not os.path.isfile(RESULTADOS_CSV) or os.path.getsize(RESULTADOS_CSV) == 0:
        return []
    with open(RESULTADOS_CSV, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _guardar_fila(row: dict):
    """Append atómico de una fila (thread-safe)."""
    os.makedirs(EVALUADOR_DIR, exist_ok=True)
    with _lock:
        needs_header = not os.path.isfile(RESULTADOS_CSV) or os.path.getsize(RESULTADOS_CSV) == 0
        with open(RESULTADOS_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNAS)
            if needs_header:
                writer.writeheader()
            writer.writerow(row)


# ---------------------------------------------------------------------------
# Helpers casos
# ---------------------------------------------------------------------------

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def _archivos_casos() -> list[str]:
    """Archivos de imagen en CASOS_DIR, ordenados."""
    if not os.path.isdir(CASOS_DIR):
        return []
    return sorted(
        f for f in os.listdir(CASOS_DIR)
        if os.path.splitext(f)[1].lower() in IMG_EXTS
    )


def _leer_casos_csv() -> dict[str, dict]:
    info: dict[str, dict] = {}
    if not os.path.isfile(CASOS_CSV):
        return info
    with open(CASOS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            caso = (row.get("caso") or row.get("archivo") or "").strip()
            if caso:
                info[caso] = row
    return info


def _garantizar_casos_csv():
    """Si no existe casos.csv lo crea a partir de las imágenes en CASOS_DIR."""
    if os.path.isfile(CASOS_CSV):
        return
    archivos = _archivos_casos()
    if not archivos:
        return
    os.makedirs(EVALUADOR_DIR, exist_ok=True)
    with open(CASOS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["caso", "id_correcto", "tipo"])
        for archivo in archivos:
            caso = os.path.splitext(archivo)[0]
            w.writerow([caso, "", "dificil"])


def _leer_completados() -> set[str]:
    """Casos marcados como evaluados por el evaluador. Un caso se completa
    cuando el evaluador juzgó TODOS los resultados que devolvió la API (pueden
    ser menos de 5 para fotos difíciles), para que nunca vuelva a aparecer."""
    if not os.path.isfile(COMPLETADOS_FILE):
        return set()
    try:
        with open(COMPLETADOS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return set(data if isinstance(data, list) else data.keys())
    except Exception:
        return set()


def _marcar_completado(caso: str):
    with _lock:
        completados = _leer_completados()
        completados.add(caso)
        os.makedirs(EVALUADOR_DIR, exist_ok=True)
        with open(COMPLETADOS_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(completados), f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/guardar")
def guardar(body: GuardarBody):
    if body.juicio not in JUICIOS_VALIDOS:
        raise HTTPException(400, detail=f"juicio inválido: '{body.juicio}'. Válidos: {sorted(JUICIOS_VALIDOS)}")
    if not 1 <= body.posicion <= 5:
        raise HTTPException(400, detail=f"posicion inválida: {body.posicion}. Debe ser 1-5.")

    row = {
        "caso": body.caso,
        "id_correcto": body.id_correcto,
        "posicion": body.posicion,
        "id_resultado": body.id_resultado,
        "score": body.score,
        "juicio": body.juicio,
        "quien": body.quien,
        "fecha": datetime.now().isoformat(timespec="seconds"),
    }
    _guardar_fila(row)
    return {"ok": True}


@router.post("/completar")
def completar(body: CompletarBody):
    _marcar_completado(body.caso)
    return {"ok": True}


@router.get("/estado")
def estado():
    _garantizar_casos_csv()

    resultados_rows = _leer_resultados()
    juicios_por_caso: dict[str, dict[int, str]] = {}
    for r in resultados_rows:
        caso = r.get("caso", "")
        pos = int(r.get("posicion", 0))
        juicio = r.get("juicio", "")
        if caso and 1 <= pos <= 5 and juicio:
            juicios_por_caso.setdefault(caso, {})[pos] = juicio

    completados = _leer_completados()
    casos_csv = _leer_casos_csv()
    archivos = _archivos_casos()

    casos = []
    for archivo in archivos:
        caso = os.path.splitext(archivo)[0]
        meta = casos_csv.get(caso, {})
        j = juicios_por_caso.get(caso, {})
        evaluado = caso in completados or len(j) >= 5
        casos.append({
            "caso": caso,
            "archivo": archivo,
            "imagen_url": f"http://localhost:8000/casos/{quote(archivo)}",
            "id_correcto": meta.get("id_correcto", ""),
            "tipo": meta.get("tipo", "dificil"),
            "juicios": {str(k): v for k, v in j.items()},
            "evaluado": evaluado,
        })

    return {"casos": casos, "total_resultados": len(resultados_rows)}
