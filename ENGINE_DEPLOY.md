# ENGINE_DEPLOY.md — Auditoría técnica y evaluación de plataformas de despliegue del motor RAG-V2

> **Fecha de elaboración:** 2026-10-14 · **Rama auditada:** `sala-5` (commit `d91399d9`).
> **Alcance:** exclusivamente el motor RAG (API FastAPI + pipeline de visión + Qdrant). La interfaz web actual (Next.js) se documenta solo como componente prescindible. Todos los precios y límites de plataforma se consultaron el **2026-10-14** en la documentación oficial de cada proveedor (enlaces en la sección H). Las cifras marcadas como **[estimación]** no son precios confirmados y requieren las mediciones indicadas.

---

## A. Resumen ejecutivo

**Qué se está desplegando.** Un motor de búsqueda visual por imagen de camisetas deportivas: una API HTTP (FastAPI) que recibe una imagen, la segmenta (YOLOv8n ONNX), elimina el fondo (rembg/U2-Net), genera un embedding de 768 dimensiones con SigLIP (`google/siglip-base-patch16-224`, ejecutándose localmente en CPU), busca los 30 vectores más cercanos en Qdrant con filtro de color, y aplica un reranking visual (histogramas HSV, estructura y descriptores precomputados) para devolver Top-5 (`api/main.py`, `api/search_engine.py`, `api/search_engine_hito2.py`). **No hay ningún modelo de lenguaje (LLM) en el camino de ejecución actual**; `prompts/country_identification.py` existe como preparación para una integración futura con LLM, pero no está conectado.

**Cómo está construido.** Python 3.10 (imagen base `python:3.10-slim` en `api/Dockerfile:2`), FastAPI + uvicorn, modelos de IA cargados en memoria al arranque (`lifespan` en `api/main.py:8-13`), y Qdrant en modo **embebido local** (archivo `qdrant_data/collection/*/storage.sqlite`, 69 MB) con soporte opcional de servidor Qdrant vía variable `QDRANT_URL` (`core/base_datos.py:13-16`). El estado persistente necesario en runtime es pequeño (~230 MB: índice Qdrant + imágenes normalizadas del banco + `descriptores.json`), pero **debe sobrevivir a los reinicios** y los modelos deben cargarse en cada arranque.

**Requisitos que condicionan el despliegue (confirmados por código):**

1. **Runtime pesado en arranque:** torch + transformers + SigLIP (~86 M parámetros) + rembg (descarga U2-Net en el primer uso) + ultralytics/YOLO. Cada arranque carga modelos desde disco; un *cold start* no es «arrancar un script», es montar un stack de ML **[estimación: 20–90 s, requiere medición]**.
2. **Memoria:** el stack torch + SigLIP + OpenCV difícilmente cabe en 512 MB. La base mínima creíble es **2 GB de RAM**, y 4 GB es el tamaño prudente **[estimación, requiere medición con `psutil`/`/usr/bin/time` en el contenedor]**. Esto descarta de entrada los planes «free» de Render (512 MB) y Railway (0,5 GB).
3. **Almacenamiento persistente:** `qdrant_data/` (69 MB), `data/imagenes_normalized/` (110 MB, leído en cada consulta para el reranking con caché en memoria, `api/search_engine_hito2.py:132-137`) y `data/descriptores.json` (49 MB) deben montarse en un volumen o disco persistente. **Un volumen efímero pierde el índice Qdrant al reiniciar.**
4. **Estado local incompatible con escalado horizontal:** el Qdrant embebido usa un lock de archivo (`qdrant_data/.lock`) y un solo escritor; escalar a N réplicas exige migrar a Qdrant en modo servidor (`QDRANT_URL` ya está soportado) o Qdrant Cloud.
5. **Sin autenticación y CORS abierto:** `api/main.py:18-24` configura `allow_origins=["*"]` junto a `allow_credentials=True` y no hay ninguna API key. Cualquier sitio podría llamar al motor. Esto debe corregirse antes de exponerlo a internet (sección E).
6. **Dockerfile desactualizado:** `api/Dockerfile:17` instala un subconjunto obsoleto (`fastapi uvicorn pydantic numpy faiss-cpu opencv...`) que **no incluye torch, transformers, qdrant-client, rembg, ultralytics ni scikit-learn**, todos importados en runtime. Tal imagen fallaría al arrancar. Además `requirements.txt` omite `rembg`, `ultralytics` y `scikit-learn`. Esto debe corregirse antes de cualquier despliegue (riesgo F-1).

**Qué debe ofrecer la infraestructura:** soporte de Docker con imagen de 3–6 GB **[estimación del tamaño de imagen con torch CPU]**, 2–4 GB RAM, disco persistente ≥ 1 GB, proceso de larga duración (no funciones efímeras por invocación), HTTPS con dominio propio, variables de entorno para secretos, y despliegue por Git o CLI. GPU **no se necesita hoy** (todo corre en CPU; `core/vision_pipeline.py:42` usa CUDA solo si está disponible).

**Recomendación final (condicionada):** como plataforma principal para el escenario demo/producción pequeña, **Railway (plan Hobby)** por su soporte nativo de Docker, volúmenes persistentes, facturación por segundo y simplicidad de despliegue (~US$35–60/mes según tamaño, sección G). Como alternativa de mínima para un prototipo controlado, **Render plan Standard (1 vCPU / 2 GB, US$25/mes + disco)** o **Hetzner (VPS CX23, ~€6/mes)** si se acepta administración propia. **Ninguna plataforma free tier sirve para este motor en la práctica**: los planes gratuitos quedan por debajo del mínimo de RAM o no ofrecen disco persistente. La recomendación es válida mientras (1) los modelos sigan ejecutándose localmente en CPU, (2) la carga sea de una decena de consultas concurrentes como máximo, y (3) el índice permanezca por debajo de ~1 M de vectores; los cambios que invalidan esta recomendación se detallan en G.

---

## B. Arquitectura y requisitos del motor

### B.1 Inventario y criterios de exclusión

**Revisados (evidencia citada):** `api/` (main.py, search_engine.py, search_engine_hito2.py, descriptores_visuales.py, preprocesar_consulta.py, Dockerfile, __init__.py), `core/` (vision_pipeline.py, base_datos.py, search_service.py, config.py, sublitex.py, database_sql.py, cdr_seguridad.py, compound_segmentation.py, adaptador_imagenes.py), `config/settings.py`, `requirements.txt`, `docker-compose.yml`, `.gitignore`, `.streamlit/config.toml`, `prompts/`, `tests/`, listados de `data/`, `qdrant_data/`, `scripts/` (cabeceras de `indexar_banco_propio.py`, `precomputar_descriptores.py` y requirements de scripts), `README.md`, `DECISIONES.md` (estructura), `AGENTS.md`, `main.py` (raíz), y `frontend/src` solo para identificar el contrato de integración (grep de endpoints).

**Excluidos con justificación:**
- **Binarios y artefactos de datos** (`data/*.npy`, `data/descriptores.json`, `yolov8n.onnx` 12,8 MB, `qdrant_data/**/*.sqlite` 69 MB, `data/imagenes_normalized/` 110 MB): solo se inspeccionaron tamaños y nombres, no contenido; aportan tamaño y persistencia, no lógica.
- **`frontend/` completo (Next.js, 452 KB de código):** es el entorno de evaluación descartable para el despliegue del motor; solo se extrajo qué endpoints consume.
- **`CONSULTAS/`, `evaluation/`, `docs/`, `TRABAJO.md`, reportes de hitos:** documentación académica/evaluación, no runtime.
- **`scraper/`, `utils/`, `storage/`, `main.py` (raíz):** pipeline de extracción de catálogo offline; no forma parte del motor en ejecución.
- **Generación de `__pycache__`, venvs, `.git`:** artefactos generados sin información relevante (regla de inspección 8).

### B.2 Tabla de componentes

| N.º | Componente | Tecnología detectada | Función | Requisito de despliegue | Evidencia |
|---:|---|---|---|---|---|
| 1 | API HTTP | FastAPI + uvicorn, Python 3.10 | Recibe imagen (multipart) y devuelve Top-5 JSON; `/health` de estado | Contenedor Docker, puerto 8000, proceso de larga duración | `api/main.py:28-49`, `api/Dockerfile:2,23`, `README.md:116` |
| 2 | Arranque del motor | `lifespan` de FastAPI | Carga VisionPipeline + Qdrant una vez al arranque | Memoria suficiente para todos los modelos residentes | `api/main.py:8-13`, `api/search_engine.py:25-46` |
| 3 | Segmentación | YOLOv8n en ONNX (12,8 MB en repo; fallback `yolov8n.pt`) | Detecta persona y recorta el torso (65 % superior) | El archivo `yolov8n.onnx` debe incluirse en la imagen o volumen | `core/vision_pipeline.py:26-33,52-102` |
| 4 | Remoción de fondo | rembg (U2-Net) con fallback | Aísla la prenda; U2-Net se descarga en primer uso | Red en el primer arranque o pre-descarga en build; caché persistente recomendada | `core/vision_pipeline.py:6,90-102` |
| 5 | Embeddings | SigLIP `google/siglip-base-patch16-224` (768 dim, `core/base_datos.py:38`) | Vector semántico de la imagen; inferencia local CPU (GPU opcional) | Descarga desde Hugging Face Hub en primer arranque (~350 MB de pesos **[estimación]**) o bake en imagen; 2+ GB RAM | `core/vision_pipeline.py:35-47` |
| 6 | Almacén vectorial | Qdrant (qdrant-client ≥1.9): embebido local o servidor por `QDRANT_URL` | Colección `banco_propio_v1`, HNSW `on_disk=True`, índice de payload `color` | **Disco persistente** para `qdrant_data/`; migración a modo servidor para escalar horizontalmente | `core/base_datos.py:13-51`, `api/search_engine.py:23-36` |
| 7 | Búsqueda híbrida | Filtro exacto de color + fallback vectorial puro | Recupera 30 candidatos para el reranking | Sin requisitos adicionales (CPU) | `core/search_service.py:6-42`, `api/search_engine.py:64-65` |
| 8 | Reranking visual | Histogramas HSV globales y por regiones, estructura 32×32, descriptores k-means | Reordena el Top-30 → Top-5 | Lectura de `data/imagenes_normalized/` (110 MB) y `data/descriptores.json` (49 MB) en cada consulta; **ambos en almacenamiento persistente**; caché en RAM por proceso | `api/search_engine_hito2.py:16-60,132-156` |
| 9 | Ingesta de documentos/índice | `scripts/indexar_banco_propio.py` (batch offline) | Indexa el banco de imágenes en Qdrant (upsert, re-ejecutable) | Se ejecuta **fuera del servidor** (el Qdrant local bloquea la carpeta mientras uvicorn corre) | `scripts/indexar_banco_propio.py:1-27` |
| 10 | Configuración | pydantic-settings + `.env` | `QDRANT_URL`, `QDRANT_API_KEY`, rutas | Secretos vía variables de entorno del proveedor; `.env` está en `.gitignore` | `core/config.py:7-28`, `.gitignore` |
| 11 | Seguridad actual | CORS `allow_origins=["*"]` + `allow_credentials=True`, sin auth | — | **Déficit:** endurecer antes de producción (sección E) | `api/main.py:17-24` |
| 12 | Dependencias de sistema | libgl1, libglib2.0-0 (OpenCV) | Runtime de OpenCV en Debian slim | Mantener en el Dockerfile definitivo | `api/Dockerfile:7-10` |
| 13 | Interfaz actual (prescindible) | Next.js (frontend/), Streamlit leftover (.streamlit/) | Evaluación experta; consume `/search/image` y `/health` | **Excluir del despliegue del motor** | `frontend/src/lib/api.ts:7,30`, `docker-compose.yml:17-28` |

### B.3 Confirmado vs. hipótesis

**Confirmado por código:** endpoint único `POST /search/image` + `GET /health`; modelos locales en CPU con GPU opcional; Qdrant embebido con ruta de servidor opcional; reranking que lee el banco de imágenes en cada consulta; ingesta solo por script offline; sin autenticación; CORS totalmente abierto; dependencias faltantes en `requirements.txt` y `api/Dockerfile`.

**Hipótesis que requieren medición (y su impacto en la elección de plataforma):**
- **RAM real del proceso:** medir con el contenedor sirviendo 1 y 10 consultas concurrentes (`/usr/bin/time -v` o métricas del proveedor). Si supera 2 GB, el plan Render Standard queda descartado y se necesita ≥ 4 GB.
- **Tiempo de arranque y cold start:** cronometrar desde `docker run` hasta `/health == ok` descargando y sin descargar modelos. Si supera 60 s, los planes con *scale-to-zero* (Cloud Run, Azure ACA, espacios gratuitos HF) son inviables para uso interactivo sin un volumen de caché de modelos.
- **Latencia por consulta:** medir P50/P95 de `/search/image` en CPU; determina la concurrencia útil por instancia y si hace falta más de una réplica.
- **Crecimiento del índice:** 131 imágenes hoy (colección local con 69 MB en `storage.sqlite`); estimar el techo en ~1 M de vectores 768-dim ≈ 4 GB **[estimación basada en la capacidad declarada por Qdrant Cloud para 1 GB/4 GB, sección H]**.

---

## C. Tabla comparativa de plataformas

Plataformas evaluadas contra el perfil real del motor: contenedor Docker, Python 3.10 + torch CPU, 2–4 GB RAM, ~230 MB de disco persistente (+ modelos), proceso siempre encendido deseable, sin GPU hoy.

| N.º | Plataforma y enlace oficial | Modalidad de precios | Características relevantes | Diferencias entre planes | Puntos fuertes | Defectos y limitaciones | Compatibilidad con RAG-V2 |
|---:|---|---|---|---|---|---|---|
| 1 | [Render](https://render.com/pricing) · [docs despliegue](https://render.com/docs/service-types) · [plan free](https://render.com/docs/free) · [compute plans](https://render.com/docs/compute-plans) | Gratuito y de pago | Docker o Git; web services, workers, cron; discos persistentes US$0,25/GB-mes; TLS y dominio incluidos | Free: 0,1 vCPU/512 MB, 750 h/mes, se duerme a los 15 min (~1 min en despertar), **sin discos persistentes**; Starter US$7 (0,5 vCPU/512 MB); Standard US$25 (1 vCPU/2 GB); Pro US$85 (2 vCPU/4 GB); autoscaling requiere workspace Pro (+US$25/mes); egress US$0,15/GB sobre 5 GB (Hobby) | Despliegue desde Git muy simple; discos persistentes desde el plan de pago; planes intermedios bien dimensionados | Free inservible para torch (512 MB, sin disco); 2 GB puede quedarse corto en RAM **[estimación]**; región principal en EE. UU./Europa (sin Sudamérica) | **Compatible (pago).** Free descartado por RAM y ausencia de volumen |
| 2 | [Railway](https://railway.com/pricing) · [docs planes](https://docs.railway.com/pricing/plans) | Gratuito (limitado) y de pago | Docker nativo; volúmenes; facturación por segundo; Git/CLI | Free: US$1/mes de crédito, máx 1 vCPU/0,5 GB y volumen 0,5 GB (insuficiente); Trial: US$5 únicos/30 días; Hobby US$5 (hasta 48 vCPU/48 GB, volumen 5 GB); tarifas: US$20/vCPU-mes, US$10/GB-mes, volumen US$0,15/GB-mes, egress US$0,05/GB | Modelo de costes lineal y predecible; volúmenes desde Hobby; despliegue en minutos | Sin plan gratuito real para este motor (0,5 GB máx); sin Sudamérica; el volumen Hobby limita a 5 GB | **Compatible.** Free descartado (RAM); Hobby es la opción PaaS más equilibrada |
| 3 | [Hugging Face Spaces](https://huggingface.co/pricing) · [docs Spaces](https://huggingface.co/docs/hub/spaces-overview) · [almacenamiento](https://huggingface.co/docs/hub/spaces-storage) | Gratuito y de pago | Docker Spaces; CPU Basic 2 vCPU/16 GB gratis; GPU on-demand (T4 desde US$0,40/h); ZeroGPU gratuito con cuota | **Crear un Space Docker/Gradio sobre compute requiere plan de pago (PRO/Team)**; cuentas gratuitas solo pueden alojar hasta 2 Gradio Spaces con ZeroGPU; CPU Basic duerme tras ~48 h inactivo; disco 50 GB efímero; almacenamiento persistente: 20 GB US$5/mes, 150 GB US$25/mes; facturación por minuto en ejecución | Es el mejor free tier en recursos (16 GB RAM gratis) y el más barato para demos de ML; GPU barata si algún día se necesita | Requiere plan de pago para crear el Space Docker; la suspensión por inactividad y el disco efímero castigan al motor; no es infraestructura de producción | **Parcial:** excelente vitrina/demo con plan pago; pobre para servicio continuo por sleep y disco efímero |
| 4 | [Fly.io](https://fly.io/pricing) · [docs pricing](https://docs.fly.io/about/pricing) | De pago (trial limitado) | Machines (VMs Firecracker) por segundo; volúmenes US$0,15/GB-mes; región **GRU (São Paulo)** con multiplicador ×1,615 | Sin free tier para organizaciones nuevas (desde jul-2024); trial 3 h de máquina o 7 días; shared-cpu-1x 2 GB ≈ US$17,55/mes (iad) o ≈ US$28 (GRU **[estimación por multiplicador]**); performance-1x 2 GB US$33/mes (iad) | La única plataforma evaluada con región en Sudamérica (baja latencia para usuarios de Argentina/Brasil); control de VM casi total; volúmenes baratos | Sin tier gratuito; precios de la región GRU ~60 % más caros; egress Sudamérica US$0,04/GB | **Compatible.** Buena elección si la latencia regional prima sobre el coste |
| 5 | [Google Cloud Run](https://cloud.google.com/run/pricing) · [free tier](https://docs.cloud.google.com/free/docs/free-cloud-features) · [billing](https://cloud.google.com/run/docs/configuring/billing-settings) | Gratuito (condiciones) y de pago | Contenedores serverless; *always free*: 180 000 vCPU-s + 360 000 GiB-s + 2 M peticiones/mes; facturación por segundo; GPU L4 opcional (US$0,0001867/s) | Free tier equivale a ~50 h/mes de 1 vCPU **[cálculo: 180000/3600]**; con facturación por instancia (min 1) una 1 vCPU/4 GiB siempre activa ≈ US$67/mes **[estimación: 0,000018×2,59 us-de-s + 0,000002×4×2,59]**; request-based cobraría cada arranque del contenedor | Free tier genuino y permanente; autoscaling fino; la gama de precios es la más granular del mercado | Cada arranque en frío recarga 4+ GB de modelos (inviable para uso interactivo sin min-instance, que cobra 24×7); región us-central1 a ~100+ ms de Argentina; requiere cuenta con tarjeta | **Compatible (de pago).** El free tier solo sirve para pruebas esporádicas |
| 6 | [AWS App Runner](https://aws.amazon.com/apprunner/pricing/) · [autoscaling](https://docs.aws.amazon.com/apprunner/latest/dg/manage-autoscaling.html) | De pago | Contenedores gestionados con HTTPS; escalado por concurrencia | **Sin free tier** (comparativa oficial AWS); activo US$0,064/vCPU-h + US$0,007/GB-h; memoria provisionada (inactiva) también US$0,007/GB-h; 1 vCPU/4 GB siempre activa ≈ US$67/mes **[estimación]**; máx 4 vCPU/12 GB por instancia | Gestionado completamente (TLS, balanceo); escalado horizontal trivial | Sin tier gratuito; la memoria inactiva se cobra siempre; sin GPU; el máximo de 12 GB por instancia limita el crecimiento | **Compatible**, pero sin ventaja diferencial frente a Cloud Run para este caso |
| 7 | [Azure Container Apps](https://azure.microsoft.com/en-us/pricing/details/container-apps/) · [billing](https://learn.microsoft.com/en-us/azure/container-apps/billing) | Gratuito (condiciones) y de pago | Contenedores serverless; free grant idéntico a Cloud Run (180 000 vCPU-s, 360 000 GiB-s, 2 M req/mes); perfiles de carga con GPU serverless (T4/A100) | Consumption: máx 4 vCPU/8 GiB por réplica; tarifa activa ≈ US$0,000024/vCPU-s (región central US) con tarifa reducida en inactividad; Brasil Sur disponible en perfiles Flex **[ver regiones en consola]**; GPU serverless con cuota por región | Mismo modelo free-tier que GCP; presencia en Brasil Sur; ruta a GPU gestionada si hiciera falta | Configuración más verbosa que Railway/Render; free tier cubre poco con modelos residentes; la memoria efímera por réplica compite con los modelos cargados | **Compatible.** Interesante si ya se es cliente Azure o si Brasil Sur es requisito |
| 8 | [Hetzner Cloud](https://www.hetzner.com/cloud/) · [ajuste de precios 2026](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | De pago | VPS con Docker completo; facturación por hora con tope mensual | Sin free tier; CX23 (2 vCPU/4 GB/40 GB) €5,49 + IPv4 €0,50 + IVA (stock limitado a 2026-10); CPX22 (igual spec) €19,49; 20 TB de tráfico incluido en UE; ubicaciones: Alemania/Finlandia/EE. UU./Singapur (**sin Sudamérica**) | Coste mínimo absoluto para recursos suficientes (4 GB de RAM reales); sin límites artificiales de peticiones; disco y red sin techo práctico | Administración 100 % propia (backup, seguridad, actualizaciones); disponibilidad de los planes CX limitada; latencia UE ~200 ms a Argentina | **Compatible (VPS).** La opción más barata si se acepta operar el servidor |
| 9 | [Qdrant Cloud](https://qdrant.tech/pricing/) · [crear clúster](https://qdrant.tech/documentation/cloud/create-cluster/) | Gratuito y de pago | Base de datos vectorial gestionada (sustituye al Qdrant embebido) | Free: 1 nodo, 0,5 vCPU/1 GB RAM/4 GB disco (~1 M vectores 768-dim), **se suspende tras 1 semana de inactividad y se borra tras 4 semanas**; Standard: consumo por hora (vCPU+RAM+disco), SLA 99,5 % | Elimina el disco local del índice y habilita escalado horizontal del motor; free tier suficiente para el catálogo actual | Añade latencia de red y segundo componente a operar; el free tier se borra por inactividad | **Complemento opcional**, no plataforma de hosting: relevante cuando el motor pase a múltiples réplicas |

**Plataformas excluidas y motivo:** AWS Lambda y Google Cloud Functions — el arranque cargaría ~4 GB de modelos por invocación en frío (latencia y coste prohibitivos; el motor mantiene estado residente). Vast.ai/RunPod — GPUs spot para entrenamiento/inferencia intensiva; el motor no necesita GPU hoy. WordPress.com / Envato — ver sección 6 (categoria incorrecta, no son infraestructura de ejecución Python).

---

## D. Evaluación económica

**Supuestos comunes:** región de referencia para usuarios en Argentina; motor con 2 vCPU y 4 GB RAM (redondeando al alza el requisito mínimo de 2 GB por la hipótesis de RAM sin medir); volumen persistente de 1 GB (índice 69 MB + imágenes 110 MB + descriptores 49 MB + margen); ~10 000 peticiones/mes en escenarios demo; tráfico de imágenes salientes despreciable (los resultados devuelven metadatos y nombres de archivo, no binarios). Los importes en USD salvo indicación. **Todos los totales son estimaciones construidas con tarifas oficiales; no son precios cerrados.**

### Escenario 1 — Prototipo / pruebas con poca carga
- **Railway Free:** US$0, pero máx 1 vCPU/0,5 GB → insuficiente (B-3). **No viable.**
- **Render Free:** 512 MB sin disco persistente → pierde el índice en cada reinicio y no carga torch. **No viable.**
- **Hugging Face Spaces CPU Basic:** 2 vCPU/16 GB gratis, pero crear el Space Docker requiere plan de pago (PRO, precio no verificado en esta investigación) **y** el disco es efímero salvo compra de persistencia (20 GB → US$5/mes). Coste mínimo real: **plan PRO + persistencia ≈ US$5/mes + precio del plan PRO [estimación]**.
- **Cloud Run / Azure ACA (free tier):** ~50 h/mes de 1 vCPU cubiertas gratis; viable solo para saquetes de pruebas, no para uso interactivo (cada arranque = carga completa de modelos).
- **Coste creíble mínimo del prototipo:** Railway Hobby con 1 vCPU/2 GB: US$5 (suscripción, incluye US$5 de uso) + ~US$40 de uso (1×20 + 2×10) − US$5 de crédito ≈ **US$40/mes** [estimación con tarifas de C].

### Escenario 2 — Demo / desarrollo con disponibilidad razonable (siempre activo)
- **Railway Hobby**, 1 vCPU/2 GB + 1 GB de volumen: ≈ US$40 de uso + 0,15 de volumen ≈ **US$40/mes** [estimación]. Con 2 vCPU/2 GB: ≈ **US$60/mes**.
- **Render Standard (1c-2g)** en workspace Hobby + 1 GB de disco: US$25 + 0,25 ≈ **US$25,25/mes** (tarifa oficial). Riesgo: 2 GB puede ser justo (B-3); si hace falta 2c-4g sube a **US$85 + disco**.
- **Hetzner CX23** (2 vCPU/4 GB): ≈ **€6–7/mes + IVA** si hay stock (sino CPX22 €19,49); más backup opcional (20 % del precio del servidor).

### Escenario 3 — Producción con concurrencia y persistencia
- **Railway Hobby** 2 vCPU/4 GB: 2×20 + 4×10 = **US$80/mes** + volumen ≈ US$0,15 [estimación]; hasta 6 réplicas si se escala (cada una se factura aparte).
- **Render** 2c-4g: **US$85/mes** + disco; autoscaling solo con workspace Pro (+US$25/mes).
- **Cloud Run** instancia mínima 1 vCPU/2 GiB con facturación por instancia: 0,000018×2 592 000 s ≈ US$46,66 + memoria 0,000002×2×2 592 000 ≈ US$10,37 → ≈ **US$57/mes por instancia** [estimación]; escala por peticiones; Cloud Storage (~US$0,02/GB-mes) para la caché de modelos.
- **Hetzner CX33** (4 vCPU/8 GB): ≈ **€9–10/mes + IVA** con administración propia.
- **Base de datos vectorial gestionada (Qdrant Cloud Standard):** se suma solo al migrar a modo servidor; el tier Free cubre el catálogo actual (1 GB/4 GB) con el riesgo de borrado por inactividad.

### Escenario 4 — Procesamiento local de embeddings (situación actual)
Ya es local (SigLIP en CPU): su coste está **incluido en el compute** de los escenarios anteriores. No se paga inferencia externa. Si se optara por inferencia gestionada (p. ej. embeddings vía API o Qdrant Cloud Inference), el coste pasaría a ser por token/vector y se eliminaría la mayor parte de la RAM del motor — cambio de arquitectura, no incluido aquí.

### Escenario 5 — Futura búsqueda visual avanzada
Si la búsqueda visual agrega modelos (p. ej. re-identificación de producto, embeddings más grandes, o almacenamiento de imágenes del catálogo consultado): +2–8 GB de RAM (→ planes de 4–8 GB: Railway ~US$100–160/mes **[estimación]**, Render 4c-8g US$175) y volumen adicional (imagen del catálogo a ~1 GB ≈ +US$0,15–0,25/mes). Solo si se exigiera GPU local: Cloud Run con L4 ≈ US$575/mes por GPU continua **[estimación: 0,0001867×2 592 000]**; antes de llegar ahí conviene revisar cuantización/distilación.

**Fórmula general para cualquier plataforma de consumo:** `coste/mes ≈ n_vCPU × tarifa_vCPU + RAM_GB × tarifa_GB + GB_volumen × tarifa_GB-disco + egress_GB × tarifa_red`, con los valores de la tabla C.

---

## E. Integración con la futura website

### Capacidades actuales (confirmadas)
- **Contrato HTTP:** `POST /search/image` acepta `multipart/form-data` con `file` (imagen) y devuelve JSON `{color_detectado, resultados:[{id, nombre, imagen, url, proveedor, score}], modo, modelo}` (`api/main.py:28-45`, `api/search_engine.py:91-94`). `GET /health` da estado (`api/main.py:47-49`). La website actual ya consume exactamente esos dos endpoints (`frontend/src/lib/api.ts:7,30`) — el contrato es funcional para una búsqueda visual por imagen.
- **CORS:** abierto a `*` con credenciales (`api/main.py:18-24`).
- **Auth:** inexistente.

### Recomendaciones de arquitectura (no implementadas en esta tarea)
1. **API key o JWT:** añadir middleware de autenticación (p. ej. cabecera `X-API-Key` validada contra secreto de entorno) antes de exponer el motor; la website backend debe ser el único portador de la clave (no exponerla en JavaScript del navegador).
2. **CORS restringido:** reemplazar `allow_origins=["*"]` por el dominio explícito de la nueva website; eliminar `allow_credentials=True` si no se usan cookies.
3. **Contrato y errores:** estandarizar errores JSON con códigos (400 imagen inválida, 413 tamaño máximo, 503 motor no listo) y añadir límite de tamaño de subida; hoy `Image.open` puede lanzar excepciones no controladas ante archivos corruptos (`api/main.py:36`).
4. **Timeouts y concurrencia:** la inferencia es CPU-bound y bloquea el event loop de uvicorn en un solo worker; para producción, uvicorn con workers múltiples **no es posible con Qdrant embebido** (un solo proceso puede abrir el lock). La ruta correcta es migrar a `QDRANT_URL` (ya soportado, `core/config.py:13-14`) y escalar workers/réplicas; o acceptar baja concurrencia con un solo proceso.
5. **Persistencia e indexación:** la ingesta actual es un script offline que exige parar el servidor (`scripts/indexar_banco_propio.py:22-24`). Para un catálogo vivo, la arquitectura futura debería exponer un endpoint de ingesta autenticado (el motor ya tiene `ingest_to_qdrant`, `api/search_engine.py:96-113`, sin usar por la API) o ejecutar el script como job planificado con el Qdrant en modo servidor.
6. **Búsqueda visual futura:** el motor ya es «búsqueda por imagen»; una nueva website con búsqueda visual solo necesita: formulario de subida → `POST /search/image` → pintar resultados. Si se desean miniaturas, servirlas desde el almacenamiento de imágenes de la website (hoy el motor devuelve `url: ""`, `api/search_engine.py:76`), no desde el motor. Si en el futuro se indexan imágenes nuevas o se usa un modelo multimodal mayor, reaparecen los requisitos de RAM/volumen del escenario D-5.
7. **Latencia:** mantener el motor en región cercana a los usuarios (Fly.io GRU o Azure Brasil Sur son las únicas opciones regionalizadas evaluadas); de lo contrario ~100–250 ms de ida y vuelta adicionales a EE. UU./UE, tolerables para una consulta visual de 1–3 s **[estimación de latencia de red, sin medición]**.

---

## F. Riesgos y limitaciones

| ID | Riesgo | Impacto | Mitigación |
|---|---|---|---|
| F-1 | `requirements.txt` y `api/Dockerfile` no incluyen todas las dependencias reales (torch, transformers, qdrant-client, rembg, ultralytics, scikit-learn); la imagen Docker actual **fallaría al arrancar** | Bloqueante para cualquier despliegue | Regenerar el Dockerfile desde `requirements.txt` completo + libgl1/libglib2, y añadir las dependencias faltantes antes de desplegar |
| F-2 | Cold start de 20–90 s **[estimación]** cargando modelos en cada arranque | Experiencia de usuario rota en plataformas con scale-to-zero o sleep | Evitar planes que se duermen (Render Free, HF CPU Basic, Cloud Run sin min-instance); o montar caché persistente de modelos Hugging Face |
| F-3 | Volumen efímero = pérdida del índice Qdrant y de `descriptores.json` | El motor arranca vacío o directamente falla | Exigir disco persistente (Render paid disk, Railway volume, Fly volume, VPS); validar montaje en el plan de despliegue |
| F-4 | RAM sin medir; torch+SigLIP podría superar 2 GB | OOM kill en planes justos | Medir antes de contratar (B-3); elegir 4 GB como tamaño inicial prudente |
| F-5 | Qdrant embebido: un solo proceso, lock de archivo, sin escalar horizontalmente | Cuello de botella bajo concurrencia; no se pueden usar múltiples workers | Migrar a Qdrant servidor (variable ya soportada) o Qdrant Cloud al crecer |
| F-6 | Endpoints sin autenticación y CORS `*` | Uso/abuso del motor por terceros; consumo de recursos | API key + CORS restringido antes de exponer (sección E) |
| F-7 | Costes sorpresa: planes «free» que cobran por excedentes (Render egress US$0,15/GB; Railway cobro por uso excedente; facturación por segundo 24/7 en HF/Cloud Run) | Facturas inesperadas | Configurar límites de gasto/alertas del proveedor; revisar consumo la primera semana (Railway lo recomienda oficialmente) |
| F-8 | Dependencia de Hugging Face Hub en el primer arranque (descarga de SigLIP y U2-Net) | Arranque fallido si el proveedor bloquea la red o hay rate-limit | Pre-descargar los pesos en el build (Docker) o caché persistente |
| F-9 | Sin región en Sudamérica en la mayoría de plataformas (Render, Railway, Hetzner, HF) | +100–250 ms por consulta para usuarios de Argentina | Fly.io (GRU) o Azure Brasil Sur si la latencia es crítica |
| F-10 | Necesidad futura de GPU o modelo multimodal mayor | Coste ×10 (p. ej. L4 continua ≈ US$575/mes **[estimación]**) | Presupuestar solo tras medir; explorar cuantización y modelos distilados antes |
| F-11 | La ingesta solo existe como script offline que exige parar el servidor | Catálogos vivos no actualizables sin downtime | Qdrant en modo servidor + endpoint de ingesta autenticado (arquitectura futura) |
| F-12 | Precios y límites de plataforma cambian con frecuencia (Hetzner subió 30–175 % en jun-2026; Render renombró planes en ago-2026) | Presupuestos desactualizados | Verificar en las fuentes de H el día del despliegue |

---

## G. Recomendación final

### Plataforma principal: Railway — plan Hobby

1. **Compatibilidad técnica:** despliegue Docker nativo (el motor ya se define con `docker-compose.yml` y Dockerfile), volúmenes persistentes desde el plan Hobby (5 GB, suficiente para los ~230 MB actuales + margen), y hasta 48 GB de RAM disponibles si el motor crece. No impone límites de ejecución ni se duerme por inactividad en planes de pago.
2. **Recursos:** 2 vCPU/2–4 GB se cubren con holgura; facturación por segundo (solo se paga el tiempo encendido) y coste lineal: US$20/vCPU-mes + US$10/GB-mes.
3. **Persistencia:** volumen de disco persistente montado en `qdrant_data/` y `data/` — exactamente lo que el motor necesita (riesgo F-3).
4. **Coste:** ~US$40/mes (1 vCPU/2 GB) a ~US$80/mes (2 vCPU/4 GB) todo incluido de compute; volumen y egress aparte. Sin cargos ocultos de plataforma más allá de la suscripción de US$5 (que se descuenta del consumo).
5. **Despliegue y mantenimiento:** despliegue por Git o CLI, variables de entorno y secretos en dashboard, rollbacks; la operación se reduce a publicar el contenedor y montar el volumen.
6. **Disponibilidad y escalado:** sin sleep (sin cold starts); réplicas hasta 6 en Hobby; escala vertical sin migrar de plataforma.
7. **Integración:** endpoint HTTPS público con dominio propio y secretos por entorno; con la API key de la sección E, la nueva website se conecta sin tocar el motor.
8. **Riesgos aceptables:** F-1 (corregible en el repo antes de desplegar), F-4 (mitigable eligiendo 4 GB), F-5 (mitigable con `QDRANT_URL` cuando haya concurrencia real). Sin región sudamericana (F-9) — tolerable si la latencia de ~150–250 ms es aceptable.

### Alternativa A (mínima económica): Render — plan Standard (1c-2g, US$25/mes)
La opción PaaS más barata con disco persistente. Válida **solo si la medición confirma que el motor cabe en 2 GB de RAM** (B-3/F-4); si no, el plan siguiente (2c-4g) cuesta US$85/mes y Railway gana en relación recursos/precio.

### Alternativa B (mínima absoluta y control total): Hetzner VPS CX23 (~€6/mes + IVA)
4 GB de RAM reales por el menor precio de todos. Contrapartida: administrar SO, Docker, firewall, backups y actualizaciones manualmente; sin Sudamérica; stock de los planes CX limitado (verificado sin disponibilidad el 2026-10-14; el plan CPX22 alternativo cuesta €19,49).

### Cuándo cambiaría esta recomendación
- **Si los embeddings salen de un proveedor externo** (API en la nube) en vez de SigLIP local: el motor se vuelve ligero (<512 MB) y entonces Cloud Run/Azure ACA con free tier y scale-to-zero se vuelven la mejor opción por coste.
- **Si se necesita GPU local** (modelo multimodal mayor): HF Spaces con GPU (T4 US$0,40/h) para experimentar, o Cloud Run/Azure con GPU gestionada para producción — con un coste de infraestructura un orden de magnitud mayor.
- **Si la carga supera la decena de consultas concurrentes** o el índice pasa de ~1 M de vectores: migrar Qdrant a modo servidor (Qdrant Cloud o autoalojado) y escalar réplicas; Railway o Fly.io siguen sirviendo como capa de cómputo.
- **Si la latencia sudamericana es crítica:** Fly.io región GRU (≈ ×1,615 sobre precios de Ashburn) o Azure Brasil Sur.

---

## H. Fuentes consultadas

Todas las URLs se consultaron el **2026-10-14**.

**Render**
- Precios: https://render.com/pricing
- Planes de cómputo: https://render.com/docs/compute-plans · https://render.com/docs/compute-plans-update
- Plan gratuito y sus límites: https://render.com/docs/free
- Tipos de servicio: https://render.com/docs/service-types
- Características por plan: https://render.com/docs/platform-features-by-plan
- FAQ (cold start de instancias free): https://render.com/docs/faq

**Railway**
- Precios y planes: https://railway.com/pricing · https://docs.railway.com/pricing/plans
- Trial gratuito: https://docs.railway.com/pricing/free-trial
- Facturación: https://docs.railway.com/pricing/understanding-your-bill

**Hugging Face Spaces**
- Precios y hardware: https://huggingface.co/pricing
- Overview de Spaces (restricción de planes para Docker/Gradio): https://huggingface.co/docs/hub/spaces-overview
- Almacenamiento persistente: https://huggingface.co/docs/hub/spaces-storage
- ZeroGPU (cuotas): https://huggingface.co/docs/hub/spaces-zerogpu
- GPU Spaces (suspensión por inactividad): https://huggingface.co/docs/hub/spaces-gpus

**Fly.io**
- Precios: https://fly.io/pricing · https://docs.fly.io/about/pricing (incluye tabla de multiplicadores por región, `gru` ×1,615)
- Facturación: https://docs.fly.io/about/billing
- Gestión de costes: https://docs.fly.io/about/cost-management

**Google Cloud Run**
- Precios y free tier: https://cloud.google.com/run/pricing
- Free tier general: https://docs.cloud.google.com/free/docs/free-cloud-features
- Facturación por petición vs. por instancia: https://cloud.google.com/run/docs/configuring/billing-settings

**AWS**
- App Runner precios: https://aws.amazon.com/apprunner/pricing/
- Comparación App Runner vs. Fargate (afirma ausencia de free tier): https://aws.amazon.com/compare/app-runner-and-fargate/
- Autoscaling: https://docs.aws.amazon.com/apprunner/latest/dg/manage-autoscaling.html

**Azure**
- Container Apps precios y free grant: https://azure.microsoft.com/en-us/pricing/details/container-apps/
- Facturación: https://learn.microsoft.com/en-us/azure/container-apps/billing
- Perfiles de carga (GPU serverless, regiones): https://learn.microsoft.com/en-us/azure/container-apps/workload-profiles-overview

**Hetzner**
- Ajuste de precios (15-06-2026): https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/
- Cloud: https://www.hetzner.com/cloud/ · https://www.hetzner.com/european-cloud/

**Qdrant Cloud**
- Precios y free tier: https://qdrant.tech/pricing/ · https://qdrant.tech/cloud/
- Crear clúster (suspendión/borrado por inactividad): https://qdrant.tech/documentation/cloud/create-cluster/

**Servicios externos del motor**
- Hugging Face Hub — modelo SigLIP: https://huggingface.co/google/siglip-base-patch16-224
- Qdrant (documentación técnica del motor de búsqueda): https://qdrant.tech/documentation/

**Documentación del proyecto (repositorio local)**
- `README.md`, `DECISIONES.md`, `AGENTS.md`, y los archivos citados en la tabla B.2.

---

*Documento generado por auditoría estática del código (sin ejecución de scripts, sin modificación de archivos del motor). Las mediciones de RAM/latencia señaladas como pendientes condicionan la elección final del plan exacto dentro de la plataforma recomendada.*
