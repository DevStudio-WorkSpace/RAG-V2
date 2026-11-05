import logging
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

logger = logging.getLogger(__name__)

def perform_hybrid_search(db_manager, query_vector, color_dominante, limit=5, min_score=0.5, offset=0):
    """
    Realiza una búsqueda híbrida en Qdrant.
    Primero busca por filtrado exacto de color. Si no hay coincidencias, 
    hace un fallback a la búsqueda por similitud vectorial pura.
    """
    # Normalizar color para búsqueda case-insensitive
    color_normalizado = str(color_dominante or "").strip().capitalize()
    
    try:
        opciones = {
            "collection_name": db_manager.collection_name,
            "query": query_vector.tolist(),
            "limit": limit,
            "offset": offset,
            "score_threshold": min_score,
        }
        if color_normalizado:
            filtro = Filter(
                must=[
                    FieldCondition(
                        key="color",
                        match=MatchValue(value=color_normalizado),
                    )
                ]
            )
            resultados = db_manager.client.query_points(
                **opciones,
                query_filter=filtro,
            ).points
            if resultados:
                return resultados
            logger.info(
                "No hubo coincidencia exacta de color; se usa búsqueda vectorial."
            )

        return db_manager.client.query_points(
            **opciones,
        ).points
    except Exception as e:
        logger.error(f"Error durante la búsqueda híbrida en Qdrant: {e}")
        raise
