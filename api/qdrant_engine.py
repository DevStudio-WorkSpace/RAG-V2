# -*- coding: utf-8 -*-
"""
api.qdrant_engine
-----------------
Motor de búsqueda vectorial basado en Qdrant para el RAG del proyecto.

Expone la misma interfaz que api.search_engine (cargar_indice, search_similar,
info_indice) pero respaldado por Qdrant en lugar de archivos .npy locales.

Esto permite que la API FastAPI use Qdrant como backend de búsqueda vectorial
escalable, mientras conserva compatibilidad con los endpoints existentes.
"""

import logging
import os
import sys

import numpy as np

# Asegurar importación del módulo core independientemente del working directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from core.qdrant_service import QdrantService
from core.config import settings

logger = logging.getLogger(__name__)

# Instancia singleton del servicio Qdrant
_qdrant_service: QdrantService | None = None

def _get_qdrant() -> QdrantService:
    """Retorna la instancia singleton de QdrantService, inicializándola si es necesario."""
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService()
    return _qdrant_service


def cargar_indice() -> None:
    """
    Inicializa la conexión con Qdrant y verifica que la colección exista.

    No carga embeddings en memoria (Qdrant los gestiona en disco), pero
    verifica la salud de la colección y la crea si no existe.
    """
    qdrant = _get_qdrant()
    salud = qdrant.health()
    if salud["status"] != "ok":
        raise RuntimeError(
            f"Qdrant no está disponible o la colección no está lista: {salud}"
        )
    logger.info(
        "Índice Qdrant listo: colección '%s' con %s puntos.",
        salud["collection"],
        salud["points"],
    )


def verificar_coleccion() -> dict:
    """Verifica disponibilidad, esquema y estado de la colección Qdrant."""
    qdrant = _get_qdrant()
    salud = qdrant.health()
    if salud["status"] != "ok":
        raise RuntimeError(
            f"Qdrant no está disponible o la colección no está lista: {salud}"
        )
    # Fuerza validación de esquema/vector/distancia en el gestor.
    qdrant.db._validate_collection()
    info = qdrant.db.client.get_collection(collection_name=qdrant.collection_name)
    points = info.points_count or 0
    return {
        **salud,
        "status": "ok",
        "points": points,
        "verificada": True,
    }


def crear_snapshot_coleccion() -> str | None:
    """Crea un snapshot de la colección activa en Qdrant."""
    qdrant = _get_qdrant()
    return qdrant.crear_snapshot()


def preparar_coleccion_arranque(
    csv_path: str | None = None,
    embeddings_path: str | None = None,
) -> dict:
    """Verifica/crea la colección, migra si está vacía y crea snapshot."""
    cargar_indice()
    estado = verificar_coleccion()
    migrados = 0
    if estado["points"] == 0:
        migrados = indexar_productos_desde_csv(
            csv_path=csv_path,
            embeddings_path=embeddings_path,
        )
        estado = verificar_coleccion()
        if estado["points"] == 0:
            raise RuntimeError(
                "La colección Qdrant está vacía y no se pudieron migrar productos."
            )

    snapshot = None
    snapshot_error = None
    try:
        snapshot = crear_snapshot_coleccion()
    except Exception as e:
        snapshot_error = str(e)
        logger.warning("No se pudo crear snapshot de arranque: %s", e)
    if snapshot is None and snapshot_error is None and not settings.QDRANT_URL:
        logger.info(
            "Snapshot de arranque omitido en modo Qdrant local; la persistencia usa %s.",
            settings.QDRANT_DATA_PATH,
        )

    estado["snapshot"] = snapshot
    if snapshot_error:
        estado["snapshot_error"] = snapshot_error
    estado["migrados"] = migrados
    estado["products"] = estado["points"]
    estado["embeddings"] = estado["points"]
    return estado


def search_similar(
    query_embedding,
    top_k: int = 5,
    color_filtro: str | None = None,
    min_score: float = 0.5,
) -> list[dict]:
    """
    Busca vectores similares en Qdrant.

    Contrato de respuesta idéntico al motor anterior:
    list de dicts con keys: id, nombre, imagen, url, proveedor, score.

    Args:
        query_embedding: Vector de consulta (np.ndarray o list).
        top_k: Número máximo de resultados.
        color_filtro: Si se proporciona, filtra por este color (búsqueda híbrida).
        min_score: Score mínimo de similitud coseno (0.0 - 1.0).
    """
    qdrant = _get_qdrant()
    v_query = np.array(query_embedding, dtype=np.float32).flatten()

    resultados = qdrant.buscar_similares(
        query_vector=v_query,
        top_k=top_k,
        color_filtro=color_filtro,
        min_score=min_score,
    )

    salida = []
    for r in resultados:
        payload = r.get("payload", {})
        salida.append(
            {
                "id": r["id"],
                "nombre": payload.get("nombre", ""),
                "imagen": payload.get("imagen", ""),
                "url": payload.get("url", ""),
                "proveedor": payload.get("proveedor", "Designs Aimari"),
                "score": r["score"],
                "color": payload.get("color", ""),
                "qdrant": True,
            }
        )
    return salida


def info_indice() -> dict:
    """
    Retorna información sobre el estado del índice Qdrant.
    """
    qdrant = _get_qdrant()
    salud = qdrant.health()
    return {
        "products": salud["points"],
        "embeddings": salud["points"],
        "collection": salud["collection"],
        "status": salud["status"],
        "qdrant_url": salud["qdrant_url"],
        "on_disk": salud["on_disk"],
        "desfase_detectado": False,
        "observacion": "Índice respaldado por Qdrant (almacenamiento en disco)",
    }


def health() -> dict:
    """Endpoint de salud detallado de Qdrant."""
    qdrant = _get_qdrant()
    return qdrant.health()


def indexar_productos_desde_csv(csv_path: str | None = None, embeddings_path: str | None = None) -> int:
    """
    Indexa todos los productos desde data/products.csv y sus embeddings en Qdrant.

    Si no se proporcionan rutas, usa los valores por defecto del proyecto.
    Requiere que los embeddings .npy ya estén generados (scripts/generar_embeddings.py).
    """
    import csv

    if csv_path is None:
        csv_path = os.path.join(BASE_DIR, "data", "products.csv")
    if embeddings_path is None:
        embeddings_path = os.path.join(BASE_DIR, "data", "embeddings.npy")
    ids_path = os.path.join(os.path.dirname(embeddings_path), "ids.npy")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró {csv_path}")
    if not os.path.exists(embeddings_path):
        raise FileNotFoundError(f"No se encontró {embeddings_path}")
    if not os.path.exists(ids_path):
        raise FileNotFoundError(f"No se encontró el archivo de IDs alineados: {ids_path}")

    qdrant = _get_qdrant()

    # Leer productos
    productos = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columnas = ["id", "proveedor", "pagina", "imagen", "nombre_original", "url"]
        if reader.fieldnames != columnas:
            raise ValueError(
                f"Las columnas de {csv_path} deben ser exactamente: "
                f"{','.join(columnas)}"
            )
        for fila in reader:
            productos.append(fila)

    # Cargar embeddings
    embeddings = np.load(embeddings_path).astype(np.float32)

    if embeddings.ndim != 2 or embeddings.shape[1] != settings.QDRANT_VECTOR_SIZE:
        raise ValueError(
            f"Los embeddings deben tener forma (N, {settings.QDRANT_VECTOR_SIZE}); "
            f"se recibió {embeddings.shape}"
        )
    if not np.isfinite(embeddings).all():
        raise ValueError(f"Hay valores no finitos en {embeddings_path}")
    if np.any(np.linalg.norm(embeddings, axis=1) == 0):
        raise ValueError(f"Hay embeddings nulos en {embeddings_path}")
    if len(productos) != embeddings.shape[0]:
        raise ValueError(
            f"Desfase: {len(productos)} productos en CSV vs "
            f"{embeddings.shape[0]} embeddings en {embeddings_path}"
        )

    ids = np.load(ids_path, allow_pickle=True)
    csv_ids = [str(fila.get("id", "")) for fila in productos]
    ids_cargados = [str(product_id) for product_id in ids]
    if ids_cargados != csv_ids:
        raise ValueError(
            f"IDs desalineados: {ids_path} debe coincidir posición por posición "
            f"con la columna id de {csv_path}"
        )
    if any(not product_id for product_id in csv_ids) or len(set(csv_ids)) != len(csv_ids):
        raise ValueError(f"Los IDs en {csv_path} deben ser únicos y no vacíos")

    vectors = []
    payloads = []

    for i, fila in enumerate(productos):
        pid = csv_ids[i]
        vectors.append(embeddings[i])
        payloads.append(
            {
                "nombre": fila.get("nombre_original", pid),
                "imagen": fila.get("imagen", ""),
                "url": fila.get("url", ""),
                "proveedor": fila.get("proveedor", "Designs Aimari"),
                "color": fila.get("color_detectado", "Desconocido"),
            }
        )

    total = qdrant.upsert_embeddings(
        ids=ids,
        vectors=vectors,
        payloads=payloads,
        batch_size=100,
    )
    logger.info(f"Indexados {total} productos en Qdrant desde {csv_path}")
    return total
