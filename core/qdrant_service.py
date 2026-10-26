"""
core.qdrant_service
-------------------
Servicio de alto nivel que une QdrantManager con la búsqueda híbrida.
Proporciona una API limpia para el motor RAG: indexar, buscar, eliminar y
consultar salud de la colección vectorial.
"""

import logging
import uuid
from typing import Any

import numpy as np
from qdrant_client.http.models import PointStruct

from core.base_datos import QdrantManager
from core.config import settings
from core.search_service import perform_hybrid_search

logger = logging.getLogger(__name__)

# Namespace fijo para generar UUIDs determinísticos a partir de IDs no-UUID
_QDRANT_ID_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def _id_a_uuid(id_original: str) -> str:
    """
    Convierte un ID arbitrario (ej. "SBX-01-0001") en un UUID determinístico
    válido para Qdrant local. El mismo ID original siempre produce el mismo UUID.
    """
    return str(uuid.uuid5(_QDRANT_ID_NAMESPACE, str(id_original)))


class QdrantService:
    """
    Capa de servicio sobre Qdrant para operaciones RAG.

    Responsabilidades:
      - Crear/verificar colección en Qdrant (siguiendo la configuración de settings)
      - Indexar vectores (embedding + payload con color, id, nombre, etc.)
      - Búsqueda híbrida (vectorial + filtro por color)
      - Consultas de salud y conteo
      - Eliminación de vectores por ID
    """

    def __init__(self, collection_name: str | None = None):
        self.db = QdrantManager(collection_name=collection_name)
        self.collection_name = self.db.collection_name

    # ── Salud y metadatos ──────────────────────────────────────────────

    def health(self) -> dict[str, Any]:
        """Retorna el estado de la conexión y la colección."""
        ok = self.db.health_check()
        return {
            "status": "ok" if ok else "error",
            "collection": self.collection_name,
            "points": self.db.count_points() if ok else 0,
            "qdrant_url": settings.QDRANT_URL or "local (path)",
            "on_disk": True,
        }

    def list_collections(self) -> list[str]:
        """Lista todas las colecciones disponibles en Qdrant."""
        return self.db.list_collections()

    # ── Indexación ─────────────────────────────────────────────────────

    def upsert_embeddings(
        self,
        ids: list[str],
        vectors: list[np.ndarray],
        payloads: list[dict[str, Any]] | None = None,
        batch_size: int = 100,
    ) -> int:
        """
        Inserta o actualiza vectores en Qdrant en lotes.

        Args:
            ids: IDs únicos de cada punto.
            vectors: Embeddings (N x D) normalizados L2.
            payloads: Metadatos por punto (color, nombre, url, etc.).
            batch_size: Tamaño del lote para upsert.

        Returns:
            Número de puntos insertados/actualizados.
        """
        if len(ids) != len(vectors):
            raise ValueError(
                f"ids ({len(ids)}) y vectors ({len(vectors)}) deben tener la misma longitud."
            )

        if payloads is None:
            payloads = [{}] * len(ids)

        puntos = []
        for pid, vector, payload in zip(ids, vectors, payloads):
            if payload is None:
                payload = {}
            # Qdrant local requiere UUID: convertir ID original a UUID determinístico
            punto_uuid = _id_a_uuid(pid)
            # Guardar el ID original en el payload para trazabilidad y retorno
            punto_payload = {"original_id": str(pid), **payload}
            puntos.append(
                PointStruct(
                    id=punto_uuid,
                    vector=vector.tolist() if isinstance(vector, np.ndarray) else list(vector),
                    payload=punto_payload,
                )
            )

        total_insertados = 0
        for inicio in range(0, len(puntos), batch_size):
            lote = puntos[inicio : inicio + batch_size]
            self.db.upsert_vectors(lote)
            total_insertados += len(lote)
            logger.info(
                f"Indexado lote {inicio}-{inicio + len(lote)} de {len(puntos)} en "
                f"'{self.collection_name}'"
            )

        return total_insertados

    def upsert_producto(
        self,
        producto_id: str,
        embedding: np.ndarray,
        nombre: str,
        color: str,
        url: str = "",
        proveedor: str = "",
        imagen: str = "",
    ) -> None:
        """
        Indexa un solo producto en Qdrant.

        El payload incluye todos los campos necesarios para el frontend y el
        filtrado híbrido por color.
        """
        payload = {
            "nombre": nombre,
            "color": str(color).capitalize(),
            "url": url,
            "proveedor": proveedor,
            "imagen": imagen,
        }
        self.upsert_embeddings(
            ids=[producto_id],
            vectors=[embedding],
            payloads=[payload],
            batch_size=1,
        )

    # ── Búsqueda ───────────────────────────────────────────────────────

    def buscar_similares(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        color_filtro: str | None = None,
        min_score: float = 0.5,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Búsqueda híbrida en Qdrant.

        Si se proporciona color_filtro, primero busca por color exacto +
        similitud vectorial. Si no hay resultados, hace fallback a búsqueda
        vectorial pura.

        Returns:
            Lista de dicts con: id, score, payload (nombre, color, url, etc.)
        """
        resultados = perform_hybrid_search(
            db_manager=self.db,
            query_vector=query_vector,
            color_dominante=color_filtro or "",
            limit=top_k,
            min_score=min_score,
            offset=offset,
        )

        salida = []
        for punto in resultados:
            payload = punto.payload or {}
            salida.append(
                {
                    # Devolver el ID original (no el UUID interno de Qdrant)
                    "id": payload.get("original_id", str(punto.id)),
                    "score": round(float(punto.score), 4),
                    "payload": payload,
                }
            )
        return salida

    # ── Mantenimiento ──────────────────────────────────────────────────

    def eliminar_productos(self, ids: list[str]) -> None:
        """Elimina vectores por sus IDs originales (se convierten a UUID internamente)."""
        punto_uuids = [_id_a_uuid(pid) for pid in ids]
        self.db.delete_vectors(point_ids=punto_uuids)

    def vaciar_coleccion(self) -> None:
        """
        Elimina todos los puntos de la colección actual.
        Útil para reindexar desde cero.
        """
        from qdrant_client.http.models import FilterSelector

        # Qdrant no tiene "delete all" directo; se elimina y se recrea la colección
        try:
            self.db.client.delete_collection(collection_name=self.collection_name)
        except Exception as e:
            logger.warning(f"No se pudo eliminar la colección: {e}")
        self.db._ensure_collection()

    @property
    def client(self):
        """Acceso directo al cliente Qdrant subyacente (para operaciones avanzadas)."""
        return self.db.client
