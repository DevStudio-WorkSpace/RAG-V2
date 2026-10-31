import logging
from pathlib import Path
from urllib.parse import urlparse

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Obtener la ruta base del proyecto (C:\HACK_3 o similar)
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Rutas absolutas resueltas usando pathlib
    CATALOG_PATH: Path = BASE_DIR / "data" / "images_normalized"
    QDRANT_DATA_PATH: Path = BASE_DIR / "qdrant_data"
    
    # Qdrant (usará memoria/disco si no hay URL)
    QDRANT_URL: str = ""
    QDRANT_API_KEY: SecretStr = SecretStr("")
    QDRANT_COLLECTION_NAME: str = "sublitex_fashion_v1"
    QDRANT_TIMEOUT: int = 30
    QDRANT_GRPC_TIMEOUT: int = 10
    QDRANT_VECTOR_SIZE: int = 512  # CLIP=512, SigLIP=768
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Seguridad API (API keys con roles). Si faltan, los endpoints
    # protegidos responden 503 en lugar de quedar abiertos.
    API_CLIENT_KEY: SecretStr = SecretStr("")
    API_CLIENT_KEYS: SecretStr = SecretStr("")
    API_ADMIN_KEY: SecretStr = SecretStr("")
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Web UI
    UI_HOST: str = "127.0.0.1"
    UI_PORT: int = 7860

    @property
    def cors_origins_list(self) -> list[str]:
        """Orígenes CORS válidos. Ignora '*' y entradas mal formadas."""
        origenes: list[str] = []
        for valor in self.CORS_ORIGINS.split(","):
            origen = valor.strip().rstrip("/")
            if not origen:
                continue
            if origen == "*":
                logger.warning(
                    "CORS_ORIGINS contiene '*'; se ignora porque CORS debe "
                    "estar restringido a orígenes explícitos."
                )
                continue
            parsed = urlparse(origen)
            if (
                parsed.scheme in ("http", "https")
                and parsed.netloc
                and not parsed.path
                and not parsed.query
                and not parsed.fragment
            ):
                if (
                    parsed.scheme == "http"
                    and parsed.hostname not in ("localhost", "127.0.0.1", "::1")
                ):
                    logger.warning(
                        "Origen CORS no local usa HTTP; en produccion use "
                        f"HTTPS: {origen!r}"
                    )
                origenes.append(origen)
            else:
                logger.warning(f"Origen CORS inválido ignorado: {origen!r}")
        return origenes

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()

# Validar rutas críticas al importar
if not settings.CATALOG_PATH.exists():
    logger.warning(f"CATALOG_PATH no existe: {settings.CATALOG_PATH}")
