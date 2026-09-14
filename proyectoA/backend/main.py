"""
Backend del módulo Search-10: bucle de entrenamiento / re-ranking con
retroalimentación. Vive 100% dentro de proyectoA/ (no toca la API raíz).

Reutiliza (importando, sin modificar) el motor RAG de la raíz:
  - api.preprocesar_consulta  -> prepara la imagen de consulta (Sala 2)
  - api.search_engine_hito2   -> recuperación amplia + reranking visual (Hito 2)
  - api.main (helpers internos) -> modelos CLIP/OpenCLIP/SigLIP y encoding de
                                   embeddings (carga única por proceso)

Persistencia del aprendizaje (sobrevive entre ejecuciones):
  proyectoA/.feedback/feedback.json
    -> { "<archivo-consulta>": { "<id_resultado>": "acierto|sirve|incorrecto" } }

Cada resultado marcado "incorrecto" para una consulta queda EXCLUIDO en
futuras búsquedas con esa misma imagen; el Top K se rellena con las siguientes
alternativas visuales válidas del pool rerankeadas (sin rellenar con basura:
respeta el umbral dinámico del motor).

Arranque:
  cd proyectoA
  ../venv/bin/python -m uvicorn backend.main:app --port 8400
"""

import json
import os
import sys
import threading
import time
from typing import Optional

from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Rutas: todo dentro de proyectoA (la raíz se usa SÓLO para importar el motor)
# ---------------------------------------------------------------------------
PROYECTOA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../proyectoA
ROOT_DIR = os.path.dirname(PROYECTOA_DIR)                                      # .../RAG-V2
SEARCH10_DIR = os.path.join(PROYECTOA_DIR, "Search-10")
FEEDBACK_DIR = os.path.join(PROYECTOA_DIR, ".feedback")
FEEDBACK_FILE = os.path.join(FEEDBACK_DIR, "feedback.json")

sys.path.insert(0, ROOT_DIR)  # para importar el motor RAG de la raíz

# ---------------------------------------------------------------------------
# Configuración del motor
# ---------------------------------------------------------------------------
MODELOS_VALIDOS = ("clip", "openclip", "fusion")
TOP_K_DEFAULT = 5
POOL = 15                     # candidatos rerankeados para poder "rellenar"
CANDIDATOS_INICIALES = 30
CANDIDATOS_INICIALES_FUSION = 200
JUICIOS_VALIDOS = {"acierto", "sirve", "incorrecto"}
IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

_LOCK = threading.RLock()  # reentrante: _guardar_feedback se usa dentro de with _LOCK

app = FastAPI(
    title="Search-10 · Feedback Loop API",
    description="Búsqueda real sobre proyectoA/Search-10 con exclusiones "
                "persistentes por feedback (entrenamiento local).",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Persistencia del feedback
# ---------------------------------------------------------------------------


def _leer_feedback() -> dict:
    if not os.path.isfile(FEEDBACK_FILE):
        return {}
    try:
        with open(FEEDBACK_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _guardar_feedback(data: dict):
    os.makedirs(FEEDBACK_DIR, exist_ok=True)
    with _LOCK:
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _feedback_de_consulta(imagen: str) -> dict:
    return _leer_feedback().get(imagen, {})


def _excluidos_de(imagen: str) -> set:
    return {
        rid for rid, j in _feedback_de_consulta(imagen).items()
        if j == "incorrecto"
    }


# ---------------------------------------------------------------------------
# Listado de imágenes de consulta (Search-10)
# ---------------------------------------------------------------------------


def _ruta_imagen(imagen: str) -> Optional[str]:
    """Valida que la consulta sea una imagen existente de Search-10."""
    if not imagen or os.path.basename(imagen) != imagen:
        return None
    ext = os.path.splitext(imagen)[1].lower()
    if ext not in IMG_EXTS:
        return None
    ruta = os.path.join(SEARCH10_DIR, imagen)
    if not os.path.isfile(ruta):
        return None
    return ruta


@app.get("/search10/imagenes")
def imagenes():
    """Lista las imágenes de consulta disponibles en proyectoA/Search-10."""
    if not os.path.isdir(SEARCH10_DIR):
        return {"imagenes": []}
    from urllib.parse import quote
    lista = sorted(
        f for f in os.listdir(SEARCH10_DIR)
        if os.path.splitext(f)[1].lower() in IMG_EXTS
    )
    return {"imagenes": [
        {"nombre": f, "url": f"/search10/images/{quote(f)}"}
        for f in lista
    ]}


# ---------------------------------------------------------------------------
# Motor de búsqueda (reutiliza el RAG de la raíz)
# ---------------------------------------------------------------------------


def _app_main():
    """Importa api.main bajo demanda (evita trabajo al arrancar y no lo toca)."""
    from api import main as app_main
    return app_main


def _pool_resultados(imagen: Image.Image, modelo: str, top_k: int = POOL):
    """Pool de candidatos: recuperación amplia + reranking visual (Hito 2)
    pidiendo más que el Top K para poder rellenar exclusiones por feedback."""
    from api.preprocesar_consulta import preparar_consulta
    from api.search_engine_hito2 import (
        search_similar_reranked,
        search_similar_reranked_fusion,
    )

    app_main = _app_main()
    prep = preparar_consulta(imagen)
    procesada = prep["procesada"]
    emb = app_main._encodificar(procesada, modelo)

    if modelo == "fusion":
        return search_similar_reranked_fusion(
            emb,
            query_image=procesada,
            top_k=top_k,
            candidatos_iniciales=CANDIDATOS_INICIALES_FUSION,
        )
    return search_similar_reranked(
        emb,
        query_image=procesada,
        top_k=top_k,
        candidatos_iniciales=CANDIDATOS_INICIALES,
        modelo=modelo,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


class BuscarBody(BaseModel):
    imagen: str
    modelo: str = "clip"
    top_k: int = Field(TOP_K_DEFAULT, ge=1, le=10)


@app.post("/search10/buscar")
def buscar(body: BuscarBody):
    ruta = _ruta_imagen(body.imagen)
    if ruta is None:
        raise HTTPException(
            400,
            "La imagen de consulta no existe en proyectoA/Search-10.",
        )
    if body.modelo not in MODELOS_VALIDOS:
        raise HTTPException(
            400,
            f"Modelo desconocido '{body.modelo}'; válidos: {', '.join(MODELOS_VALIDOS)}",
        )

    app_main = _app_main()
    try:
        t0 = time.perf_counter()
        imagen = Image.open(ruta).convert("RGB")

        pool = _pool_resultados(imagen, body.modelo, POOL)
        excluidos = _excluidos_de(body.imagen)
        feedback = _feedback_de_consulta(body.imagen)

        final = []
        for r in pool:
            if r["id"] in excluidos:
                continue
            final.append(r)
            if len(final) >= body.top_k:
                break

        return {
            "query_imagen": body.imagen,
            "modelo": app_main.MODELOS_ETIQUETA[body.modelo],
            "tiempo_segundos": round(time.perf_counter() - t0, 3),
            "top_k": body.top_k,
            "pool_candidatos": len(pool),
            "excluidos_aplicados": sorted(excluidos),
            "resultados": final,
            "feedback": {r["id"]: feedback.get(r["id"], "") for r in final},
        }
    except FileNotFoundError as e:
        return JSONResponse(500, {"error": f"Falta un archivo de datos: {e}"})
    except ValueError as e:
        return JSONResponse(500, {"error": str(e)})
    except Exception as e:
        return JSONResponse(500, {"error": f"Error interno: {e}"})


class FeedbackBody(BaseModel):
    imagen: str
    id_resultado: str
    juicio: str  # "acierto" | "sirve" | "incorrecto"


@app.post("/search10/feedback")
def guardar_feedback(body: FeedbackBody):
    if _ruta_imagen(body.imagen) is None:
        raise HTTPException(
            400, "La imagen de consulta no existe en proyectoA/Search-10."
        )
    if body.juicio not in JUICIOS_VALIDOS:
        raise HTTPException(
            400,
            f"Juicio inválido '{body.juicio}'; válidos: {sorted(JUICIOS_VALIDOS)}",
        )

    with _LOCK:
        data = _leer_feedback()
        data.setdefault(body.imagen, {})[body.id_resultado] = body.juicio
        _guardar_feedback(data)

    return {
        "imagen": body.imagen,
        "id_resultado": body.id_resultado,
        "juicio": body.juicio,
        "feedback": data[body.imagen],
        "excluidos": sorted(_excluidos_de(body.imagen)),
    }


@app.get("/search10/feedback")
def estado_feedback():
    """Todo el estado de entrenamiento: por consulta, id_resultado -> juicio."""
    return {
        "feedback": _leer_feedback(),
        "archivo": "proyectoA/.feedback/feedback.json",
    }


class LimpiarBody(BaseModel):
    imagen: Optional[str] = None  # si se omite, limpia TODO el feedback


@app.post("/search10/feedback/limpiar")
def limpiar_feedback(body: LimpiarBody):
    """Resetea el feedback: de una imagen concreta o de todo el sistema."""
    with _LOCK:
        data = _leer_feedback()
        if body.imagen:
            eliminados = len(data.pop(body.imagen, {}))
        else:
            eliminados = sum(len(v) for v in data.values())
            data = {}
        _guardar_feedback(data)

    return {"ok": True, "eliminados": eliminados}


# ---------------------------------------------------------------------------
# Imágenes de consulta (Search-10)
# ---------------------------------------------------------------------------
app.mount("/search10/images", StaticFiles(directory=SEARCH10_DIR), name="search10-images")