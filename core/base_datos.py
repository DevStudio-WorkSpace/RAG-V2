import logging
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, HnswConfigDiff, PointStruct
from core.config import settings

logger = logging.getLogger(__name__)

class QdrantManager:
    def __init__(self, collection_name: str = None):
        """
        Inicializa el cliente de Qdrant apuntando a Docker o a almacenamiento local según .env.
        """
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
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return info.points_count or 0
        except Exception as e:
            logger.error(f"Error contando puntos: {e}")
            return 0

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
        """
        Crea la colección si no existe, con on_disk=True para HNSW.
        Esto mapea los grafos HNSW directamente al disco (mmap), permitiendo
        búsquedas instantáneas en miles de vectores con bajo consumo de RAM.
        """
        # Obtenemos las colecciones actuales
        collections_response = self.client.get_collections()
        collections = collections_response.collections
        
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            logger.info(f"Creando colección '{self.collection_name}' en Qdrant...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.QDRANT_VECTOR_SIZE,  # CLIP=512, SigLIP=768
                    distance=Distance.COSINE
                ),
                hnsw_config=HnswConfigDiff(
                    on_disk=True  # Crítico para escalabilidad de memoria
                )
            )
            # Crear índice en el payload para filtrar rápidamente por color
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="color",
                field_schema="keyword"
            )
            logger.info("Colección creada con on_disk=True e índice de color exitosamente.")
        else:
            logger.info(f"La colección '{self.collection_name}' ya existe.")
            
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
