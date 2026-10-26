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
    
    filtro = Filter(
        must=[
            FieldCondition(
                key="color",
                match=MatchValue(value=color_normalizado)
            )
        ]
    )
    
    try:
        # Búsqueda estricta por color con score mínimo
        resultados = db_manager.client.query_points(
            collection_name=db_manager.collection_name,
            query=query_vector.tolist(),
            query_filter=filtro,
            limit=limit,
            offset=offset,
            score_threshold=min_score
        ).points
        
        # Fallback
        if not resultados:
            logger.info("No hubo coincidencia exacta de color. Realizando fallback vectorial...")
            resultados = db_manager.client.query_points(
                collection_name=db_manager.collection_name,
                query=query_vector.tolist(),
                limit=limit,
                offset=offset,
                score_threshold=min_score
            ).points
            
        return resultados
    except Exception as e:
        logger.error(f"Error durante la búsqueda híbrida en Qdrant: {e}")
        raise e
