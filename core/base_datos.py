import logging
from pathlib import Path
from urllib.parse import unquote, urlparse

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    HnswConfigDiff,
    PointStruct,
    SnapshotPriority,
    VectorParams,
)
from core.config import settings

logger = logging.getLogger(__name__)

class QdrantManager:
    def __init__(self, collection_name: str = None):
        """
        Inicializa el cliente de Qdrant apuntando a Docker o a almacenamiento local según .env.
        """
        if settings.QDRANT_VECTOR_SIZE != 512:
            raise ValueError(
                "La búsqueda canónica usa CLIP y requiere QDRANT_VECTOR_SIZE=512."
            )
        self.collection_name = collection_name or settings.QDRANT_COLLECTION_NAME
        
        if settings.QDRANT_URL:
            qdrant_api_key = settings.QDRANT_API_KEY.get_secret_value().strip() or None
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=qdrant_api_key,
                timeout=settings.QDRANT_TIMEOUT,
            )
        else:
            self.client = QdrantClient(path=str(settings.QDRANT_DATA_PATH))
        
        self._ensure_collection()

    def health_check(self) -> bool:
        """Verifica que Qdrant esté accesible y la colección exista."""
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check fallido: {e}")
            return False

    def count_points(self) -> int:
        """Retorna el número de vectores en la colección."""
        info = self.client.get_collection(collection_name=self.collection_name)
        return info.points_count or 0

    def delete_vectors(self, point_ids: list):
        """Elimina vectores por ID en lote."""
        if not point_ids:
            return
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=point_ids
            )
            logger.info(f"Eliminados {len(point_ids)} vectores de '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error eliminando vectores: {e}")
            raise

    def list_collections(self) -> list[str]:
        """Lista todas las colecciones disponibles."""
        try:
            response = self.client.get_collections()
            return [c.name for c in response.collections]
        except Exception as e:
            logger.error(f"Error listando colecciones: {e}")
            return []

    def _ensure_collection(self):
        created = False
        if not self.client.collection_exists(self.collection_name):
            if settings.QDRANT_SNAPSHOT_PATH:
                self._restore_snapshot()
            else:
                self._create_collection()
                created = True

        if not self.client.collection_exists(self.collection_name):
            raise RuntimeError(
                f"Qdrant no creó ni restauró la colección '{self.collection_name}'."
            )
        self._validate_collection()
        info = self.client.get_collection(self.collection_name)
        if created or "color" not in (info.payload_schema or {}):
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="color",
                field_schema="keyword",
            )

    def _create_collection(self):
        logger.info("Creando colección '%s' en Qdrant...", self.collection_name)
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=settings.QDRANT_VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
            hnsw_config=HnswConfigDiff(on_disk=True),
        )

    def _restore_snapshot(self):
        location = settings.QDRANT_SNAPSHOT_PATH.strip()
        parsed = urlparse(location)
        if parsed.scheme != "file" or not parsed.path:
            raise ValueError(
                "QDRANT_SNAPSHOT_PATH debe ser una URL file:// a un snapshot "
                "local disponible en el volumen de Qdrant."
            )

        snapshot_path = Path(unquote(parsed.path))
        shared_storage = Path("/qdrant/storage")
        if snapshot_path.is_relative_to(shared_storage):
            app_snapshot_path = settings.QDRANT_DATA_PATH / snapshot_path.relative_to(
                shared_storage
            )
        else:
            app_snapshot_path = snapshot_path
        if not app_snapshot_path.is_file():
            raise FileNotFoundError(
                f"No se encontró el snapshot configurado: {app_snapshot_path}"
            )

        logger.info(
            "Restaurando colección '%s' desde el snapshot local configurado.",
            self.collection_name,
        )
        if not settings.QDRANT_URL:
            location = app_snapshot_path.resolve().as_uri()
        self.client.recover_snapshot(
            collection_name=self.collection_name,
            location=location,
            priority=SnapshotPriority.SNAPSHOT,
            wait=True,
        )

    def _validate_collection(self):
        info = self.client.get_collection(self.collection_name)
        vectors = info.config.params.vectors
        if isinstance(vectors, dict):
            vectors = vectors.get("default")
        if vectors is None:
            raise ValueError(
                f"La colección '{self.collection_name}' no tiene un vector "
                "denso predeterminado."
            )
        if vectors.size != settings.QDRANT_VECTOR_SIZE:
            raise ValueError(
                f"La colección '{self.collection_name}' usa {vectors.size} "
                f"dimensiones; se requieren {settings.QDRANT_VECTOR_SIZE}."
            )
        if vectors.distance != Distance.COSINE:
            raise ValueError(
                f"La colección '{self.collection_name}' usa distancia "
                f"{vectors.distance}; se requiere Cosine."
            )
            
    def upsert_vectors(self, points: list[PointStruct]):
        """
        Inserta o actualiza vectores en lote.
        """
        if not points:
            return
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
