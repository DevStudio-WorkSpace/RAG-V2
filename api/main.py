import io
import logging
import os
import sys
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from threading import Lock

from PIL import Image, UnidentifiedImageError
from fastapi import Depends, FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sentence_transformers import SentenceTransformer


# ── Tipos de imagen admitidos por la API ───────────────────────────────────
# La validación final del formato la realiza Pillow sobre el contenido.
# También se acepta application/octet-stream porque algunos clientes (ej. curl)
# no siempre adjuntan el MIME correcto; la validación real la hace Pillow al
# abrir la imagen, la cual detecta el formato desde los bytes.
MIME_PERMITIDOS = ("image/jpeg", "image/jpg", "image/png", "image/webp", "application/octet-stream")

# Asegurar importación del módulo search_engine independientemente del working directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.search_engine import search_similar
from api.search_engine_hito2 import search_similar_reranked
from api.preprocesar_consulta import preparar_consulta
from api.security import (
    advertencias_config_seguridad,
    require_admin,
    require_client,
)
from api.qdrant_engine import (
    cargar_indice as cargar_indice_qdrant,
    info_indice as info_indice_qdrant,
    health as health_qdrant,
    indexar_productos_desde_csv,
)
from core.config import settings

MODEL_NAME = "clip-ViT-B-32"  # equivalente a openai/clip-vit-base-patch32
logger = logging.getLogger(__name__)
_model = None

MODELOS_ETIQUETA = {"clip": "openai/clip-vit-base-patch32"}


def _encodificar(imagen, modelo: str = "clip"):
    """Genera un embedding CLIP compatible con la colección Qdrant activa."""
    if modelo != "clip":
        raise ValueError("La colección Qdrant activa solo admite el modelo CLIP.")
    return get_model().encode(imagen)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Verifica Qdrant, migra el índice inicial si está vacío y carga CLIP."""
    for aviso in advertencias_config_seguridad():
        logger.warning("AVISO DE SEGURIDAD: %s", aviso)

    cargar_indice_qdrant()
    estado = info_indice_qdrant()
    if estado["products"] == 0:
        total = indexar_productos_desde_csv()
        if total == 0:
            raise RuntimeError(
                "La colección Qdrant está vacía y no se pudieron migrar productos."
            )
        logger.info("Migrados %s productos a Qdrant durante el arranque.", total)

    try:
        get_model()
        logger.info("Modelo CLIP '%s' cargado correctamente.", MODEL_NAME)
    except Exception as e:
        logger.exception("No se pudo precargar el modelo CLIP; se intentará al buscar: %s", e)

    yield


app = FastAPI(
    title="Motor de Búsqueda Visual RAG - Sala 3 API",
    description="API FastAPI para búsqueda e integración visual de camisetas deportivas",
    version="1.1.0",
    lifespan=lifespan,
)

# CORS restringido a los orígenes explícitos del frontend. No se permite "*"
# ni cookies de sesión: la autenticación viaja en el header X-API-Key.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key", "Authorization"],
    max_age=600,
)

# Parámetros del Hito 2: cuántos candidatos se recuperan en la fase amplia
# antes de hacer el reranking por color.
CANDIDATOS_INICIALES = 30

def _motor_reranked(
    embedding,
    query_image,
    modelo: str,
    top_k: int = 5,
    color_filtro: str | None = None,
    min_score: float = 0.5,
):
    """Recupera candidatos en Qdrant y aplica el reranking visual del Hito 2."""
    if modelo != "clip":
        raise ValueError("La colección Qdrant activa solo admite el modelo CLIP.")
    return search_similar_reranked(
        embedding,
        query_image=query_image,
        top_k=top_k,
        candidatos_iniciales=CANDIDATOS_INICIALES,
        modelo=modelo,
        usar_qdrant=True,
        color_filtro=color_filtro,
        min_score=min_score,
    )

# Tamaño mínimo (px por lado) para aceptar una imagen de consulta. Por debajo
# no hay píxeles suficientes para que el histograma HSV ni el descriptor de
# estructura tengan sentido, y CLIP produce vectores poco fiables.
MIN_DIM = 32

# Límite del archivo subido para evitar lecturas sin cota en el servidor.
MAX_UPLOAD_SIZE = 15 * 1024 * 1024  # 15 MB límite de tamaño de subida

# Control básico de Rate Limiting en memoria por IP
_request_counts = {}
_request_counts_lock = Lock()
RATE_LIMIT_WINDOW = 60  # segundos
RATE_LIMIT_MAX_REQUESTS = 60  # máx peticiones por minuto por IP


def _check_rate_limit(client_ip: str) -> bool:
    """Verifica si la IP excede el límite de peticiones (Rate Limiting)."""
    with _request_counts_lock:
        now = time.time()
        requests = _request_counts.setdefault(client_ip, [])
        requests[:] = [started for started in requests if now - started < RATE_LIMIT_WINDOW]
        if len(requests) >= RATE_LIMIT_MAX_REQUESTS:
            return False
        requests.append(now)
        return True


def get_model():
    """Retorna la instancia singleton del modelo CLIP, cargándolo si es necesario."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


@app.get("/health")
def health():
    """Endpoint público de liveness/readiness (no expone secretos).

    Se mantiene sin API key para que Docker/Kubernetes y el proxy puedan
    comprobar el estado del servicio sin credenciales.
    """
    try:
        info = info_indice_qdrant()
        if info["status"] != "ok":
            return JSONResponse(
                status_code=503,
                content={"status": "error", "detail": "Qdrant no está disponible"},
            )
        return {
            "status": "ok",
            "products": info["products"],
            "embeddings": info["embeddings"],
            "model": MODELOS_ETIQUETA["clip"],
            "backend": "qdrant",
            "collection": info["collection"],
            "desfase_detectado": False,
            "observacion": info["observacion"],
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )


def _error_dimensiones(imagen) -> str | None:
    """Devuelve un mensaje de error si la imagen es demasiado pequeña (None si ok)."""
    w, h = imagen.size
    if min(w, h) < MIN_DIM:
        return (
            f"La imagen es demasiado pequeña ({w}x{h}); se requiere un mínimo "
            f"de {MIN_DIM}px por lado para una búsqueda fiable."
        )
    return None


def _leer_imagen_subida(file: UploadFile | None):
    if file is None or (file.content_type and file.content_type not in MIME_PERMITIDOS):
        return None, JSONResponse(
            status_code=400,
            content={"error": "El archivo enviado no es una imagen válida"},
        )

    contents = file.file.read(MAX_UPLOAD_SIZE + 1)
    if len(contents) > MAX_UPLOAD_SIZE:
        return None, JSONResponse(
            status_code=413,
            content={
                "error": (
                    "El archivo excede el tamaño máximo permitido de "
                    f"{MAX_UPLOAD_SIZE // (1024 * 1024)}MB."
                )
            },
        )

    try:
        imagen = Image.open(io.BytesIO(contents)).convert("RGB")
    except (
        OSError,
        ValueError,
        UnidentifiedImageError,
        Image.DecompressionBombError,
    ):
        return None, JSONResponse(
            status_code=400,
            content={"error": "El archivo enviado no es una imagen válida"},
        )

    error_dim = _error_dimensiones(imagen)
    if error_dim:
        return None, JSONResponse(status_code=400, content={"error": error_dim})
    return imagen, None


@app.post(
    "/search/image",
    dependencies=[Depends(require_client)],
    tags=["búsqueda"],
)
@app.post(
    "/search/image/qdrant",
    dependencies=[Depends(require_client)],
    deprecated=True,
    tags=["compatibilidad"],
)
@app.post(
    "/search/image/v2",
    dependencies=[Depends(require_client)],
    deprecated=True,
    tags=["compatibilidad"],
)
def search_image(
    request: Request,
    file: UploadFile | None = File(None),
    modo: str = Form("auto"),
    modelo: str = Form("clip"),
    top_k: int = Form(5, ge=1, le=50),
    color_filtro: str | None = Form(None),
    min_score: float = Form(0.5, ge=-1.0, le=1.0),
):
    """
    Busca en Qdrant y aplica el reranking visual del Hito 2.

    ``/search/image/qdrant`` y ``/search/image/v2`` son alias de compatibilidad
    temporal. Los modos ``original``, ``clasico`` y ``legacy`` se conservan
    únicamente como baseline del Hito 1 para la evaluación comparativa.
    """
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "Demasiadas peticiones. Por favor intente más tarde (Rate limit excedido)."}
        )

    if modo not in ("auto", "completo", "procesada", "original", "clasico", "legacy"):
        return JSONResponse(
            status_code=400,
            content={"error": f"Modo desconocido: {modo}"},
        )
    if modelo != "clip":
        return JSONResponse(
            status_code=400,
            content={
                "error": (
                    "La colección Qdrant activa utiliza CLIP (512 dimensiones); "
                    "seleccione modelo=clip."
                )
            },
        )

    imagen, error_imagen = _leer_imagen_subida(file)
    if error_imagen:
        return error_imagen

    try:
        get_model()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error al cargar el modelo CLIP: {e}"},
        )

    try:
        t0 = time.perf_counter()
        etiqueta_modelo = MODELOS_ETIQUETA[modelo]
        if modo == "legacy":
            logger.warning("modo=legacy usa el índice .npy solo para evaluación histórica.")
            embedding = _encodificar(imagen, "clip")
            return search_similar(embedding, top_k=top_k)

        if modo == "original":
            logger.warning("modo=original usa el índice .npy solo como baseline del Hito 1.")
            embedding = _encodificar(imagen, "clip")
            resultados = search_similar(embedding, top_k=top_k)
            return {
                "query_id": f"q_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
                "modo": "original",
                "modelo": etiqueta_modelo,
                "tiempo_segundos": round(time.perf_counter() - t0, 3),
                "resultados": resultados,
            }

        prep = preparar_consulta(imagen)
        procesada = prep["procesada"]
        embedding = _encodificar(procesada, "clip")

        if modo == "clasico":
            logger.warning("modo=clasico usa el índice .npy solo como baseline del Hito 1.")
            resultados = search_similar(embedding, top_k=top_k)
            modo_usado = "clasico"
        else:
            resultados = _motor_reranked(
                embedding,
                procesada,
                modelo,
                top_k=top_k,
                color_filtro=color_filtro,
                min_score=min_score,
            )
            modo_usado = "qdrant" if request.url.path.endswith("/qdrant") else "completo"

        return {
            "query_id": f"q_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
            "modo": modo_usado,
            "modelo": etiqueta_modelo,
            "preprocesamiento": {
                "ok": True,
                "pasos": prep["pasos"],
                "backend": prep["backend"],
                "bbox": prep["bbox"],
                "recorte_pct": prep["recorte_pct"],
                "tiempo_segundos": prep["tiempo_segundos"],
            },
            "tiempo_segundos": round(time.perf_counter() - t0, 3),
            "backend": "qdrant" if modo_usado != "clasico" else "npy-compatibility",
            "top_k": top_k,
            "color_filtro": color_filtro,
            "min_score": min_score,
            "candidatos_evaluados": CANDIDATOS_INICIALES if modo_usado != "clasico" else top_k,
            "resultados": resultados,
        }
    except FileNotFoundError as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Falta un archivo de datos: {str(e)}"}
        )
    except ValueError as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error interno: {str(e)}"}
        )


# ════════════════════════════════════════════════════════════════════════════
# ENDPOINTS QDRANT (RAG escalable)
# ════════════════════════════════════════════════════════════════════════════


@app.get("/health/qdrant", dependencies=[Depends(require_admin)])
def health_qdrant_endpoint():
    """Estado de salud de Qdrant: colección, puntos, URL, almacenamiento en disco."""
    try:
        return health_qdrant()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )


@app.get("/collections/qdrant", dependencies=[Depends(require_admin)])
def listar_colecciones_qdrant():
    """Lista todas las colecciones disponibles en Qdrant."""
    try:
        qdrant = _get_qdrant_service()
        return {"colecciones": qdrant.list_collections()}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )


@app.post("/index/qdrant", dependencies=[Depends(require_admin)])
def indexar_qdrant(
    csv_path: str = None,
    embeddings_path: str = None,
):
    """
    Indexa productos desde data/products.csv y sus embeddings en Qdrant.

    Parámetros opcionales (query string):
      - csv_path: ruta al CSV de productos (default: data/products.csv)
      - embeddings_path: ruta al archivo .npy de embeddings (default: data/embeddings.npy)
    """
    try:
        total = indexar_productos_desde_csv(
            csv_path=csv_path,
            embeddings_path=embeddings_path,
        )
        return {
            "status": "ok",
            "productos_indexados": total,
            "coleccion": settings.QDRANT_COLLECTION_NAME,
        }
    except FileNotFoundError as e:
        return JSONResponse(
            status_code=404,
            content={"error": str(e)}
        )
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error indexando en Qdrant: {str(e)}"}
        )


def _get_qdrant_service():
    """Obtiene la instancia singleton de QdrantService desde qdrant_engine."""
    from api.qdrant_engine import _get_qdrant
    return _get_qdrant()
