# Guía de Despliegue en Servidor de Producción (RAG Sublitex)

Esta guía detalla el procedimiento estándar para verificar, transferir, configurar y levantar el sistema RAG (FastAPI + Qdrant + Next.js) en un servidor de producción (VPS, AWS, GCP, DigitalOcean, etc.).

---

## 1. Verificación Previa Local (Opcional pero Recomendado)

Antes de realizar la migración al servidor, confirma que los contenedores locales respondan:

1. **Abrir en navegador:**
   - **Frontend (UI):** [http://localhost:3000](http://localhost:3000)
   - **Swagger API:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Panel Qdrant:** [http://localhost:6333/dashboard](http://localhost:6333/dashboard)
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

> **Comando rápido para empaquetar desde Linux/WSL/Git Bash:**
> ```bash
> tar --exclude='frontend/node_modules' \
>     --exclude='frontend/.next' \
>     --exclude='__pycache__' \
>     --exclude='.venv' \
>     -czvf sublitex_deploy.tar.gz .
> ```

---

## 3. Configuración en el Servidor (IP Pública o Dominio)

En producción, los navegadores de los clientes se comunican directamente con la API. Por lo tanto, la variable `NEXT_PUBLIC_API_URL` debe apuntar a la dirección accesible por internet del servidor.

Edita `docker-compose.yml` en el servidor:

```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: sublitex_frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - ./data/images_normalized:/data/images_normalized:ro
    environment:
      # Reemplaza con la IP pública o dominio de tu servidor:
      - NEXT_PUBLIC_API_URL=http://TU_IP_O_DOMINIO:8000
    depends_on:
      - api
```

Asegúrate también de que los puertos **3000** (Frontend), **8000** (API) y opcionalmente **6333** (Qdrant) estén permitidos en el Firewall / Security Group del proveedor cloud.

---

## 4. Despliegue con Docker Compose

En la carpeta raíz del proyecto dentro del servidor, ejecuta:

```bash
# 1. Construir imágenes y levantar servicios en segundo plano
docker compose up -d --build

# 2. Verificar que los 3 contenedores estén arriba (status Up)
docker compose ps
```

Deberás ver los tres contenedores activos:
- `sublitex_qdrant` (Qdrant Vector DB)
- `sublitex_api` (FastAPI)
- `sublitex_frontend` (Next.js)

---

## 5. Poblado e Indexación en Qdrant (Solo la primera vez)

Una vez que los contenedores estén corriendo, ejecuta la migración de vectores dentro del contenedor de la API:

```bash
docker exec -it sublitex_api python scripts/migrar_a_qdrant.py
```

Este script:
1. Crea la colección `sublitex_fashion_v1` si no existe.
2. Carga los metadatos desde `data/products.csv`.
3. Sube los 284 vectores CLIP desde `data/embeddings.npy`.

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
