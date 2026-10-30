# AGENTS.md — Reglas de trabajo para la IA en este repositorio

> La IA DEBE leer este archivo al inicio de cada sesión y seguirlo.
> La consigna histórica está en `TRABAJO.md`; si ese archivo no está presente,
> usar `README.md`, `PRODUCCION_SERVER.md` y este `AGENTS.md` como referencia.
> No inventar requisitos que no estén en el código o en la documentación.

## 1. Objetivo del proyecto

Motor de búsqueda visual para camisetas deportivas del catálogo **SBX**:

1. El usuario sube una imagen de consulta.
2. Uno o varios modelos generan embeddings visuales.
3. El motor busca en el índice correspondiente.
4. La API devuelve el Top 5 con ID, nombre, imagen, URL, proveedor y score.
5. El frontend Next.js muestra los resultados y permite comparar modelos.

El proyecto tiene dos hitos técnicos:

- **Hito 1:** búsqueda directa por similitud coseno con CLIP.
- **Hito 2:** recuperación amplia + reranking visual + umbral dinámico, con
  CLIP, OpenCLIP o fusión de CLIP + OpenCLIP + SigLIP.

Frase de validación del Hito 1: «Una imagen se carga una sola vez, se procesa
con un solo modelo, se compara contra un solo índice y los resultados se
muestran en una sola interfaz.» El Hito 2 amplía esa frase: usa tres modelos y
varios índices, pero conserva una sola interfaz y un solo contrato de salida.

## 2. Estructura canónica (NO crear copias ni rutas alternativas)

```text
proyecto/
├── api/
│   ├── main.py                  # API FastAPI y endpoints
│   ├── search_engine.py         # motor Hito 1 (embeddings.npy + ids.npy + products.csv)
│   ├── search_engine_hito2.py   # motor Hito 2 (recuperación amplia + reranking)
│   ├── qdrant_engine.py         # motor Qdrant (endpoints paralelos)
│   ├── preprocesar_consulta.py  # Sala 2: rembg/GrabCut + normalización de consulta
│   └── descriptores_visuales.py # color, estructura, patrón, marco, franjas
├── core/
│   ├── config.py                # settings y variables de entorno
│   ├── base_datos.py            # cliente Qdrant
│   ├── qdrant_service.py        # servicio de alto nivel Qdrant
│   └── search_service.py        # búsqueda híbrida vector + color
├── data/
│   ├── DATA_NEW/                # PNG originales del banco (NO modificar)
│   ├── images_normalized/       # banco canónico JPG (284 imágenes)
│   ├── products.csv             # ÚNICA fuente de productos
│   ├── ids.npy                  # IDs alineados con los embeddings
│   ├── embeddings.npy           # Hito 1: CLIP, 284 x 512
│   ├── embeddings_clip.npy      # Hito 2: CLIP, 284 x 512
│   ├── embeddings_openclip.npy  # Hito 2: OpenCLIP, 284 x 512
│   ├── embeddings_siglip.npy    # Hito 2: SigLIP, 284 x 768
│   ├── consultas/               # imágenes de evaluación
│   ├── queries_original/        # consultas guardadas por la API (generado)
│   ├── queries_procesadas/      # consultas procesadas por la API (generado)
│   ├── comparacion_hito1_hito2.csv
│   └── tiempos.csv
├── frontend/                    # Next.js (React), cliente puro de la API
│   ├── src/app/search/          # pantalla de búsqueda
│   ├── src/app/api/images/      # proxy de imágenes del catálogo
│   ├── src/lib/api.ts           # llamadas a FastAPI
│   ├── Dockerfile
│   └── package.json
├── evaluation/                  # consultas de evaluación
├── scripts/                     # creación de CSV, normalización, índices, evaluación
├── Dockerfile.api               # imagen de FastAPI
├── docker-compose.yml           # Qdrant + API + frontend
├── requirements.txt
├── README.md
└── PRODUCCION_SERVER.md
```

El frontend es **Next.js**. No crear una segunda interfaz ni un cliente
paralelo que genere embeddings o busque localmente.

### Archivos de índice permitidos

Los únicos índices vectoriales permitidos son:

- `data/embeddings.npy` (Hito 1, CLIP)
- `data/embeddings_clip.npy` (Hito 2, CLIP)
- `data/embeddings_openclip.npy` (Hito 2, OpenCLIP)
- `data/embeddings_siglip.npy` (Hito 2, SigLIP)
- `data/ids.npy` (alineado posición a posición)

PROHIBIDO crear `index_embeddings.npy`, `embeddings_productos.npy`,
`embeddings_final_v2.npy`, `embeddings_v3.npy` o cualquier duplicado.
Si hace falta un índice nuevo, se justifica y se agrega a esta lista; no se
crea por conveniencia.

## 3. Contrato de datos

- `data/products.csv` con columnas exactas:
  `id,proveedor,pagina,imagen,nombre_original,url`.
- Catálogo actual: **284 productos**, proveedor **SBX**, IDs con patrón
  `SBX-##-NNNN` (ej. `SBX-01-0001`, `SBX-05-0040`).
- `imagen` contiene SOLO el nombre de archivo. En el CSV actual figura como
  `.png`; el banco canónico `images_normalized/` está en `.jpg`. Los motores y
  el frontend resuelven el equivalente `<id>.jpg`; no cambiar esa tolerancia
  sin migrar todos los datos.
- `nombre_original` actualmente coincide con el ID. Para producción deben ser
  nombres comerciales reales; no asumir que el ID es el nombre final.
- Las URLs actuales son de ejemplo (`https://ejemplo.com/...`). No usarlas
  como evidencia de un catálogo real.
- `images_normalized/` es el banco canónico de búsqueda. `DATA_NEW/` contiene
  los originales y **no se modifica ni se borra**.
- `ids.npy` debe conservar el MISMO orden que `embeddings.npy`
  (posición 0 → id 0, etc.). Validar la alineación al cargar.
- `frontend/src/lib/catalog.ts` es una copia de presentación para la UI. La
  fuente de verdad para búsqueda y metadatos sigue siendo `products.csv`; no
  agregar productos solo en el frontend.

## 4. Modelos, índices y motores

### Modelos de embeddings

| Clave | Modelo | Dimensión | Uso |
|---|---|---:|---|
| `clip` | `openai/clip-vit-base-patch32` | 512 | Hito 1 y Hito 2 |
| `openclip` | `laion/CLIP-ViT-B-32-laion2B-s34B-b79K` | 512 | Hito 2 |
| `siglip` | `google/siglip-base-patch16-224` | 768 | Solo dentro de `fusion` |

`MODELOS_VALIDOS` en `api/main.py` es `("clip", "openclip", "fusion")`.
**SigLIP no se puede pedir solo**: únicamente se usa cuando `modelo=fusion`.
`fusion` no es un cuarto modelo; combina los tres.

### Motores

- **Hito 1 — `api/search_engine.py`:** carga `embeddings.npy` + `ids.npy` +
  `products.csv`, normaliza L2 y devuelve el Top 5 por producto punto. No
  aplica reranking.
- **Hito 2 — `api/search_engine_hito2.py`:** carga el índice normalizado del
  modelo (`embeddings_clip/openclip/siglip.npy`), recupera candidatos amplios
  y los reordena con color HSV, estructura, color dominante, gama, patrón,
  marco y franjas. Usa umbral absoluto y margen relativo; puede devolver
  **0 a 5 resultados**, no rellena.
- **Qdrant — `api/qdrant_engine.py` + `core/`:** colección
  `sublitex_fashion_v1`, vectores de 512 dimensiones. Hoy solo indexa CLIP
  (`data/embeddings.npy`) y **no aplica el reranking del Hito 2**.

### Relación actual entre motores

- El endpoint principal `POST /search/image` usa los motores `.npy`
  (Hito 1 / Hito 2). **No usa Qdrant.**
- Qdrant se usa solo en los endpoints `/search/image/qdrant`, `/index/qdrant`,
  `/health/qdrant` y `/collections/qdrant`.
- El Hito 2 con `clip` usa 30 candidatos; con `openclip`, 30; con `fusion`,
  200 (`CANDIDATOS_INICIALES_FUSION`).
- `embeddings.npy` y `embeddings_clip.npy` son actualmente idénticos
  (284 × 512). Son dos rutas por compatibilidad de hitos; no crear una tercera
  copia del mismo CLIP.
- Para que Qdrant reemplace al Hito 2 hace falta indexar OpenCLIP y SigLIP
  (vectores nombrados o colecciones separadas) y agregar el reranking. Hoy no
  está implementado; no documentarlo como si lo estuviera.

## 5. API

### `POST /search/image`

Form-data:

- `file`: JPG/PNG de la consulta.
- `modo`: `auto`, `completo`, `procesada`, `clasico`, `original` o `legacy`.
- `modelo`: `clip`, `openclip` o `fusion`.

Devuelve un OBJETO, no una lista:

```json
{
  "query_id": "q_20261029_140958_849483",
  "modo": "completo",
  "modelo": "openai/clip-vit-base-patch32",
  "preprocesamiento": {
    "ok": true,
    "pasos": ["..."],
    "backend": "rembg",
    "bbox": [0, 0, 320, 320],
    "recorte_pct": 0.12,
    "tiempo_segundos": 1.31
  },
  "tiempo_segundos": 4.8,
  "imagen_original_b64": "...",
  "imagen_procesada_b64": "...",
  "resultados": [
    {
      "id": "SBX-01-0001",
      "nombre": "SBX-01-0001",
      "imagen": "SBX-01-0001.png",
      "url": "https://ejemplo.com/SBX-01-0001",
      "proveedor": "SBX",
      "score": 0.82,
      "score_reranking": 0.85,
      "posicion_final": 1,
      "modelo_utilizado": "clip+color+estructura+patron+marco+franjas"
    }
  ],
  "resultados_original": null,
  "resultados_procesada": null
}
```

`resultados_original` y `resultados_procesada` solo se calculan en modo `clip`
para comparar Hito 1. En los demás modos quedan en `null`.

### `POST /search/image/v2`

Recibe `file` y `modelo`, y devuelve:

```json
{
  "resultados": [],
  "tiempo_segundos": 0.0,
  "candidatos_evaluados": 30,
  "modelo": "openai/clip-vit-base-patch32"
}
```

Es el endpoint directo del Hito 2, sin el preprocesamiento de Sala 2.

### Endpoints Qdrant

- `GET /health/qdrant`
- `GET /collections/qdrant`
- `POST /index/qdrant` (indexa `products.csv` + `embeddings.npy`; no protege
  autenticación, no exponerlo públicamente)
- `POST /search/image/qdrant` (`file`, `top_k`, `color_filtro`, `min_score`,
  `modelo`)

### `GET /health`

Devuelve:

- `status`
- `products`
- `embeddings`
- `model`
- `desfase_detectado`
- `observacion`
- `modelo_openclip`
- `indice_openclip_ok`
- `modelos_fusion`

## 6. Modos y modelos

| `modo` | Preprocesa | Motor | Modelos permitidos |
|---|---|---|---|
| `auto` / `completo` | Sí | Hito 2 + reranking | `clip`, `openclip`, `fusion` |
| `procesada` | Sí | Hito 2 + reranking | `clip`, `openclip`, `fusion` |
| `clasico` | Sí | Hito 1, sin reranking | Solo `clip` |
| `original` | No | Hito 1, sin reranking | Solo `clip` |
| `legacy` | No | Hito 1, respuesta simple | Solo `clip` |

- `openclip` y `fusion` solo aplican a `auto`, `completo` y `procesada`.
  Si se envían con `clasico`, `original` o `legacy`, la API responde 400.
- El frontend envía `modo=auto` y por defecto `modelo=fusion`
  (`frontend/src/app/search/page.tsx`). `fusion` es el modo más pesado en CPU;
  para demo local o pruebas rápidas usar `clip`. No cambiar ese default sin
  medir latencia y calidad.
- El score es un **score de similitud**, no un porcentaje de coincidencia ni
  una probabilidad/confianza.

## 7. Evaluación (Hito 2)

- Mínimo 50 consultas: 10 exactas, 10 sin marco, 10 recoloreadas, 10
  recortadas y 10 mockups/personas.
- Cada consulta debe tener su `id_correcto`.
- Métricas: Top 1 exactitud, Top 5 recuperación y calidad Top 5 humana
  (Muy similar / Similar / Poco similar / No relacionado).
- Comparación obligatoria Hito 1 vs Hito 2 sobre las MISMAS consultas.
- Scripts de referencia:
  - `scripts/evaluar_50_consultas.py`
  - `scripts/compare_hito1_hito2.py`
  - `evaluation/consultas_hito2.csv`
- Salidas esperadas:
  - `data/comparacion_hito1_hito2.csv`
  - `data/comparacion_hito1_hito2.json`
  - `data/tiempos.csv`
- `evaluation/consultas_hito2.csv` actual usa rutas con `\` de Windows. Si se
  ejecuta en Linux, normalizar las rutas antes de confiar en los resultados.
- No llamar al score «porcentaje de coincidencia» ni «confianza».

## 8. Manejo de errores obligatorio en la API

La API NO debe cerrarse ante:

- Sin imagen / archivo no válido → 400
  `{"error": "El archivo enviado no es una imagen válida"}`.
- Imagen demasiado pequeña (mínimo 32 px por lado) → 400 con mensaje claro.
- Modelo desconocido → 400 con la lista de modelos válidos.
- `openclip`/`fusion` en un modo Hito 1 → 400 explicando que solo aplican al
  Hito 2.
- Falta `embeddings.npy`, falta `products.csv`, IDs desalineados o modelo que
  no carga → 500 con mensaje, sin matar el servidor.
- Qdrant caído: el endpoint Qdrant responde 500, pero el endpoint principal
  basado en `.npy` debe seguir funcionando.
- Una imagen de un candidato que no puede abrirse: puntuar 0 en visuales, no
  romper la búsqueda.

## 9. Flujo de trabajo estándar para cada tarea

1. Leer este archivo y, si existe, `TRABAJO.md`.
2. Explorar el código existente ANTES de modificar; buscar patrones, no asumir.
3. Implementar en la estructura canónica, sin duplicar motores ni índices.
4. Verificar:
   - `python -m py_compile` de los archivos Python tocados.
   - `node --check` no aplica a TS/TSX; en frontend usar `npm run lint`.
   - `npm run build` si se tocó el frontend.
   - Probar la API con una imagen real:
     `curl -X POST -F "file=@data/images_normalized/SBX-01-0001.jpg" http://localhost:8000/search/image`
5. Si se tocó Docker y `docker compose` está disponible, validar
   `docker compose config` y levantar los servicios.
6. Actualizar `AI_LOG.md` solo si existe y el usuario lo pide. No crear ni
   modificar otros `.md` sin autorización.
7. NO commitear a menos que lo pida el usuario explícitamente.

## 10. Entorno local (Linux/Arch, shell fish)

- No usar `pip` del sistema (PEP 668). Usar el venv del proyecto:
  `source .venv/bin/activate.fish`.
- API:
  `uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload`.
- Frontend:
  `cd frontend && npm run dev`.
- URLs locales:
  - Frontend: `http://localhost:3000`
  - API/Swagger: `http://localhost:8000/docs`
  - Qdrant local (si se levanta): `http://localhost:6333/dashboard`
- El torch instalado es CPU (sin NVIDIA). No reinstalar CUDA.
- Si falta espacio al instalar, usar `TMPDIR=/var/tmp` (el disco tiene más
  espacio que `/tmp`).
- La primera ejecución puede tardar por descarga de modelos de Hugging Face y
  del modelo de `rembg`/U2-Net. No confundir esa descarga con un cuelgue.
- `data/queries_original/` y `data/queries_procesadas/` las genera la API.
  No borrarlas sin preguntar: son evidencia de consultas.

## 11. Docker

> En este host el CLI de Docker no tiene el plugin `compose`; los comandos de
> esta sección se ejecutan en el servidor o después de instalar
> `docker-compose-plugin`. No asumir que `docker compose` funciona localmente.

### Servicios de `docker-compose.yml`

| Servicio | Contenedor | Imagen/build | Puertos | Volúmenes |
|---|---|---|---|---|
| `qdrant` | `sublitex_qdrant` | `qdrant/qdrant:latest` | `6333:6333`, `6334:6334` | `./qdrant_data:/qdrant/storage` |
| `api` | `sublitex_api` | build `Dockerfile.api` | `8000:8000` | `./data:/app/data`, `./qdrant_data:/app/qdrant_data` |
| `frontend` | `sublitex_frontend` | build `frontend/Dockerfile` | `3000:3000` | `./data/images_normalized:/data/images_normalized:ro` |

Variables del servicio `api`:

- `QDRANT_URL=http://qdrant:6333`
- `QDRANT_COLLECTION_NAME=sublitex_fashion_v1`
- `API_HOST=0.0.0.0`
- `API_PORT=8000`
- `CATALOG_PATH=/app/data/images_normalized`

El servicio `frontend` define `NEXT_PUBLIC_API_URL=http://localhost:8000`.
Ese valor es el que usa el **navegador**, no el contenedor: para un servidor
remoto debe ser la IP o el dominio públicos.

### Comandos estándar

```bash
# Construir y levantar todo
docker compose up -d --build

# Ver estado
docker compose ps

# Logs
docker compose logs -f api
docker compose logs -f frontend
docker compose logs -f qdrant

# Reiniciar / detener
docker compose restart
docker compose down

# Reconstruir tras cambios de código
docker compose up -d --build
```

### Poblado de Qdrant (primera vez o tras recrear `qdrant_data/`)

`qdrant_data/` está en `.gitignore`; un despliegue limpio arranca con Qdrant
vacío. La API principal sigue funcionando con `.npy`, pero los endpoints
Qdrant no tendrán vectores hasta ejecutar:

```bash
docker exec -it sublitex_api python scripts/migrar_a_qdrant.py
```

Ese script:

1. Crea la colección `sublitex_fashion_v1` si no existe.
2. Carga `data/products.csv`.
3. Indexa los **284 vectores CLIP** de `data/embeddings.npy`.

Opciones útiles:

```bash
docker exec -it sublitex_api python scripts/migrar_a_qdrant.py --recrear
docker exec -it sublitex_api python scripts/migrar_a_qdrant.py --coleccion otra_coleccion
```

Limitación actual: la migración **solo indexa CLIP**. No indexa OpenCLIP ni
SigLIP y no aplica el reranking del Hito 2. No presentar Qdrant como
equivalente completo del motor Hito 2.

### Verificación y salud

`docker-compose.yml` **no define bloques `healthcheck`**. Verificar con:

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/health/qdrant
curl -s http://localhost:8000/collections/qdrant
curl -s http://localhost:6333/dashboard
```

Comprobaciones mínimas:

- `GET /health` responde 200, `products=284`, `embeddings=284`,
  `desfase_detectado=false`.
- `GET /health/qdrant` responde 200 y muestra puntos (284 si se migró).
- `POST /search/image` con una imagen real devuelve 200 y Top 5 coherente.
- Archivo inválido → 400; imagen <32 px → 400.
- El frontend en `:3000` llama a la API pública correcta, no a `localhost`
  desde el navegador del usuario.

`depends_on` solo ordena el arranque; no espera a que Qdrant o los modelos
estén listos. El `lifespan` de la API tolera que Qdrant falle, pero el motor
`.npy` sí necesita `products.csv`, `embeddings.npy` e `ids.npy`.

### Variables de entorno

- Copiar `.env.example` a `.env` y ajustar.
- `QDRANT_URL` vacío = Qdrant en modo local por path
  (`QDRANT_DATA_PATH=./qdrant_data`). En Compose se usa `http://qdrant:6333`.
- `QDRANT_COLLECTION_NAME` debe coincidir con la colección migrada.
- `NEXT_PUBLIC_API_URL` se inlinea en tiempo de **build** de Next.js. Cambiarla
  solo en `environment` de Compose no cambia el bundle ya compilado. Para
  producción hay que pasarla como build arg/`ENV` antes de `npm run build` y
  reconstruir la imagen del frontend.
- No dejar secretos dentro de la imagen. `Dockerfile.api` hace `COPY .env*`;
  revisar que no se hornee un `.env` real con credenciales.

### Limitaciones actuales del build Docker

- No hay `.dockerignore` en la raíz ni en `frontend/`; el contexto puede
  incluir `.venv`, `node_modules`, `data` y `.git`.
- `frontend/package-lock.json` no existe; el Dockerfile usa `npm install`, no
  `npm ci`.
- `requirements.txt` usa versiones `>=` y contiene dependencias no usadas por
  el flujo actual (por ejemplo, librerías de UI heredadas y `ultralytics`).
- `Dockerfile.api` instala `torch` desde PyPI; en Linux puede resolver una
  wheel CUDA aunque el entorno sea CPU.
- No hay volumen para el caché de Hugging Face ni para U2-Net; al recrear el
  contenedor se pueden volver a descargar los modelos.
- `qdrant/qdrant:latest` no está pineado.
- No hay reverse proxy/TLS ni autenticación. No exponer `3000`, `8000`,
  `6333` o `6334` directamente a Internet sin resolverlo.

## 12. Estado actual conocido (no asumir otra cosa)

- Catálogo: **284 productos**, **284 imágenes** en `images_normalized/`.
- `products.csv`: 284 filas, proveedor `SBX`, IDs únicos, URLs de ejemplo,
  `imagen` con extensión `.png`.
- Índices: `embeddings.npy` y `embeddings_clip.npy` son idénticos
  (284 × 512); `embeddings_openclip.npy` es 284 × 512;
  `embeddings_siglip.npy` es 284 × 768.
- `data/descriptores.json` **no existe** actualmente. El reranking calcula
  descriptores on-the-fly y los cachea por proceso; la primera consulta es
  más lenta. Existe `scripts/precomputar_descriptores.py` para precomputarlos.
- Qdrant local: colección `sublitex_fashion_v1` con 284 puntos de 512
  dimensiones (solo CLIP).
- El endpoint principal no usa Qdrant; Qdrant está en endpoints paralelos.
- El frontend usa `fusion` por defecto. En CPU es el modo más lento; `clip`
  es la opción rápida para demo.
- `README.md` y `PRODUCCION_SERVER.md` pueden estar desactualizados en algunos
  detalles. Validar siempre contra el código y este archivo.

## 13. Comandos de mantenimiento

```bash
# Crear products.csv desde DATA_NEW/
python scripts/crear_csv_data_new.py

# Normalizar a JPG en images_normalized/
python scripts/normalizar_data_new.py

# Hito 1: embeddings.npy + ids.npy
python scripts/generar_embeddings.py

# Hito 2: embeddings_clip/openclip/siglip.npy
python scripts/generar_indices_comparativos.py

# Opcional: descriptores visuales precomputados
python scripts/precomputar_descriptores.py

# Migrar CLIP a Qdrant
python scripts/migrar_a_qdrant.py

# Comparar Hito 1 vs Hito 2 (requiere API corriendo)
python scripts/compare_hito1_hito2.py

# Evaluación de 50 consultas (requiere API corriendo)
python scripts/evaluar_50_consultas.py
```

Reglas de mantenimiento:

- Si se agregan productos, actualizar `products.csv` y regenerar **todos** los
  índices; no mezclar índices viejos con un CSV nuevo.
- Si se regenera un índice, validar que `ids.npy` siga alineado.
- Si se cambia la extensión de `imagen` en el CSV, migrar también las imágenes
  y el resolvedor del frontend.
- Si se toca el reranking, correr la comparación Hito 1 vs Hito 2 y revisar
  Top 1/Top 5 antes de dar por buena la mejora.
