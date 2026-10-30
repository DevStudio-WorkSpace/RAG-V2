# Requerimientos y permisos para desplegar — RAG Visual Sublitex

**Fecha:** 2026-10-29  
**Alcance:** auditoría del repositorio `RAG-V2` (FastAPI + Next.js + Qdrant) para determinar qué debe autorizar/entregar el supervisor y qué requisitos faltan antes de desplegar.  
**Fuentes revisadas:** `TRABAJO.md`, `AGENTS.md`, `README.md`, `PRODUCCION_SERVER.md`, `QA_REPORTE.md`, `docker-compose.yml`, `Dockerfile.api`, `frontend/Dockerfile`, `api/main.py`, `api/search_engine.py`, `api/qdrant_engine.py`, `core/`, `scripts/`, `requirements.txt`, `data/products.csv`, `frontend/src/`.

---

## 0. Veredicto rápido

El sistema **funciona en local**: API en `:8000`, Next.js en `:3000`, 284 productos, índices `.npy` alineados y Qdrant con 284 puntos. El Hito 2 está aprobado por QA.

Pero **no está listo para un despliegue público ni para el Hito 3**. No es solo un tema de “permisos de usuario”: la API no tiene login ni roles. Los permisos que faltan son **habilitaciones del supervisor** (infraestructura, datos, secretos, legal) y **decisiones de arquitectura**.

| Escenario | Estado | Qué implica |
|---|---|---|
| Demo privada en un VPS, con datos de prueba | 🟡 Desplegable tras 1–2 días de hardening | Sirve para mostrar el flujo, no para clientes reales |
| Producción pública | 🔴 No apto todavía | Faltan seguridad, TLS, datos reales y operación |
| Hito 3 (15.000 diseños + WordPress) | 🔴 Falta casi todo el alcance | Faltan catálogo, plugin, evaluación y comparación |

**Si solo hay una reunión con el supervisor, priorizar:**

1. Definir el alcance: demo privada, producción pública o Hito 3.
2. Conseguir datos reales y autorización legal de uso.
3. Aprobar servidor + dominio + TLS + secretos.
4. Decidir el backend único: `.npy` o Qdrant.

---

## 1. Permisos que debe dar el supervisor

| Habilitación | Para qué | Qué debe entregar |
|---|---|---|
| **Infraestructura y presupuesto** | Levantar API, frontend y Qdrant | Servidor/VPS o proyecto cloud, región, acceso SSH, `sudo`/Docker y autorización de gasto. Mínimo recomendado: **4 vCPU, 8 GB RAM, 50 GB disco**. Ideal GPU si se usará `fusion`. |
| **Red, dominio y TLS** | Publicar con HTTPS | Subdominio (ej. `busqueda.sublitex.com`), acceso DNS, certificado Let's Encrypt y apertura solo de **80/443**. Cerrar `3000`, `8000`, `6333` y `6334`. |
| **Secretos y credenciales** | Configurar producción sin filtrar claves | `.env` de producción, `QDRANT_API_KEY` si Qdrant es cloud, token de Hugging Face si hace falta, API key de la aplicación, credenciales de WordPress/WooCommerce y secretos de CI/CD. |
| **Datos reales del catálogo** | Cumplir el contrato de datos | Nombres comerciales reales, URLs reales, imágenes correctas, catálogo de 15.000 diseños si aplica y mapeo `design_id → product_id` de WooCommerce. |
| **Derechos de uso** | Publicar imágenes y marcas | Autorización escrita para almacenar, mostrar y enlazar las imágenes; revisión de términos del proveedor; permisos de marcas/logos; política de privacidad y retención de imágenes subidas por usuarios. |
| **Legal de modelos y código** | Evitar incumplimientos | Aprobación de licencias de CLIP/OpenCLIP/SigLIP y eliminación de `ultralytics` (AGPL-3.0) si no se usa. Hoy está en `requirements.txt` sin importarse. |
| **WordPress/WooCommerce** | Hito 3 / Sala 5 | Acceso de administrador a un sitio staging, permiso para instalar el plugin, claves REST de WooCommerce y versión de PHP/WordPress objetivo. |
| **Operación** | Poder sostener el servicio | Responsable de backups, monitoreo, logs, ventana de despliegue, rollback y contacto de incidentes. |
| **Repositorio/CI** | Desplegar de forma reproducible | Permiso de escritura/merge, deploy key o registry, y secretos de GitHub Actions si se automatiza. |

### 1.1 Permisos que NO existen hoy dentro de la aplicación

La API no tiene autenticación ni autorización. Si se expone públicamente, cualquiera puede:

- consumir CPU/GPU con `POST /search/image`;
- reindexar con `POST /index/qdrant`;
- consultar `/docs` y `/health`;
- enviar archivos sin límite de tamaño real en servidor.

Antes de producción hay que crear, como mínimo:

- **API key o JWT** para clientes;
- **rol administrador** para indexación;
- **CORS restringido** al dominio del frontend;
- **rate limiting** y límite de subida;
- **política de retención** de imágenes de consulta.

---

## 2. Requerimientos que faltan

### 2.1 🔴 Bloqueantes para producción

#### 1. Los datos del catálogo son de prueba, no reales

Evidencia en `data/products.csv`:

- **284/284 URLs** son `https://ejemplo.com/...`.
- **284/284 nombres** (`nombre_original`) son iguales al ID (`SBX-01-0001`).
- La columna `imagen` apunta a `.png` (`SBX-01-0001.png`), pero el banco real `data/images_normalized/` contiene `.jpg`.
- Todos los proveedores son `SBX`.

El QA reportó “0 URLs vacías”, pero no validó que fueran URLs reales. Para producción hacen falta nombres, URLs y archivos reales, y corregir la extensión en el CSV.

**Impacto:** el Top 5 muestra IDs en lugar de nombres comerciales y enlaces que no llevan a ningún producto.

---

#### 2. No hay autenticación ni protección de la API

Evidencia:

- `api/main.py` no tiene `Depends`, API key, JWT ni roles.
- `api/main.py:231` usa `allow_origins=["*"]` con credenciales.
- `api/main.py:618` expone `POST /index/qdrant` sin autenticación.
- `docker-compose.yml` publica Qdrant en `6333` y `6334` sin API key.
- `docker-compose.yml` publica la API directamente en `8000`.
- No hay reverse proxy ni TLS.

**Qué falta:**

- Reverse proxy con TLS (Caddy/Nginx).
- API key/JWT para clientes.
- CORS restringido al dominio real.
- Rate limiting.
- Qdrant solo en red interna, con API key si aplica.
- Cerrar puertos internos (`3000`, `8000`, `6333`, `6334`).
- Endpoint de indexación protegido o deshabilitado en producción.

---

#### 3. La URL de la API del frontend está mal resuelta para producción

Evidencia:

- `docker-compose.yml:45` define `NEXT_PUBLIC_API_URL=http://localhost:8000` en runtime.
- `frontend/Dockerfile` ejecuta `npm run build` **sin** pasar `NEXT_PUBLIC_API_URL` como build arg.
- En Next.js, las variables `NEXT_PUBLIC_*` se inyectan en **tiempo de build** para el código cliente.

**Impacto:** el navegador de un usuario remoto intentará llamar a *su propio* `localhost:8000`, no al servidor.

**Qué falta:**

- Pasar `NEXT_PUBLIC_API_URL` como `ARG`/`ENV` antes de `npm run build`.
- Usar la URL pública real (ej. `https://api.sublitex.com`) o un proxy relativo.
- Recompilar la imagen cuando cambie la URL.

---

#### 4. El build de Docker no es reproducible y puede ser enorme

Evidencia:

- No existe `.dockerignore` en la raíz ni en `frontend/`.
- El contexto de build incluye `.venv` (~2,6 GB), `frontend/node_modules` (~529 MB), `data` (~370 MB) y `.git` (~3,9 GB): más de **7 GB** de contexto.
- No hay `frontend/package-lock.json`.
- `Dockerfile.api` instala `torch>=2.0.0` desde PyPI; en Linux eso suele resolver la wheel CUDA y sus dependencias, aunque el proyecto es CPU.
- `requirements.txt` usa `>=` en todas las dependencias.
- `qdrant/qdrant:latest` no está pineado.
- `Dockerfile.api` hace `COPY .env* ./`, lo que puede hornear un `.env` con secretos dentro de la imagen si existe durante el build.
- El caché de modelos de Hugging Face no se persiste en un volumen: al recrear el contenedor se vuelven a descargar CLIP/OpenCLIP/SigLIP.

**Qué falta:**

- `.dockerignore` en raíz y frontend.
- `package-lock.json` y `npm ci`.
- Torch CPU (`--index-url https://download.pytorch.org/whl/cpu` o versión `+cpu`).
- Versiones pineadas de dependencias e imágenes base.
- Secrets por variables de entorno o Docker secrets, nunca `COPY .env*`.
- Volumen para `~/.cache/huggingface`.

---

#### 5. Hay dos backends y la documentación no coincide

Evidencia:

- `PRODUCCION_SERVER.md` presenta Qdrant como obligatorio.
- `POST /search/image` usa el motor `.npy` (`api/search_engine.py`).
- Qdrant solo se usa en endpoints separados (`/search/image/qdrant`, `/index/qdrant`).
- `qdrant_data/` está en `.gitignore`, así que un despliegue limpio arranca sin vectores hasta ejecutar `scripts/migrar_a_qdrant.py`.

**Impacto:** no está claro cuál es la fuente de verdad. Un despliegue puede parecer correcto y estar usando un índice distinto del que se populatea.

**Qué falta:**

- Decidir un backend canónico: `.npy` o Qdrant.
- Si es Qdrant: migrar, crear snapshot y verificar la colección al arranque.
- Documentar el procedimiento de reconstrucción del índice.
- Alinear `PRODUCCION_SERVER.md`, `README.md` y `AGENTS.md`.

---

#### 6. Exposición de datos y consumo de recursos

Evidencia:

- `api/main.py` guarda todas las imágenes subidas en `data/queries_original/` y `data/queries_procesadas/` mediante `_guardar_versiones()`, sin límite ni caducidad.
- No hay límite de tamaño en servidor: el cliente valida 15 MB, pero `await file.read()` acepta cualquier tamaño por `curl`.
- No hay rate limit ni cuotas.
- El frontend usa `fusion` por defecto (`frontend/src/app/search/page.tsx:26`), que en CPU tarda >60 s la primera consulta y ~5–6 s las siguientes.
- En la prueba local la API llegó a consumir ~2,6 GB de RAM y ~100 % de CPU al cargar/atender.

**Qué falta:**

- Límite de subida en servidor y en proxy.
- Rate limiting.
- Retención/borrado automático de consultas.
- Plan de capacidad o GPU.
- Modelo por defecto `clip` si no hay GPU.
- Evitar devolver imágenes base64 en `auto` si no son necesarias para el contrato.

---

### 2.2 🟡 Importantes antes de un go-live serio

- **Escala del Hito 3:** hay 284 productos, no 15.000; hay 50 consultas de evaluación, no las 60 del Hito 3; no existe comparación Hito 2 vs. Hito 3.
- **Plugin WordPress/WooCommerce:** no está en el repo. Faltan plugin instalable, buscador visual, configuración de URL/timeout y mapeo `design_id → product_id`.
- **Catálogo duplicado en el frontend:** `frontend/src/lib/catalog.ts` tiene una lista hardcodeada de imágenes y nombres generados. Viola que `products.csv` sea la única fuente; al escalar a 15.000 o cambiar el catálogo habrá que tocar código.
- **Sin healthchecks ni readiness:** `docker-compose.yml` no tiene `healthcheck`; `depends_on` no espera a que Qdrant/modelos estén listos. El `lifespan` de la API arranca aunque falte el índice o el modelo, y `/health` puede devolver 500 o tardar.
- **Sin backups, monitoreo, rotación de logs ni rollback:** no hay snapshots de `qdrant_data`, etiquetas de imagen, alertas ni procedimiento de vuelta atrás.
- **Sin tests ni CI:** no hay `.github/`, pytest ni pipeline. El despliegue sería manual y sin verificación automática.
- **Sin límites de recursos:** la API corre como root, sin `mem_limit`/`cpus` ni usuario no-root.
- **Sin validación de bombas de descompresión:** Pillow puede consumir mucha memoria con imágenes maliciosas.
- **Respuesta pesada:** el modo `auto` devuelve la imagen original y la procesada en base64, lo que aumenta banda y latencia sin ser necesario para el contrato.
- **Proxy de imágenes frágil:** `frontend/src/app/api/images/[filename]/route.ts` resuelve `../data/images_normalized` según el `cwd`. Funciona con el volumen de Compose, pero se rompe si se usa `output: standalone` o se cambia el directorio de ejecución.
- **`output: standalone` desaprovechado:** `next.config.ts` lo declara, pero el Dockerfile ejecuta `npm start` y copia `.next` + `node_modules` completos.
- **Documentación desactualizada:** `README.md` menciona `scripts/validate_dataset.py`, `scripts/generar_consultas_hito2.py`, `main.py` raíz y `data/evaluation.csv`, que ya no existen.
- **Sin `LICENSE`:** no hay licencia explícita del proyecto.
- **Repositorio pesado:** `git` reporta ~3,84 GiB empaquetados; `data/DATA_NEW/` e `images_normalized/` están trackeados (284 + 284 imágenes). Para desplegar conviene usar un release/tarball o registry, no un `git clone` completo.

---

### 2.3 🔴 Brechas específicas del Hito 3

Según `TRABAJO.md`:

| Requisito Hito 3 | Estado actual |
|---|---|
| Biblioteca normalizada de ~15.000 diseños | 284 diseños |
| Embeddings de todo el banco | 284 vectores por modelo |
| Recuperación Top 30–50 + reranking | Implementado parcialmente (30/200 candidatos) |
| Top final visualmente coherente | Hito 2 aprobado; falta validar a escala |
| Devolver menos de 5 resultados si no hay suficientes | Existe umbral dinámico, falta evidencia a escala |
| Pruebas con fotos reales y personas | 50 consultas Hito 2 |
| Comparación Hito 2 vs. Hito 3 | No existe |
| Plugin WordPress conectado a FastAPI | No existe |
| Mapeo `design_id → product_id` WooCommerce | No existe |
| 60 consultas mínimas | 50 consultas |

---

### 2.4 🟡 Legal, privacidad y licencias

- **Imágenes y marcas:** el catálogo incluye camisetas con equipos/logos (Barcelona, Boca, Perú, etc.). Publicarlas comercialmente requiere derechos o autorización. Revisar términos del proveedor y del scraping.
- **Fotos de personas:** las consultas de categoría `persona` y las imágenes subidas por usuarios pueden contener datos personales. Hace falta base legal, consentimiento, retención y borrado.
- **Privacidad:** definir política para `data/queries_original/` y `data/queries_procesadas/`; hoy se guardan indefinidamente.
- **Licencias de modelos:**
  - CLIP: MIT.
  - SentenceTransformers: Apache-2.0.
  - SigLIP: Apache-2.0.
  - OpenCLIP: revisar la licencia específica del modelo/pesos en su model card.
  - `ultralytics`: AGPL-3.0. Está en `requirements.txt` sin importarse; si se mantiene, obliga a liberar el código bajo AGPL o contratar licencia Enterprise.
- **Datos de catálogo:** confirmar que se puede almacenar, transformar y servir públicamente cada imagen y URL.

---

## 3. Checklist mínimo antes de pedir el “go”

### 3.1 Producto y datos

- [ ] Congelar alcance: demo privada, producción pública o Hito 3.
- [ ] Entregar nombres comerciales, URLs reales y archivos correctos.
- [ ] Corregir `imagen` en `products.csv` (`.png` vs `.jpg`).
- [ ] Regenerar índices y validar alineación `ids.npy` ↔ `products.csv` ↔ `embeddings.npy`.
- [ ] Si es Hito 3: cargar ~15.000 diseños y regenerar todos los índices.

### 3.2 Arquitectura

- [ ] Elegir backend único: `.npy` o Qdrant.
- [ ] Si es Qdrant: migrar, crear snapshot y verificar la colección al arranque.
- [ ] Eliminar o documentar los endpoints duplicados.
- [ ] Definir modelo por defecto (`clip` si no hay GPU).
- [ ] Medir latencia p50/p95 con carga real.

### 3.3 Seguridad

- [ ] API key/JWT para clientes.
- [ ] Rol administrador para indexación.
- [ ] CORS restringido al dominio del frontend.
- [ ] Rate limiting.
- [ ] Límite de subida en servidor y proxy.
- [ ] Retención/borrado de imágenes de consulta.
- [ ] Qdrant sin puertos públicos.
- [ ] Reverse proxy con TLS y solo 80/443 expuestos.
- [ ] Contenedores no-root y con límites de recursos.

### 3.4 Build y despliegue

- [ ] `.dockerignore` en raíz y frontend.
- [ ] `package-lock.json` + `npm ci`.
- [ ] Torch CPU o versión pineada.
- [ ] Dependencias e imágenes pineadas.
- [ ] `.env` por secretos, sin `COPY .env*`.
- [ ] `NEXT_PUBLIC_API_URL` como build arg con URL pública.
- [ ] Volumen para caché de Hugging Face.
- [ ] Healthchecks y readiness.
- [ ] Backups de `data/` y `qdrant_data/`.
- [ ] Monitoreo, logs con rotación y alertas.
- [ ] Rollback documentado (imagen/tag anterior).

### 3.5 Verificación en el servidor

- [ ] `docker compose config` sin errores.
- [ ] `GET /health` responde 200 y muestra `desfase_detectado=false`.
- [ ] `POST /search/image` con imagen real devuelve Top 5 correcto.
- [ ] Archivo inválido → 400.
- [ ] Imagen <32 px → 400.
- [ ] Imagen externa → 200 sin cerrar el servidor.
- [ ] Medir p95 con `clip` y con `fusion`.
- [ ] Confirmar que el frontend remoto llama a la API pública, no a `localhost`.

### 3.6 Solo si es Hito 3

- [ ] 15.000 diseños normalizados.
- [ ] Embeddings de todo el banco.
- [ ] 60 consultas (10 exactas, 10 cambios pequeños, 10 recoloreadas/logos, 10 recortadas, 10 mockups, 10 personas).
- [ ] Comparación Hito 2 vs. Hito 3.
- [ ] Plugin WordPress instalable.
- [ ] Buscador visual dentro de WordPress.
- [ ] Configuración de URL/timeout/máximo de resultados.
- [ ] Mapeo `design_id → product_id` WooCommerce.
- [ ] Demostración funcional en staging.

---

## 4. Arquitectura objetivo recomendada

```text
Internet
   │
   ▼
Caddy / Nginx  (443, TLS, rate limit, tamaño máximo)
   ├── /            → Next.js :3000
   └── /api/*       → FastAPI :8000
                         │
                         ├── data/ (read-only)
                         ├── ~/.cache/huggingface (volume)
                         └── Qdrant :6333 (red interna, API key)
```

Reglas:

- Solo **80/443** públicos.
- `3000`, `8000`, `6333` y `6334` sin publicar.
- Frontend y API en la misma red Docker.
- Secrets por `.env`/Docker secrets, nunca en la imagen.
- Healthcheck en API, frontend y Qdrant.
- Backups de `data/` y `qdrant_data/`.
- Logs con rotación y alertas de latencia/errores.

---

## 5. Texto para pedir la autorización

> Para habilitar el despliegue del buscador visual necesito que se apruebe y provea: (1) servidor/VPS o proyecto cloud con Docker, especificando CPU/RAM/disco y presupuesto; (2) dominio o subdominio, acceso DNS y certificado TLS; (3) secretos de producción (`.env`, API key de la aplicación, `QDRANT_API_KEY` si aplica); (4) autorización de uso de las imágenes, nombres, URLs y marcas del catálogo, junto con la política de privacidad y retención de imágenes subidas; (5) decisión de alcance: demo privada, producción pública o Hito 3; (6) si es Hito 3, acceso a WordPress/WooCommerce staging y el catálogo de 15.000 diseños; (7) responsable de backups, monitoreo, ventana de despliegue y rollback. Sin esos puntos el sistema puede levantarse, pero no exponerse públicamente de forma segura.

---

## 6. Decisiones que necesito del supervisor

1. ¿El objetivo es **demo privada**, **producción pública** o **Hito 3 completo**?
2. ¿Qué infraestructura y presupuesto se autorizan? ¿CPU o GPU?
3. ¿Qué dominio/subdominio y quién administra DNS/TLS?
4. ¿Se entregan datos reales y derechos de uso, o se despliega con datos de prueba y aviso explícito?
5. ¿Backend único: `.npy` o Qdrant? ¿Modelo por defecto: `clip` o `fusion`? ¿Latencia máxima aceptable?
6. ¿Quién firma la revisión legal/privacidad y quién opera el servicio?
7. Si aplica Hito 3: ¿quién da acceso al WordPress staging y a las claves de WooCommerce?

---

## 7. Evidencia rápida (archivo → hallazgo)

| Archivo | Hallazgo |
|---|---|
| `data/products.csv` | 284 URLs `ejemplo.com`, nombres = ID, `imagen` `.png` vs banco `.jpg` |
| `frontend/src/lib/catalog.ts` | Catálogo hardcodeado, duplica `products.csv` |
| `frontend/src/app/search/page.tsx:26` | Modelo por defecto `fusion` |
| `frontend/Dockerfile` | `npm run build` sin `NEXT_PUBLIC_API_URL` como build arg |
| `docker-compose.yml:45` | `NEXT_PUBLIC_API_URL=http://localhost:8000` en runtime |
| `docker-compose.yml` | Puertos `3000`, `8000`, `6333`, `6334` publicados; sin healthcheck |
| `api/main.py:231` | CORS `allow_origins=["*"]` |
| `api/main.py:316` | Guarda todas las consultas sin retención |
| `api/main.py:618` | `POST /index/qdrant` sin autenticación |
| `Dockerfile.api` | `COPY .env*` y `pip install` sin CPU index |
| `requirements.txt` | `ultralytics` sin uso; dependencias con `>=` |
| `PRODUCCION_SERVER.md` | Presenta Qdrant como obligatorio, pero `/search/image` usa `.npy` |
| `README.md` | Referencia scripts/archivos eliminados (`validate_dataset.py`, `generar_consultas_hito2.py`, `main.py`, `data/evaluation.csv`) |
| `TRABAJO.md` | Hito 3 exige ~15.000 diseños, 60 consultas y plugin WordPress |
| `QA_REPORTE.md` | Hito 2 aprobado con 284 productos y 50 consultas; `fusion` lento en CPU |

---

## 8. Resumen ejecutivo para el supervisor

- **Se puede mostrar** una demo privada con los 284 productos actuales, tras corregir seguridad mínima, URL de API y build.
- **No se puede poner en producción pública** mientras los nombres/URLs sean de ejemplo, no haya autenticación/TLS y Qdrant esté expuesto.
- **No se puede presentar como Hito 3** porque faltan los 15.000 diseños, las 60 consultas, el plugin WordPress y la comparación Hito 2 vs. Hito 3.
- **La decisión más urgente** es definir alcance y entregar datos reales; sin eso, cualquier esfuerzo de despliegue queda sobre datos de prueba.
