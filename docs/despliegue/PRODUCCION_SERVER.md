# Guía de Despliegue en Servidor de Producción (RAG Sublitex)

> Guía en revisión. Backup y restauración aún requieren correcciones y pruebas; el rollback de imágenes está documentado abajo, pero falta probarlo con Docker/VPS. Los comandos parten de la raíz del repositorio.


Esta guía detalla el procedimiento estándar para verificar, transferir, configurar y levantar el sistema RAG (FastAPI + Qdrant + Next.js) en un servidor de producción (VPS, AWS, GCP, DigitalOcean, etc.).

---

## 1. Verificación Previa Local (Opcional pero Recomendado)

Antes de realizar la migración al servidor, confirma que los contenedores locales respondan:

1. **Abrir en navegador:**
   - **Frontend (UI):** [http://localhost:3000](http://localhost:3000)
   - **Swagger API:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Panel Qdrant:** [http://localhost:6333/dashboard](http://localhost:6333/dashboard) (solo desde el servidor o por túnel SSH; requiere `QDRANT_API_KEY`)
2. **Sincronizar vectores localmente (si la base arrancó vacía):**
   ```bash
   docker exec -it sublitex_api python scripts/migrar_a_qdrant.py
   ```
3. Realizar una búsqueda de prueba subiendo una imagen para confirmar la inferencia de CLIP y el ranking visual.

---

## 2. Preparación de Archivos para Transferencia

### Archivos y carpetas obligatorios a transferir:
```text
├── api/                       # Código de la API FastAPI
├── core/                      # Servicios centrales y conexión a Qdrant
├── data/                      # Catálogo e índices canónicos:
│   ├── products.csv           # Metadatos del catálogo
│   ├── images_normalized/     # Banco de imágenes limpias
│   └── *.npy                  # Embeddings precomputados
├── frontend/                  # Aplicación Next.js:
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── Dockerfile
│   └── tsconfig.json, next.config.ts, etc.
├── scripts/                   # Scripts de mantenimiento (migrar_a_qdrant.py, etc.)
├── Dockerfile.api             # Definición de contenedor para FastAPI
├── docker-compose.yml         # Orquestación de servicios
├── requirements.txt           # Dependencias de Python
└── .env                       # Variables de entorno base
```

### Archivos y carpetas que NO se deben subir:
- ❌ `frontend/node_modules/` (Docker los instala durante el build)
- ❌ `frontend/.next/` (generado automáticamente al compilar)
- ❌ carpetas `__pycache__/`
- ❌ entornos virtuales `.venv/`
- ❌ `.git/` (si transfieres por archivo comprimido)
- ❌ `.env` y `frontend/.env.local` (crear en el servidor, nunca empaquetar)
- ❌ claves API reales en `.env.example`, README, capturas o código

> **Comando rápido para empaquetar desde Linux/WSL/Git Bash:**
> ```bash
> tar --exclude='frontend/node_modules' \
>     --exclude='frontend/.next' \
>     --exclude='__pycache__' \
>     --exclude='.venv' \
>     --exclude='.env' \
>     --exclude='frontend/.env.local' \
>     -czvf sublitex_deploy.tar.gz .
> ```

---

## 3. Configuración de seguridad en el Servidor

El navegador ya **no** llama directamente a FastAPI ni recibe claves. El frontend
usa rutas server-side (`/api/search` y `/api/health`) que actúan como proxy y
añaden el header `X-API-Key` en el servidor de Next.js. Por eso **no se usa
`NEXT_PUBLIC_API_URL`** ni ninguna variable `NEXT_PUBLIC_*` para secretos.

Crea el archivo `.env` en la raíz del proyecto (nunca lo subas a Git):

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

```dotenv
API_CLIENT_KEY=clave-larga-y-aleatoria-para-clientes
# Opcional: claves por cliente, formato "web:clave,mobile:clave"
API_CLIENT_KEYS=
API_ADMIN_KEY=clave-larga-y-aleatoria-para-indexacion
QDRANT_API_KEY=clave-larga-y-aleatoria-para-qdrant
CORS_ORIGINS=https://TU_DOMINIO_REAL
```

Reglas:

- `API_CLIENT_KEY` (y cada clave de `API_CLIENT_KEYS`) y `API_ADMIN_KEY` deben
  ser **distintas** y secretas.
- `API_ADMIN_KEY` solo se usa para indexación/administración; no la configures
  en el frontend.
- `QDRANT_API_KEY` protege Qdrant y se pasa tanto al contenedor de Qdrant como
  a la API. En modo local sin Docker puede quedar vacía.
- `CORS_ORIGINS` debe listar los orígenes exactos del frontend, separados por
  comas. Nunca uses `*`; en producción usa HTTPS, por ejemplo
  `https://rag.tudominio.com`.
- Si faltan las claves, la API responde `503` en los endpoints protegidos
  (fail-closed), no los deja abiertos.

En `docker-compose.yml`, el frontend recibe la URL interna y la clave de
cliente; el administrador y la clave de Qdrant solo se pasan a los servicios
que los necesitan:

```yaml
  qdrant:
    ports:
      - "127.0.0.1:6333:6333"
      - "127.0.0.1:6334:6334"
    environment:
      - "QDRANT__SERVICE__API_KEY=${QDRANT_API_KEY:?Defina QDRANT_API_KEY en .env}"
    networks: [backend]

  api:
    environment:
      - "QDRANT_API_KEY=${QDRANT_API_KEY:?Defina QDRANT_API_KEY en .env}"
      - "API_CLIENT_KEY=${API_CLIENT_KEY:?Defina API_CLIENT_KEY en .env}"
      - "API_CLIENT_KEYS=${API_CLIENT_KEYS:-}"
      - "API_ADMIN_KEY=${API_ADMIN_KEY:?Defina API_ADMIN_KEY en .env}"
      - "CORS_ORIGINS=${CORS_ORIGINS:?Defina CORS_ORIGINS con el dominio del frontend}"
    networks: [backend, frontend_net]

  frontend:
    environment:
      - API_URL=http://api:8000
      - "API_CLIENT_KEY=${API_CLIENT_KEY:?Defina API_CLIENT_KEY en .env}"
    networks: [frontend_net]
```

Abre al público solo el puerto **3000** (Frontend). El puerto **8000** (API)
debe exponerse únicamente si hay clientes externos que envíen su propia API key;
en caso contrario, restríngelo al proxy/firewall. Qdrant queda en
`127.0.0.1:6333/6334` (no accesible desde internet) y aislado en la red
`backend`, a la que el frontend no tiene acceso. Para administrar Qdrant usa un
túnel SSH o el propio servidor.

---

## 4. Despliegue con Docker Compose

En la carpeta raíz del proyecto dentro del servidor, ejecuta:

```bash
# Desarrollo local/staging: construye y levanta los servicios.
# En producción usa el procedimiento de etiquetas versionadas de abajo.
docker compose up -d --build

# Verificar el estado de los servicios.
docker compose ps
```

En un despliegue de producción, usa etiquetas inmutables por commit para poder
volver a las imágenes anteriores. No reutilices `local` ni ejecutes `docker
image prune` como parte del despliegue.

Antes de migrar una instalación existente a imágenes etiquetadas, conserva las
imágenes actualmente ejecutadas bajo una etiqueta de recuperación y registra
esa etiqueta en el registro de despliegues:

```bash
PREVIOUS_TAG="pre-etiquetado-$(date +%Y%m%d%H%M%S)"
docker image tag "$(docker inspect --format='{{.Image}}' sublitex_api)" "sublitex_api:${PREVIOUS_TAG}"
docker image tag "$(docker inspect --format='{{.Image}}' sublitex_frontend)" "sublitex_frontend:${PREVIOUS_TAG}"
printf 'Rollback inicial: %s\n' "$PREVIOUS_TAG"
```

Para cada versión posterior, registra la etiqueta que está ejecutándose como
`PREVIOUS_TAG`, actualiza el código a un commit limpio y crea las imágenes con
el SHA completo de ese commit:

```bash
export PREVIOUS_TAG="<etiqueta-actual-en-produccion>"
export APP_IMAGE_TAG="$(git rev-parse --verify HEAD)"
docker compose build api frontend
docker compose up -d --no-build --pull never --wait api frontend
docker compose ps
curl -fsS "https://${SITE_ADDRESS}/api/health"
```

Si la comprobación de salud falla, vuelve a desplegar las imágenes que guardaste
con `PREVIOUS_TAG`. No reconstruyas durante el rollback:

```bash
export APP_IMAGE_TAG="$PREVIOUS_TAG"
docker compose up -d --no-build --pull never --wait api frontend
docker compose ps
curl -fsS "https://${SITE_ADDRESS}/api/health"
```

Este procedimiento solo revierte las imágenes de API y frontend. Conserva
`data/`, `qdrant_data/` y los volúmenes nombrados; no uses `down -v` ni borres
volúmenes. Si una versión cambió el esquema o los datos de Qdrant, restaurar la
imagen anterior puede no ser compatible: restaura un snapshot siguiendo la
sección siguiente y valida primero el procedimiento en staging. Mantén las
etiquetas anteriores hasta confirmar la versión nueva y la recuperación; la
prueba operativa del rollback sigue pendiente de Docker/VPS.

Deberás ver los tres contenedores activos:
- `sublitex_qdrant` (Qdrant Vector DB)
- `sublitex_api` (FastAPI)
- `sublitex_frontend` (Next.js)

---

## 5. Inicialización, migración y snapshots de Qdrant

En un volumen vacío, el lifespan de FastAPI crea y valida la colección
`sublitex_fashion_v1` (512 dimensiones, Cosine), y migra automáticamente los
vectores de `data/embeddings.npy` junto con `products.csv` e `ids.npy`. La API
no queda lista si Qdrant no responde, el esquema no coincide o los IDs están
desalineados.

El comando de migración sigue disponible para reindexar manualmente:

```bash
docker exec sublitex_api python scripts/migrar_a_qdrant.py
```

Opcionalmente, define `QDRANT_SNAPSHOT_PATH` en `.env` con una URL `file://`
dentro del volumen de Qdrant, por ejemplo
`file:///qdrant/storage/snapshots/sublitex_fashion_v1/<archivo>.snapshot`.
Compose guarda los snapshots de Qdrant en ese volumen persistente. Créalo con
el cliente Python de Qdrant (por ejemplo, dentro del contenedor API):

```bash
docker exec sublitex_api python -c "from api.qdrant_engine import _get_qdrant; service = _get_qdrant(); print(service.db.client.create_snapshot(service.collection_name).name)"
```

Si la colección aún no existe, el arranque verifica el archivo y solicita a
Qdrant restaurarlo con prioridad `snapshot` antes de crear una colección
vacía. La restauración no sobrescribe una colección que ya existe. Comprueba
el estado con:

```bash
curl -H "X-API-Key: $API_ADMIN_KEY" http://localhost:8000/health/qdrant
```

Los snapshots deben crearse y copiarse al volumen como parte del procedimiento
de backup; `QDRANT_SNAPSHOT_PATH` solo automatiza la recuperación en el arranque.
Valida una restauración en staging antes de usarla como procedimiento de
recuperación de producción.

---

## 6. Monitoreo y Comandos Útiles

- **Ver logs en tiempo real:**
  ```bash
  docker compose logs -f api
  docker compose logs -f frontend
  docker compose logs -f qdrant
  ```
- **Reiniciar servicios:**
  ```bash
  docker compose restart
  ```
- **Detener servicios:**
  ```bash
  docker compose down
  ```
- **Reconstruir tras cambios en código:**
  ```bash
  docker compose up -d --build
  ```
