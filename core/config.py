import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

logger = logging.getLogger(__name__)

# Obtener la ruta base del proyecto (C:\HACK_3 o similar)
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Rutas absolutas resueltas usando pathlib
    CATALOG_PATH: Path = BASE_DIR / "data" / "images_normalized"
    QDRANT_DATA_PATH: Path = BASE_DIR / "qdrant_data"
    
    # Qdrant (usará memoria/disco si no hay URL)
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "sublitex_fashion_v1"
    QDRANT_TIMEOUT: int = 30
    QDRANT_GRPC_TIMEOUT: int = 10
    QDRANT_VECTOR_SIZE: int = 512  # CLIP=512, SigLIP=768
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Web UI
    UI_HOST: str = "127.0.0.1"
    UI_PORT: int = 7860
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()

# Validar rutas críticas al importar
if not settings.CATALOG_PATH.exists():
    logger.warning(f"CATALOG_PATH no existe: {settings.CATALOG_PATH}")
