# WebScraping — RAG Visual

Plataforma de búsqueda visual de camisetas deportivas basada en **embeddings CLIP/OpenCLIP/SigLIP**. El proyecto consolida un catálogo de camisetas (banco **SBX**), normaliza las imágenes, convierte cada una en un vector y expone una API que devuelve el **Top 5 de diseños visualmente más parecidos** a una imagen cargada. Todo se presenta en una interfaz de cliente de la API.

> **Hito 2 — Búsqueda visual robusta:** una camiseta puede encontrarse aunque la consulta no sea idéntica al banco (sin marco, recoloreada, recortada, mockup o persona), y el Top 5 pasa por un reranking visual para que tenga coherencia humana.

> **Frase de validación:** «Una imagen se carga una sola vez, se procesa con un solo modelo, se compara contra un solo índice y los resultados se muestran en una sola interfaz.»

## Flujo del sistema

```text
data/DATA_NEW/  (imágenes nuevas SBX-###-NNNN.png)
        │
[crear_csv_data_new.py] → data/products.csv   (Sala 1: id, proveedor, pagina, imagen, nombre_original, url)
        │
[normalizar_data_new.py] → data/images_normalized/   (copia a JPG, mismo ID, sin tocar originales)
        │
[generar_embeddings.py] → data/embeddings.npy + data/ids.npy   (Sala 4, Hito 1: CLIP, L2, 512 dims)
[generar_indices_comparativos.py] → embeddings_clip/openclip/siglip.npy   (Sala 4, Hito 2)
        │
[FastAPI api/main.py] → POST /search/image (modos) + GET /health   (Sala 3)
        │
[frontend/ Next.js] → sube imagen, Top 5, nombre, imagen, URL, score   (cliente puro de la API)
```

## Requisitos previos

- **Python 3.10+** (probado con 3.13 / 3.14).
- **Node.js 18+** y **npm** (para el frontend Next.js).
- Conexión a internet la ak_2mw3cc9sS6wI7xS3K29qE8ZT4J77Wprimera vez (para descargar los modelos CLIP/OpenCLIP/SigLIP de Hugging Face a `~/.cache/huggingface`).

## Entorno virtual

El proyecto usa un entorno virtual ubicado un nivel arriba del repo:

```bash
# Desde C:\Users\lucia\Downloads\S5\sala-5 (shell fish / Windows)
. ..\.venv\Scripts\activate.fish        # fish
# o:
..\.venv\Scripts\activate               # PowerShell / cmd

# Verificar:
python --version
pip list | grep -iE "fastapi|torch|transformers|uvicorn|opencv|pillow|numpy"
```

> No usar pip del sistema (PEP 668). Siempre activar el venv antes de ejecutar scripts o la API.

## Guía de inicialización del sistema (desde cero)

Si no hay `data/products.csv`, `data/images_normalized/` ni índices, seguir este orden **obligatorio** (Sala 1 → Sala 4 → Sala 3 → frontend):

### Paso 1 — Generar el catálogo (products.csv)

Lee las imágenes de `data/DATA_NEW/` (patrón `SBX-###-NNNN.png`) y crea `data/products.csv`:

```bash
python scripts/crear_csv_data_new.py
```

Salida esperada:

- `data/products.csv` con 284 filas: `id,proveedor,pagina,imagen,nombre_original,url`.
- IDs sin duplicados; columnas exactas del contrato común.

### Paso 2 — Normalizar las imágenes (images_normalized/)

Copia las imágenes de `data/DATA_NEW/` a `data/images_normalized/` convirtiéndolas a JPG con el mismo ID. **No modifica los originales.**

```bash
python scripts/normalizar_data_new.py
```

Salida esperada: `data/images_normalized/SBX-###-NNNN.jpg` (284 imágenes).

### Paso 3 — Generar los embeddings (Hito 1)

Lee `products.csv` en orden, abre cada imagen de `images_normalized/`, genera su vector con CLIP (`openai/clip-vit-base-patch32`), lo normaliza con L2 y guarda:

```bash
python scripts/generar_embeddings.py
```

Salida esperada:

- `data/embeddings.npy` — matriz `(284, 512)` float32, normalizada L2.
- `data/ids.npy` — 284 IDs alineados posición a posición con los embeddings.

> La correspondencia posición ↔ ID es obligatoria: si se altera el orden, el sistema devolvería nombres asociados a la imagen equivocada.

### Paso 4 — Generar índices comparativos (Sala 4, Hito 2)

Genera los tres índices sobre `images_normalized/` (necesarios porque la interfaz usa el modelo `fusion` por defecto):

```bash
python scripts/generar_indices_comparativos.py
```

O solo algunos modelos:

```bash
python scripts/generar_indices_comparativos.py --solo clip openclip
```

Salida esperada:

- `data/embeddings_clip.npy` (284×512)
- `data/embeddings_openclip.npy` (284×512)
- `data/embeddings_siglip.npy` (284×768)

### Paso 5 — Validar el dataset

```bash
python scripts/validate_dataset.py
```

Reporta: registros totales/válidos, IDs duplicados, nombres vacíos, URLs vacías, imágenes faltantes/dañadas y duplicados por hash MD5.

### Paso 6 — Levantar la API (Sala 3)

Antes de arrancar, crea `.env` a partir de `.env.example` y define claves
aleatorias distintas (la API falla cerrado sin ellas):

```bash
cp .env.example .env
python -c "import secrets; print('API_CLIENT_KEY=' + secrets.token_urlsafe(48)); print('API_ADMIN_KEY=' + secrets.token_urlsafe(48))"
```

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Al iniciar carga el índice y el modelo CLIP una sola vez. Endpoints:

- `GET /health` — estado, cantidad de productos/embeddings, modelo y desfase detectado.
- `POST /search/image` — recibe una imagen (multipart) y el `modo` de búsqueda. Devuelve el Top 5 con ID, nombre, imagen, URL, score y metadatos de reranking.

Prueba rápida desde otra terminal:

```bash
curl -X POST -H "X-API-Key: $API_CLIENT_KEY" \
  -F "file=@data/images_normalized/SBX-01-0001.jpg" \
  http://localhost:8000/search/image
```

Verificación de salud:

```bash
curl http://localhost:8000/health
```

Respuesta esperada (ejemplo):

```json
{
  "status": "ok",
  "products": 284,
  "embeddings": 284,
  "model": "openai/clip-vit-base-patch32",
  "desfase_detectado": false,
  "observacion": "..."
}
```

### Paso 7 — Levantar la interfaz (frontend Next.js)

```bash
cd frontend
npm run dev
```

Antes de arrancar, copia `frontend/.env.example` a `frontend/.env.local` y define `API_URL=http://localhost:8000` y `API_CLIENT_KEY` (la misma del backend). Abre `http://localhost:3000`: la app usa el proxy server-side `/api/search`, que añade la clave sin exponerla al navegador, y muestra el Top 5 con imagen, ID, nombre, URL y score.

---

## Carga de datos — actualizar datos existentes y cargar nuevo contenido

Esta sección explica cómo **actualizar el banco ya cargado** o **incorporar nuevas imágenes** sin romper el índice existente.

### Flujo general de carga

```
Nuevas imágenes en data/DATA_NEW/
        │
        ▼
1) crear_csv_data_new.py   →  data/products.csv        (regenera el catálogo completo)
        │
        ▼
2) normalizar_data_new.py  →  data/images_normalized/  (copia a JPG, mismo ID)
        │
        ▼
3) generar_embeddings.py   →  data/embeddings.npy + ids.npy   (reindexa todo)
        │
        ▼
4) generar_indices_comparativos.py   →  embeddings_clip/openclip/siglip.npy
        │
        ▼
5) validate_dataset.py     →  validación de integridad
        │
        ▼
6) Reiniciar la API        →  uvicorn recarga el índice nuevo
```

### Caso A: Cargar un banco completamente nuevo

Si se quiere reemplazar el banco actual (por ejemplo, pasar de SBX a otro proveedor):

1. Poner las nuevas imágenes en `data/DATA_NEW/` con nomenclatura `SBX-###-NNNN.png` (o ajustar el patrón en `crear_csv_data_new.py` si cambia el proveedor).
2. Borrar los derivados antiguos (opcional, los scripts sobrescriben):
   ```bash
   del data\products.csv
   del data\embeddings.npy data\ids.npy
   del data\embeddings_clip.npy data\embeddings_openclip.npy data\embeddings_siglip.npy
   rd /s /q data\images_normalized
   ```
3. Ejecutar los pasos 1 a 6 de la **Guía de inicialización del sistema**.
4. Reiniciar la API para que cargue el nuevo índice.

### Caso B: Actualizar / añadir imágenes al banco existente

1. Añadir las nuevas imágenes PNG a `data/DATA_NEW/` respetando la nomenclatura `SBX-###-NNNN.png` y sin repetir IDs ya existentes.
2. Ejecutar los pasos 1 a 4 (los scripts regeneran todo el catálogo desde `DATA_NEW`, por lo que las imágenes nuevas se incluyen automáticamente).
3. Ejecutar `scripts/validate_dataset.py` para verificar que no hay duplicados ni imágenes dañadas.
4. Reiniciar la API.

### Reglas importantes de carga

- **`products.csv` es la ÚNICA fuente de productos.** Columnas exactas: `id,proveedor,pagina,imagen,nombre_original,url`. El campo `imagen` contiene solo el nombre de archivo (ej. `SBX-01-0001.png`).
- **`ids.npy` debe conservar el MISMO orden que `embeddings.npy`** (posición 0 → id 0, etc.). Siempre validar la alineación al cargar.
- **Nomenclatura de IDs:** `SBX-###-NNNN` (patrón `SBX-\d{2}-\d{4}`).
- **`images_normalized/` es el banco canónico.** Las imágenes originales en `DATA_NEW/` no se modifican ni se borran.
- Los únicos índices permitidos son: `embeddings.npy`, `embeddings_clip.npy`, `embeddings_openclip.npy`, `embeddings_siglip.npy` + `ids.npy`. **Prohibido** crear archivos tipo `index_embeddings.npy`, `embeddings_productos.npy`, `embeddings_final_v2.npy` o rutas duplicadas.

---

## Contrato de respuesta

`POST /search/image` (form-data: `file` + `modo`) devuelve una lista de objetos con al menos:

```json
[
  {
    "id": "SBX-01-0001",
    "nombre": "SBX-01-0001",
    "imagen": "SBX-01-0001.jpg",
    "url": "https://ejemplo.com/SBX-01-0001",
    "proveedor": "SBX",
    "score": 0.82,
    "score_reranking": 0.85,
    "posicion_final": 1,
    "modelo_utilizado": "clip+openclip+siglip"
  }
]
```

`GET /health` devuelve: `status`, `products`, `embeddings`, `model`, `desfase_detectado`, `observacion`.

## Autenticación y CORS

La API usa **API keys con roles** mediante el header `X-API-Key`:

- `API_CLIENT_KEY`: permite búsquedas (`/search/image`, `/search/image/v2`, `/search/image/qdrant`).
- `API_CLIENT_KEYS` (opcional): claves adicionales por cliente con formato `nombre:clave,otro:clave`. Permite identificar integraciones sin compartir una única clave.
- `API_ADMIN_KEY`: permite indexación y administración (`POST /index/qdrant`, `GET /health/qdrant`, `GET /collections/qdrant`). También puede buscar.
- `GET /health` es público para liveness/readiness y no expone secretos.
- Si las claves no están configuradas, los endpoints protegidos responden `503` (fail-closed). Clave ausente o inválida → `401`; clave válida sin rol admin → `403`.
- `QDRANT_API_KEY` protege Qdrant. En Docker, sus puertos quedan en `127.0.0.1` y el frontend no comparte red con Qdrant.

Configurar en `.env` (ver `.env.example`):

```dotenv
API_CLIENT_KEY=...
# Opcional: web:...,mobile:...
API_CLIENT_KEYS=
API_ADMIN_KEY=...
QDRANT_API_KEY=...
# Desarrollo; en producción: https://rag.tudominio.com
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Ejemplo de búsqueda directa:

```bash
curl -X POST http://localhost:8000/search/image \
  -H "X-API-Key: $API_CLIENT_KEY" \
  -F "file=@data/consultas/consulta.jpg" \
  -F "modo=auto" \
  -F "modelo=fusion"
```

`CORS_ORIGINS` solo acepta orígenes explícitos `http://` o `https://`; el valor `*` se ignora. En producción usa únicamente el dominio real con HTTPS, por ejemplo `CORS_ORIGINS=https://rag.tudominio.com`. El frontend Next.js **no** recibe claves en el navegador: usa el proxy server-side `/api/search` y `/api/health`, que añade `X-API-Key` desde `API_CLIENT_KEY` (`frontend/.env.local` en desarrollo).

## Modos del endpoint (Sala 2, Hito 2)

- `auto` / `completo`: prepara la consulta (Sala 2) + motor Hito 2 (reranking).
- `procesada`: imagen preparada + motor Hito 2.
- `clasico`: Hito 1 + preprocesamiento de Sala 2 (sin reranking).
- `original`: Hito 1 con la consulta tal cual llega.
- `legacy`: solo la lista del motor (comportamiento Hito 1).

El parámetro `modelo` (`clip` | `openclip` | `fusion`) se envía junto con `modo`; `fusion` es el recomendado por defecto (CLIP + OpenCLIP + SigLIP).

## Reglas de la evaluación (Hito 2)

- Mínimo 50 consultas: 10 exactas, 10 sin marco, 10 recoloreadas, 10 recortadas, 10 mockups/personas. Cada una con su `id_correcto`.
- Métricas: Top 1 exactitud, Top 5 recuperación y calidad Top 5 humana (Muy similar / Similar / Poco similar / No relacionado).
- Comparación obligatoria Hito 1 vs Hito 2 sobre las MISMAS consultas.
- No llamar al score «porcentaje de coincidencia» ni «confianza»: es un **score de similitud**.

## Manejo de errores obligatorio en la API

La API NO debe cerrarse ante:

- Sin imagen / archivo no válido → 400 `{"error": "El archivo enviado no es una imagen válida"}`.
- Imagen demasiado pequeña (mínimo 32 px por lado) → 400 con mensaje claro.
- Falta `embeddings.npy`, falta `products.csv`, IDs desalineados, modelo no carga → 500 con mensaje, sin matar el servidor.
- Una imagen de un candidato que no puede abrirse: puntuar 0 en visuales, no romper la búsqueda.

## Estructura del proyecto

```text
sala-5/
├── api/                 # FastAPI + motores de búsqueda
│   ├── main.py           #   endpoints /search/image (modos) y /health
│   ├── security.py       #   API keys con roles client/admin y fail-closed
│   ├── search_engine.py  #   motor Hito 1 (embeddings.npy + ids.npy + products.csv)
│   └── search_engine_hito2.py # motor Hito 2 (recuperación amplia + reranking)
├── frontend/            # Next.js (React) cliente puro de la API
│   ├── src/app/api/search/route.ts  # proxy server-side con X-API-Key
│   ├── src/app/api/health/route.ts  # proxy server-side de /health
│   └── ...               #   sube imagen, Top 5, nombre, imagen, URL, score
├── data/
│   ├── DATA_NEW/         # imágenes nuevas SBX-###-NNNN.png (fuente, NO modificar)
│   ├── images_normalized/# banco canónico JPG, mismo ID que products.csv
│   ├── products.csv      # dataset canónico (ÚNICA fuente de productos)
│   ├── embeddings.npy    # vectores CLIP (Hito 1)
│   ├── embeddings_clip.npy      # vectores CLIP sobre images_normalized (Sala 4, Hito 2)
│   ├── embeddings_openclip.npy  # vectores OpenCLIP sobre images_normalized (Sala 4, Hito 2)
│   ├── embeddings_siglip.npy    # vectores SigLIP 768d sobre images_normalized (Sala 4, Hito 2)
│   ├── ids.npy           # IDs alineados con embeddings
│   ├── evaluation.csv    # resultado de evaluaciones
│   └── tiempos.csv       # tiempo de generación de índices
├── scripts/              # crear_csv_data_new, normalizar_data_new, generar_embeddings,
│   │                     # generar_indices_comparativos, validate_dataset, etc.
├── evaluation/           # plan de pruebas y consultas de evaluación
├── requirements.txt      # dependencias Python
├── .env / .env.example   # configuración de entorno
├── AGENTS.md             # reglas de trabajo para la IA
├── TRABAJO.md            # consigna oficial del proyecto
├── README.md             # este documento
└── main.py               # runner del scraper (legacy, no usado en el flujo actual)
```

## Archivos generados clave

| Archivo                          | Contenido                                                                    |
| -------------------------------- | ---------------------------------------------------------------------------- |
| `data/products.csv`            | 284 filas: `id, proveedor, pagina, imagen, nombre_original, url`           |
| `data/embeddings.npy`          | Matriz `(284, 512)` float32, normalizada L2 (CLIP, Hito 1)                 |
| `data/embeddings_clip.npy`     | Matriz `(284, 512)` CLIP sobre `images_normalized/` (Sala 4, Hito 2)     |
| `data/embeddings_openclip.npy` | Matriz `(284, 512)` OpenCLIP sobre `images_normalized/` (Sala 4, Hito 2) |
| `data/embeddings_siglip.npy`   | Matriz `(284, 768)` SigLIP sobre `images_normalized/` (Sala 4, Hito 2)   |
| `data/ids.npy`                 | 284 IDs en el mismo orden que los embeddings                                 |
| `data/images_normalized/`      | 284 imágenes normalizadas `SBX-###-NNNN.jpg`                              |
| `data/tiempos.csv`             | Tiempo de generación por modelo (Sala 4, Hito 2)                            |
| `data/evaluation.csv`          | Evaluación de consultas (Sala 2)                                            |

## Solución de problemas

- **`ModuleNotFoundError`**: activar el venv (`. ..\.venv\Scripts\activate.fish`) e instalar dependencias (`pip install -r requirements.txt`).
- **La API no responde en `/health`**: verificar que esté corriendo (`uvicorn api.main:app --host 0.0.0.0 --port 8000`).
- **`401` / `403` al buscar**: falta el header `X-API-Key` o la clave no tiene el rol requerido. El frontend debe usar el proxy `/api/search` con `API_CLIENT_KEY` configurada en `frontend/.env.local`.
- **`503` en endpoints protegidos**: faltan
  `API_CLIENT_KEY`/`API_CLIENT_KEYS` o `API_ADMIN_KEY` en el entorno del
  servidor, o `QDRANT_API_KEY` al usar Docker/Qdrant remoto. El sistema falla
  cerrado por seguridad.
- **El validador reporta imágenes faltantes**: asegurar de haber corrido `normalizar_data_new.py` (el validador apunta a `data/images_normalized/`).
- **Errores de codificación en consola (Windows)**: usar `set PYTHONIOENCODING=utf-8` antes de ejecutar.
- **Primera ejecución lenta**: la descarga de los modelos CLIP/OpenCLIP/SigLIP y el procesamiento de las 284 imágenes toma unos minutos.
- **IDs desalineados**: volver a ejecutar `generar_embeddings.py` y `generar_indices_comparativos.py` en ese orden; `ids.npy` se regenera alineado con `products.csv`.

## Próximos pasos

- Completar el plan de evaluación de 50 consultas en `evaluation/`.
- Migrar el índice a PostgreSQL + pgvector (o FAISS/Qdrant) para persistencia, filtros y concurrencia al escalar.
- Fase siguiente del RAG: usar un LLM con los resultados recuperados para proponer nombres y etiquetas.
