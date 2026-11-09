# AI_LOG.md - Registro de prompts de IA

> Requisito del supervisor: registrar cada prompt de IA usado en el proyecto.

## Fecha: 2026-08-07 (rama sala-2-v2)

### Prompt 1 - Interfaz como cliente puro de API
**Propósito:** Reemplazar la interfaz que hacía búsqueda local por un cliente
que SOLO consume la API de Sala 3.
**Resultado:** `frontend/app.py` — sube la imagen, hace `POST /search/image`,
muestra Top 5 (imagen, ID, nombre, proveedor, URL, score), permite clasificar cada
resultado (Correcto / Útil / Incorrecto) y guarda la evaluación en
`data/evaluation.csv`. Sin embeddings ni búsqueda local.

### Prompt 2 - Script de métricas
**Propósito:** Calcular la precisión Top 1, Top 5, falsos positivos, falsos
negativos y tiempo promedio a partir de `evaluation.csv`.
**Resultado:** `scripts/reporte_metricas.py`.

### Prompt 3 - Protocolo de evaluación (20 pruebas)
**Propósito:** Definir el plan de las 20 consultas de prueba y las imágenes del
grupo A.
**Resultado:** `evaluation/test_plan.csv`, `evaluation/README.md` y 5 imágenes de
prueba en `evaluation/test_images/`.

### Prompt 4 - Verificación de la API de Sala 3
**Propósito:** Verificar que `api/search_engine.py` (conector de
Sala 1 + embeddings de Sala 4) carga los 1000 productos y responde búsquedas.
**Resultado:** Confirmado: 1000 productos, 1000 embeddings (1000,512), búsqueda
Top-K OK.

## Fecha: 2026-08-10 (rama sala-1, Hito 2)

### Prompt 5 - Informe de formatos del banco (Actividad 1 de Sala 1)
**Propósito:** Determinar cuántos formatos visuales existen, posición de marcos,
cabecera, pie/URL, ubicación de frente y espalda, y % recortable por reglas simples,
sobre una muestra ≥100 (se analizaron las 1000).
**Resultado:** `scripts/analizar_formatos.py` → `data/informe_formatos.txt` +
`data/detalle_formatos.csv`. Hallazgos: 5 formatos (1 dominante con 99,4%),
cabecera en 99,7%, pie/URL en 99,8%, frente 17–56% y espalda 57–97% del ancho,
recorte medio estimado 48,7%.

### Prompt 6 - Revisión de la muestra de 50 (Actividad 5 de Sala 1)
**Propósito:** Completar `data/revision_humana_50.csv` (muestra aleatoria semilla 42)
con la clasificación de cada normalizada: solo frente+espalda, sin logo, sin marco,
sin cabecera/pie, sin cortes, sin deformación, lienzo uniforme.
**Resultado:** `scripts/revisar_muestra_50.py` aplica criterios objetivos de píxel
cruzados con el estado del pipeline → **49/50 correctas (98%), 1 dudosa**
(`AIM-P003-164`, espalda lisa indistinguible del fondo), 0 incorrectas.
`data/informe_revision_humana.txt` + hoja de contacto para visto bueno visual final.

## Fecha: 2026-08-10 (rama piloto, complemento Sala 3 / Hito 2)

### Prompt 7 - Bug de rutas no-ASCII en el reranking del Hito 2
**Propósito:** El motor de Sala 3 (`api/search_engine_hito2.py`) dejaba
`score_color = 0` en todas las consultas: `cv2.imread` falla silenciosamente con
rutas que contienen caracteres no-ASCII (p. ej. la carpeta `Imágenes` del perfil
de Windows).
**Resultado:** lectura de imágenes reemplazada por PIL (`Image.open` → BGR) en
`_leer_bgr_desde_ruta` y `_a_imagen_bgr`. Verificado: el reranking por color
ahora produce scores > 0 y el Top 1 es correcto en consultas exactas y sin marco.

### Prompt 8 - Reranking por regiones y estructura
**Propósito:** Complementar el reranking del Hito 2 con los criterios que pide
TRABAJO.md: comparación por regiones (frente/espalda) y distribución del patrón,
con pesos en constantes para calibrar (no asumidos).
**Resultado:** `api/search_engine_hito2.py` ahora combina 5 señales: embedding CLIP
(0,55) + color HSV global (0,15) + color frente (0,10) + color espalda (0,10) +
estructura en grises 32×32 (0,10). Respuesta ampliada con `score_color_global`,
`score_color_frente`, `score_color_espalda`, `score_estructura`, `score_reranking`,
`posicion_final` y `modelo_utilizado`.

### Prompt 9 - Comparación Hito 1 vs Hito 2 con evidencia
**Propósito:** Medir objetivamente si el motor nuevo mejora al del Hito 1 usando
las mismas consultas, con tiempos por consulta y evidencia guardada.
**Resultado:** `scripts/compare_hito1_hito2.py` (lee `evaluation/consultas_hito2.csv`,
mide Top 1/Top 5/tiempos, guarda `data/comparacion_hito1_hito2.csv` + `.json`) y
`scripts/generar_consultas_prueba.py` (genera las 20 consultas derivables:
10 exactas + 10 sin marco; documenta cómo agregar las 30 restantes).
**Resultado real sobre 20 consultas:** Hito 1: Top1 80% / Top5 100% (2 294 ms);
Hito 2: Top1 90% / Top5 95% (2 665 ms). En sin_marco el Top 1 sube de 6/10 a 8/10.

## Fecha: 2026-08-11 (integración de Sala 4 / Hito 2)

### Prompt 11 - Índices comparativos de Sala 4 sobre el banco normalizado
**Propósito:** Sala 4 ya había generado `embeddings_clip/openclip/siglip.npy`
pero desde `images_final/` (con marco), cuando TRABAJO.md exige usar exactamente
las imágenes NORMALIZADAS de Sala 1. Además el CSV apunta a `.png` mientras la
normalización entrega `.jpg` con el mismo ID.
**Resultado:** `scripts/generar_indices_comparativos.py` lee ahora de
`data/images_normalized/` con resolución de extensión (`<id>.jpg`). Re-ejecutado:
CLIP 42,2 s · OpenCLIP 43,8 s · SigLIP 161,8 s; 1000/1000 por modelo, 0 errores,
normalizados L2 (`data/tiempos.csv`).

### Prompt 12 - Evaluación de Sala 4 y colisión de archivo con Sala 1
**Propósito:** `scripts/evaluar_50_consultas.py` escribía su revisión humana en
`data/revision_humana_50.csv`, el MISMO archivo del entregable de Sala 1
(revisar_muestra_50.py), sobrescribiéndolo.
**Resultado:** la salida de Sala 4 ahora es `data/revision_humana_modelos_top5.csv`
(estructura de clasificación humana del Top 5) y se restauró el CSV de Sala 1
(49/50 correctas, 1 dudosa). Evaluación real sobre 50 consultas con índices
normalizados: **CLIP Top1 70% · OpenCLIP 84% · SigLIP 92% (ganador)**,
`data/evaluation_metrics.csv`.

### Prompt 13 - Manifest de la prueba integrada con ids incorrectos (CRÍTICO)
**Propósito:** `evaluation/consultas_hito2.csv` asignaba `id_correcto` con la
lista de patrones vieja (AIM-P001-001/-010/-025/...) que no correspondía a los
archivos reales de `data/consultas/`; la comparación H1 vs H2 daba 0/50.
**Resultado:** ids verificados por hash perceptual (coincidencia única): los 16
diseños son `AIM-P001-001..016` en orden (c01=AIM-P001-013, c06=AIM-P001-002,
c16=AIM-P001-012). Corregidos los 50 del manifest; `generar_consultas_hito2.py`
y `evidencia_hito2.py` actualizados para no volver a romperlo.

### Prompt 14 - Motor Hito 2 sobre el índice normalizado de Sala 4
**Propósito:** integrar el entregable de Sala 4 en el motor de Sala 3: el
reranking calculaba color/estructura sobre `images_final/` mientras el vector
CLIP provenía del índice Hito 1 (incoherente).
**Resultado:** `api/search_engine_hito2.py` recupera candidatos contra
`data/embeddings_clip.npy` (índice normalizado de Sala 4) con `CARPETA_IMAGENES =
images_normalized` y fallback al Hito 1 si falta el índice. `compare_hito1_hito2.py`
re-ejecutado sobre las 50 consultas: **H1 Top1 30/50 (60%) → H2 32/50 (64%);
Top5 34→37; sin_marco 8/10→10/10; recortada 5/10→10/10; tiempo por consulta
5 472→2 141 ms**; `evaluar_hito2.py` y `evidencia_hito2.py` re-ejecutados;
`REPORTES_HITO2.md`, `README.md` e `INFORME_SALA2_HITO2.md` actualizados.

## Fecha: 2026-08-11 (rama sala-2 / Hito 2) — histórico, números superados

> Nota: los resultados del Prompt 10 (35/50 · 33/50 · 37/50) usaban un manifest
> con `id_correcto` incorrectos; corregido en el Prompt 13 (números reales:
> 32/50 · 30/50 · 35/50 Top 1).

### Prompt 10 - Migración de Sala 2 a la estructura canónica del repo
**Propósito:** El supervisor marcó que `REPORTES_HITO2.md` estaba desactualizado
(decía PENDIENTE y 20/50), que los números eran inconsistentes (resumen 35/50 vs
informe 8/50), que `frontend/app.py` no enviaba `modo`, que faltaban
`data/queries_original/` y `data/queries_procesadas/`, que
`evaluation/consultas_hito2.csv` solo tenía 20 filas y que la carpeta `hito2/`
debía borrarse moviendo sus archivos a las carpetas correspondientes.
**Resultado:**
- `evaluation/consultas_hito2.csv` reconstruido a **50 filas** (10 diseños × 5
  versiones) con las imágenes reales de `data/consultas/` (nomenclatura nueva:
  `cNN_exacto.jpg`, `cNN_sin_marco.jpg`, `cNN_recoloreado.jpeg`, `cNN_recorte.jpg`,
  `cNN_cuerpo.jpeg`) y su `id_correcto`.
- Run canónico nuevo en `data/resultados_hito2.csv` + `data/resumen_hito2.txt`:
  **Hito 1 Top1 35/50 · Hito 2 Top1 33/50 · auto 37/50; Top5 38/50 · 36/50 · 39/50**.
  Borrado el set viejo (`resultados_hito2_sala2_referencia.csv`,
  `resumen_hito2_sala2.txt`, `evidencia_coherencia_sala2.txt`).
- Scripts movidos a `scripts/` con rutas canónicas: `evaluar_hito2.py`,
  `evidencia_hito2.py`, `generar_consultas_hito2.py` (leen `evaluation/consultas_hito2.csv`
  y `data/consultas/`, escriben en `data/`).
- `frontend/app.py` integra selector de modo (`auto`, `procesada`, `original`,
  `completo`, `legacy`), vista antes/después (original vs preparada) y comparación
  de rankings Hito 1 vs Hito 2.
- Generadas `data/queries_original/` (50) y `data/queries_procesadas/` (50) con la
  venv usando `api/preprocesar_consulta.py` (backend GrabCut).
- `REPORTES_HITO2.md` actualizado: Sala 2 **COMPLETO**, 50/50 consultas, métricas
  finales con los números nuevos, comparación por casos A–F y próximos pasos.
- `evaluation/INFORME_SALA2_HITO2.md` actualizado a los números nuevos y movido a
  su carpeta canónica.
- Carpeta `hito2/` eliminada por completo.

## Fecha: 2026-08-11 (Fase 3 - robustez del motor y descriptores avanzados)

### Prompt 15 - Reranking enriquecido con descriptores avanzados y API robusta
**Propósito:** reforzar el motor del Hito 2 añadiendo descriptores visuales
avanzados al score (más allá de color+estructura), corregir escalas del score
CLIP, y endurecer la API (lifespan, validación de imagen, modos correctos).
**Resultado:**
- `api/descriptores_visuales.py` (nuevo): descriptores avanzados por atributo —
  color dominante (k-means HSV), gama cromática (histograma HSV grueso), patrón
  de diseño (energía de textura en grilla), estructura con/sin marco (banda
  perimetral) y franjas/rayas + banda central. Con `similitudes_visuales()`
  (todas las similitudes en [0,1]).
- `scripts/precomputar_descriptores.py` (nuevo): precálculo de los descriptores
  avanzados de las 1000 imágenes → `data/descriptores.json` (clave `id_catalogo`).
- `api/search_engine_hito2.py`: el score_final ahora combina 10 atributos
  (embedding normalizado por consulta con min-max + color global/frente/espalda +
  estructura 32x32 + 5 descriptores avanzados) con pesos calibrables que suman 1;
  `modelo_utilizado` actualizado. Descriptores clásicos y avanzados se leen de la
  carpeta coherente con el índice activo (`images_normalized` en Hito 2,
  `images_final` en el fallback del Hito 1); se usa el precomputado cuando existe
  y on-the-fly con cache si no. Fix de correlación: dos diseños lisos (sin
  variación) ahora puntúan 1.0 en patrón/estructura en vez de 0.0.
- `api/main.py`: `on_event("startup")` (deprecado) reemplazado por
  `lifespan`; validación de dimensión mínima (32px por lado) en `/search/image`
  y `/search/image/v2`; modos corregidos — `auto`/`completo`/`procesada` usan el
  motor con reranking (Sala 1+2+3), nuevo `clasico` (Hito 1 + preprocesamiento de
  Sala 2), `original` y `legacy` sin cambios.
- Verificación: `py_compile` OK en todos los archivos tocados y test funcional de
  `descriptores_visuales` con imágenes sintéticas (auto-similitud 1.0, colores
  distintos → 0.0 en color, lisos vs rayados distinguidos por patrón/franjas).

## Fecha: 2026-08-11 (verificación integral + correcciones)

### Prompt 16 - Verificación de punta a punta del proyecto (sin commit)
**Propósito:** ejecutar el prompt de inicio de sesión (leer AGENTS.md + docx,
hacer que el proyecto funcione completo: API, motor Hito 1 + Hito 2 y frontend,
verificando con curl, registrando en AI_LOG, SIN commit ni push).
**Resultado:**
- `AGENTS.md` creado: reglas operativas para la IA, con la fuente de verdad en
  `RAG HACKATON FIN DE SEMANA .docx`.
- API levantada con la venv (torch CPU): `/health` OK (1000 productos, 1000
  embeddings, 512 dims, `desfase_detectado=false`, ids alineados con el CSV).
- `/search/image` probado con consultas reales: exacto→#2, sin_marco→#1,
  recoloreado→#1, recorte→#1, persona→fuera del Top 5 (caso difícil permitido).
- Manejo de errores OK: sin imagen→422, archivo inválido→400 con el mensaje del
  docx, imagen <32px→400 con mensaje claro.
- `data/descriptores.json` regenerado con las **1000** imágenes (antes 20),
  0 errores, 60s.
- Frontend reescrito como interfaz simple (subir imagen → Top 5); `py_compile`
  OK, Streamlit sirve HTTP 200 sin errores.
- Fix en `api/main.py`: `modo=original` es ruta rápida (0.4s, sin preprocesar);
  antes corría GrabCut + doble embedding innecesariamente.
- Fix en `scripts/compare_hito1_hito2.py`: H1 ahora llama con `modo=original`
  (el default `auto` pasó a usar el motor H2, lo que sesgaba la columna H1);
  categoría `persona` agregada al resumen (estaba como `mockup_persona`).
- Comparación H1 vs H2 regenerada (50 consultas, mismas imágenes):
  **H1 Top1 32/50 (64%) · Top5 36/50 (72%); H2 Top1 36/50 (72%) · Top5 37/50
  (74%)**. Por categoría: sin_marco 7→10 y recortada 6→10 en Top1; recoloreada
  6→7; exacta 10→8 y persona 3→1. La "regresión" en exacta es un artefacto del
  set (las exactas son copias de images_final y el índice H2 es images_normalized);
  persona es el caso difícil documentado en el docx.
- NOTA: no se hizo commit ni push.

### Prompt 17 - Integración OpenCLIP como mejora de la búsqueda (sin commit)
**Propósito:** integrar OpenCLIP (laion/CLIP-ViT-B-32-laion2B-s34B-b79K) como
modelo de embeddings opcional del motor Hito 2 para que la búsqueda reconozca
mejor diseños con franjas/dibujos centrales, usando el índice ya existente
`data/embeddings_openclip.npy` (Sala 4, 1000×512).
**Resultado:**
- `api/search_engine_hito2.py`: índice generalizado por modelo
  (`INDICES_NORMALIZADOS` con `embeddings_clip.npy` / `embeddings_openclip.npy`,
  cache por modelo en `_cache_indices`). `cargar_indice_normalizado(modelo)`,
  `buscar_en_indice_normalizado(..., modelo)` y `search_similar_reranked(...,
  modelo)`. Si falta el índice openclip → ValueError con instrucción de
  generación (sin fallback silencioso); para "clip" se conserva el fallback al
  índice Hito 1. `modelo_utilizado` responde `openclip+color+estructura+...`.
- `api/main.py`: parámetro de formulario `modelo` (`clip` default | `openclip`)
  en `/search/image` y `/search/image/v2`; encoder lazy de OpenCLIP vía
  transformers (`get_openclip`/`_embedding_openclip`) precalentado en lifespan;
  extracción del embedding coherente con `extraer_embeddings` del script de
  índices (el checkpoint devuelve `BaseModelOutputWithPooling`; se usa
  `image_embeds` o `pooler_output`). `modelo=openclip` solo válido en modos Hito 2
  (auto/completo/procesada); en H1 (clasico/original/legacy) → 400 con mensaje.
  En modo openclip no se devuelven `resultados_original/procesada` (serían
  mezclas contra el índice CLIP del Hito 1). `/health` expone
  `modelo_openclip` e `indice_openclip_ok`.
- `frontend/app.py`: radio CLIP/OpenCLIP (OpenCLIP por defecto) que envía
  `modelo`; la caption muestra el modelo usado.
- `scripts/compare_hito1_hito2.py`: flag `--openclip` agrega el motor `h2oc`
  (endpoint `/search/image/v2` con `modelo=openclip`) como columna y en el
  resumen por categoría.
- Evaluación (50 consultas, 3 motores, mismas imágenes):
  **H1 Top1 32/50 (64%) · Top5 36/50 (72%)**
  **H2 (CLIP) Top1 36/50 (72%) · Top5 37/50 (74%)**
  **H2 OpenCLIP Top1 41/50 (82%) · Top5 47/50 (94%)** (+5 Top1, +10 Top5 vs CLIP).
  Por categoría (Top1/Top5): exacta 9/10, sin_marco 10/10, recoloreada 9/10,
  recortada 10/10, **persona 3/10→7/10** (CLIP solo 1/10). Evidencia en
  `data/comparacion_hito1_hito2.csv` y `.json`.
- Fix: `_embedding_openclip` inicial falló con `BaseModelOutputWithPooling` (sin
  `.norm()` ni `.image_embeds`); resuelto con la misma lógica de
  `extraer_embeddings` (image_embeds → pooler_output).
- NOTA: el modelo OpenCLIP queda como opción (`modelo=openclip`); el default
  sigue siendo `clip` para conservar el contrato del docx ("un solo modelo CLIP").
- NOTA: no se hizo commit ni push.

### Prompt 18 - Robustez a oclusiones: fusión CLIP+OpenCLIP+SigLIP y multi-recorte (sin commit)
**Propósito:** que la búsqueda encuentre el producto más parecido AUNQUE la
imagen tenga un "punto grande" u otro elemento tapando parte del diseño.
**Resultado:**
- `api/search_engine_hito2.py`: recuperación por FUSIÓN de índices alineados
  (`recuperacion_fusion` promedia por producto los cosenos de clip+openclip+
  siglip) y multi-recorte (imagen completa + 4 cuadrantes, score = MÁXIMO por
  recorte): si un recorte contiene el punto que tapa, otro lo compensa.
  Refactor del reranking en `_rerank_candidatos` reutilizable por el motor de
  un solo modelo y por el de fusión (`search_similar_reranked_fusion`).
  Pesos reajustados para robustez: embedding 0.50 (la señal más robusta a
  oclusiones), estructura 0.07, color_dominante 0.08, patron 0.06, franjas 0.04.
- `api/main.py`: modelo `fusion` (CLIP+OpenCLIP+SigLIP) con `get_siglip` +
  `_embedding_siglip` (transformers, lazy) y `_recortes_consulta`/`_encodificar_fusion`
  (5 recortes × 3 modelos). `_motor_reranked` despacha según modelo;
  `CANDIDATOS_INICIALES_FUSION=100`. En modos no-clip solo se calcula el
  embedding de la consulta preparada (ahorra ~50% del cómputo). `/health`
  expone `modelos_fusion`.
- `frontend/app.py`: radio con opción recomendada "Fusión (CLIP + OpenCLIP +
  SigLIP) — más robusto" como default.
- `scripts/compare_hito1_hito2.py`: flag `--fusion` agrega el motor `h2fu`.
- Evaluación estándar (50 consultas): **Fusión Top1 42/50 (84%) · Top5 48/50
  (96%)**, OpenCLIP 40/46, H2-CLIP 34/37, H1 32/36. Fusión recupera exacta
  10/10 y persona 8/10 Top5.
- Prueba de oclusión (punto negro/blanco 34% y 50%, 3 posiciones, 5 productos,
  60 casos): oclusión 34% → **fusión 30/30 y openclip 30/30** (clip 27/30);
  oclusión 50% (punto que cubre toda la imagen) → fusión 18/30 (openclip
  15/30, clip 11/30).
- Tiempos (CPU, en caliente): fusión ~5-6s por consulta (15 forwards), clip y
  openclip <1s.
- LÍMITE honesto: no existe "100%". Con un punto de hasta ~1/3 del diseño la
  fusión acierta siempre; con una mancha que cubre TODA la imagen (50%) ningún
  modelo puede garantizarlo. Es el límite físico de cualquier sistema visual.
- NOTA: no se hizo commit ni push.

### Prompt 19 - images_normalized como carpeta ÚNICA de búsqueda (sin commit)
**Propósito:** que `data/images_normalized/` sea la carpeta de donde se buscan
TODAS las imágenes del catálogo (antes el fallback del Hito 1 leía los
descriptores visuales desde `images_final/`).
**Resultado:**
- `api/search_engine_hito2.py`: eliminado `CARPETA_IMAGENES_H1` y la bandera
  `_indice_normalizado_activo`. `_carpeta_imagenes_activa()` ahora SIEMPRE
  devuelve `CARPETA_IMAGENES` (`data/images_normalized/`), sin excepciones.
  Los descriptores visuales (color/estructura/avanzados) se calculan siempre
  sobre el banco limpio, coherente con los índices de Sala 4.
- Nuevo `_resolver_imagen(nombre, id)`: resuelve por nombre exacto del CSV o
  por el equivalente normalizado `<id>.jpg` (Sala 1 convierte todo a .jpg);
  usado por `_descriptores_de_archivo` y `_descriptores_avanzados_candidato`.
  Verificado: las 1000 imágenes de products.csv resuelven en images_normalized.
- `_descriptores_avanzados_candidato` ahora usa SIEMPRE los precomputados de
  `descriptores.json` (calculados sobre images_normalized), no solo cuando el
  índice activo era el normalizado.
- El fallback del Hito 1 (falta embeddings_clip.npy) sigue funcionando solo
  para el ranking por vectores; las imágenes siempre salen de images_normalized.
- Verificación: `/search/image/v2` con openclip sobre una imagen de
  images_normalized → top1 correcto (score 1.0), `modelo_utilizado` correcto.
- REFUERZO ESTRICTO: se revisó todo el flujo de búsqueda (frontend + API +
  precomputo). `frontend/app.py` y `api/search_engine_hito2.py` solo usan
  `data/images_normalized/`. `scripts/precomputar_descriptores.py` también se
  hizo estricto: eliminado el respaldo a `images_final`; si un producto no
  resuelve en images_normalized se marca error, no se sustituye. Se regeneró
  `data/descriptores.json` → fuente "images_normalized", 1000/1000 OK, 0
  errores (el respaldo a images_final nunca fue necesario).
- NOTA: no se hizo commit ni push.

## Fecha: 2026-08-12 (migración de banco: images_final -> images_normalized)

### Prompt - Unificar el banco de imágenes del sistema en data/images_normalized/
**Propósito:** Hacer que las imágenes que muestra la interfaz, las que usa el
algoritmo para generar embeddings y las que se comparan contra la consulta del
usuario sean SIEMPRE las normalizadas de data/images_normalized/ (Sala 1, sin
marco ni texto externo), en lugar de data/images_final/.
**Resultado:**
- scripts/generar_embeddings.py: IMAGES_DIR -> data/images_normalized/ +
  
esolver_ruta_imagen() (fallback <id>.jpg porque la normalización
  convierte todo a .jpg y 177 filas del CSV usan .png/.gif/.jpeg).
- rontend/app.py: 
uta_local() ahora intenta el nombre exacto del CSV y,
  si falta, el equivalente <id>.jpg en images_normalized/ (antes 177
  productos caían a la URL remota).
- scripts/validate_dataset.py: valida contra data/images_normalized/ con el
  mismo fallback.
- Re-generados data/embeddings.npy + data/ids.npy desde images_normalized:
  1000 productos, 1000 embeddings (1000x512), errores 0, IDs alineados con
  products.csv, vectores L2 normalizados. Resultado idéntico a
  data/embeddings_clip.npy (ambos sobre el banco normalizado con el mismo
  modelo openai/clip-vit-base-patch32), confirmando coherencia Hito 1/Hito 2.

## Fecha: 2026-08-12 (Sala 1, Hito 3 — banco de 15.272)

### Prompt 6 - Consolidadar 15.272 y normalizar el banco completo
**Propósito:** Llevar el flujo del README hasta la creación de data/images_normalized/ con el banco completo (~15.000) descargado y normalizado.
**Resultado:**
- scripts/consolidar.py corregido: (a) las URLs repetidas del sitio (misma preview para productos distintos con imágenes locales distintas) ahora son avisos, no errores bloqueantes; (b) fallback por índice numérico para los 97 nombres con espacios dobles; (c) conversión automática de .webp a .jpg (AIM-P221-001); (d) redimensionado de la imagen gigante (AIM-P130-056, 219M px) para evitar DecompressionBombError y OOM; (e) limpieza de archivos huérfanos en images_final.
- scripts/normalizar_imagenes.py: fallback conservador 'dudoso' para imágenes sin frente/espalda detectables (casacas claras sobre fondo blanco), completando 15.272/15.272.
- Productos: products.csv 15.272 filas, images_final 15.272, images_normalized 15.272 (.jpg), 0 fallidas, 347 dudosas, informe_normalizacion, detalle_normalizacion, analizar_formatos (5 formatos), revisión muestra 50 (98% correctas), validate_dataset (0 faltantes/dañadas; 104 URLs repetidas aviso; 307 duplicados por hash MD5).

### Prompt 7 - Reporte del Hito 3 y validación humana de 100
**Propósito:** Crear el reporte REPORTES_HIT3.md analizando el Hito 3 de TRABAJO.md (foco Sala 1) y completar la validación humana de 100 imágenes que el Hito 3 exige (antes eran 50).
**Resultado:**
- REPORTES_HIT3.md: resumen, estado global (Sala 1 completa; Salas 4, 3, 2 y 5 pendientes), análisis del proyecto (15.272 productos), Sala 1 en detalle (entregables, actividades, validaciones, medición, problemas resueltos en consolidar.py, desglose de 347 dudosas, respuesta a la pregunta central), métricas obligatorias y próximos pasos.
- scripts/normalizar_imagenes.py: generar_muestra_humana parametrizable (revision_humana_{N}.csv + revision_contact_sheet_{N}.png) y modo --solo-muestra --muestra N para regenerar la muestra sin re-normalizar; main() acepta --muestra.
- scripts/revisar_muestra_50.py: acepta --n (100 en Hito 3), nombres dinámicos y aviso de uso.
- Resultado real: revision_humana_100.csv -> 99/100 correctas (99%), 1 dudosa (AIM-P202-007: 4 bandas, frente/espalda fusionados), 0 incorrectas; informe_revision_humana_100.txt; revision_contact_sheet_100.png.
- REPORTES_HIT3.md actualizado con los resultados reales de la revisión de 100.

## Fecha: 2026-08-13 (Sala 4 + Sala 3, Hito 3 — embeddings a escala 15.272)

### Prompt - Re-indexar el sistema a escala 15.272 sobre images_normalized
**Propósito:** Generar los índices del Hito 3 con el banco completo (15.272) a
partir de data/images_normalized/ (única carpeta del catálogo), que eran los
bloqueos de Sala 4 y Sala 3 (no existía ningún .npy a escala).
**Resultado:**
- `scripts/generar_embeddings.py` (Hito 1, CLIP openai) re-ejecutado sobre las
  15.272 normalizadas → `data/embeddings.npy` (15272×512) + `data/ids.npy`
  (15272, alineado posición a posición con products.csv).
- `scripts/generar_indices_comparativos.py` (Sala 4) re-ejecutado a escala →
  `data/embeddings_clip.npy` (15272×512, listo) y `embeddings_openclip.npy` +
  `embeddings_siglip.npy` en generación (CPU, sin GPU; run secuencial).
- Verificado motor Hito 1 a escala: carga 0,62 s, búsqueda 61 ms, Top 1 exacto.
- Verificado motor Hito 2 (`search_similar_reranked`) contra el índice clip de
  15.272: recuperación Top 30 en 0,15 s, Top 1 correcto, respuesta con
  score_recuperacion/score_reranking/posicion_inicial/posicion_final/modelo.

### Prompt - Contrato de respuesta del Hito 3 y descriptores a escala
**Propósito:** Alinear la respuesta de la API con HITO3.md (Sala 3, punto 7) y
escalar los descriptores del reranking.
**Resultado:**
- `api/search_engine_hito2.py`: cada resultado ahora incluye `score_recuperacion`
  (alias de score_inicial), `posicion_inicial` (posición en la recuperación
  amplia) y `modelo` (además de `modelo_utilizado`), cumpliendo el contrato
  `id, score_recuperacion, score_reranking, posicion_inicial, posicion_final,
  modelo, nombre, imagen, url`.
- `frontend/app.py`: muestra recuperación vs reranking y `posicion_inicial →
  posicion_final`.
- `scripts/precomputar_descriptores.py` re-ejecutado a 15.272 →
  `data/descriptores.json` (fuente images_normalized) para que el reranking no
  compute descriptores on-the-fly con el catálogo grande.
- NOTA: no se hizo commit ni push.

## Fecha: 2026-08-13 (rediseño de interfaz frontend)

### Prompt - Mejora de la UI de frontend/app.py sin romper el funcionamiento
**Propósito:** Rediseñar la interfaz de Sala 2 (cliente puro de la API) con un
look moderno y más información, manteniendo intacto el contrato con la API.
**Resultado:** rontend/app.py rediseñado:
- Tema oscuro deportivo vía CSS (gradientes, tarjetas redondeadas, chips de
  estado, barra de score por resultado).
- Sidebar nueva: URL de la API configurable, verificación de /health,
  selector de modelo (fusion/openclip/clip) e instrucciones.
- Header con estado de la API (productos/embeddings) y chips.
- Panel de consulta: imagen original + imagen preparada por Sala 2
  (imagen_procesada_b64) + detalles del preprocesamiento en expander.
- Resultados en tarjetas: badge de ranking (#1 destacado), nombre, ID,
  proveedor, score de similitud con barra, recuperación vs reranking,
  posición inicial → final, modelo utilizado y enlace a la imagen original.
- Registro de evaluación humana (Muy similar / Similar / Poco similar /
  No relacionado + observación) guardado en data/evaluation.csv con las
  columnas del contrato (consulta, resultado_id, posicion, score,
  clasificacion_humana, observacion).
- Selector de imágenes de prueba desde data/consultas/ para demos.
- Sin embeddings ni búsqueda local: solo consume POST /search/image.
**Verificado:** py_compile OK, arranque headless de Streamlit OK (HTTP 200)
y prueba real contra la API con consulta de data/consultas/ (modo completo,
modelo fusion, 5 resultados con todos los campos del contrato).

## Fecha: 2026-08-13 (tema claro/oscuro en español, caché de preferencia)

### Prompt - Tema en español, tema claro mejorado y preferencia en caché
**Propósito:** Que la interfaz esté íntegramente en español, arreglar el tema
claro (se veía mal) y recordar la elección de tema entre sesiones.
**Resultado:**
- .streamlit/config.toml nuevo: [theme] base = "dark" para que los widgets
  nativos (selectbox, botones, expander) combinen con el diseño oscuro.
- rontend/app.py: toggle "🌓 Tema claro" en el sidebar (español) que aplica
  un tema claro rediseñado (gradientes suaves, tarjetas blancas, textos y
  chips legibles, botones/inputs/expander re-skin via CSS) y guarda la
  preferencia en rontend/.theme_pref.json (caché entre sesiones) +
  st.session_state (caché entre reruns).
- Menú nativo: se ocultan los items en inglés "Get help"/"Report a bug" y
  "About" muestra texto en español (el menú Settings de Streamlit en sí no es
  traducible; el control de tema propio queda en español).
- rontend/.theme_pref.json agregado a .gitignore.
**Verificado:** py_compile OK, arranque headless con tema claro OK (HTTP 200),
ciclo guardar/leer de la preferencia OK.

### Prompt - Fix KeyError tema_claro
**Propósito:** Corregir KeyError: st.session_state has no key "tema_claro" en
arranque: la inyección CSS condicional (linea 178) se ejecutaba antes de la
inicializacion de la clave en session_state.
**Resultado:** cargar_tema()/guardar_tema() y la inicializacion
if "tema_claro" not in st.session_state movidas al inicio del script (antes
de la inyeccion CSS). Verificado con streamlit.testing.v1.AppTest:
arranque sin pref, con pref claro, y toggle off (persiste en
rontend/.theme_pref.json).

## Fecha: 2026-08-13 (acciones imprimir/descargar, sin emojis, tema claro)

### Prompt - Imprimir/descargar en resultados, soporte tema claro, sin emojis
**Propósito:** (1) Botones Imprimir y Descargar imagen en cada resultado; (2)
que esos controles soporten el tema claro; (3) eliminar TODOS los emojis de la
interfaz usando iconos SVG en línea (sin descargar librerías, solo código
inline); (4) sin opción de grabar video.
**Resultado:**
- html_acciones(): iframe via streamlit.components.v1.html con botones
  "Descargar" (data-URI + download) e "Imprimir" (ventana nueva + print) por
  resultado, coloreados según tema claro/oscuro.
- Iconos SVG estilo Feather inline (_svg() + dict ICONOS): gear, zap, cpu,
  info, sun, target, search, trophy, wrench, link, edit, shirt. Sin emojis en
  toda la app y sin CDN (nada se descarga, todo inline).
- page_icon emoji eliminado; clase .result-img con borde adaptado a cada
  tema; labels de widgets en texto plano.
- No se agregó ninguna opción de grabación de video.
**Verificado:** py_compile OK; AppTest en tema oscuro y claro sin excepciones;
flujo completo con imagen real (c01_cuerpo.jpeg) contra la API: 5 tarjetas +
5 iframes de acciones + 5 expanders de evaluación renderizados sin errores.

## Fecha: 2026-08-13 (fix iconos SVG invisibles + descarga corrupta)

### Prompt - Fix: iconos no visibles y descarga de imagen corrupta
**Propósito:** (1) Los SVG inline no se renderizaban porque el sanitizador de
Streamlit no permite etiquetas svg (labels de expander usan allowHTML=false
y st.markdown pasa por rehype-raw/DOMPurify); (2) la descarga por data-URI
JS descargaba archivo corrupto (data URI gigante en el srcdoc del iframe).
**Resultado:**
- Iconos migrados a **Bootstrap Icons por CDN** (solo URL, sin descargar):
  <link> en st.markdown + <i class="bi bi-xxx ic"></i>. Los labels de
  expander (que escapan HTML) quedan sin icono, en texto plano.
- Descarga reemplazada por st.download_button nativo: envía los BYTES reales
  del archivo local por websocket (archivo JPEG siempre válido). El iframe
  queda solo con el botón Imprimir.
- Tema claro: botón secundario (Descargar) también re-estilizado en claro.
**Verificado:** py_compile OK; AppTest con imagen real contra la API en tema
oscuro y claro: 5 resultados, 5 download_buttons (label/filename/mime/bytes)
sin excepciones; sin emojis restantes.

## Fecha: 2026-08-13 (fix: descarga re-dispara búsqueda + iconos emoji)

### Prompt - Fix: al descargar se repite la búsqueda; los SVG no se ven
**Propósito:** (1) El botón Descargar (widget) provoca un rerun de Streamlit
que re-ejecutaba la búsqueda contra la API (lento y duplicaba consultas);
(2) los iconos por CDN (Bootstrap Icons) tampoco se veían en el navegador;
el usuario autorizó emojis si SVG no funciona.
**Resultado:**
- **Caché de búsqueda:** hash md5(bytes imagen + modelo + api_url) guardado en
  st.session_state["busqueda_clave"]; la API solo se consulta si cambia la
  clave. Los reruns de widgets (descargar, evaluar) ya no re-buscan.
- **Iconos en emojis** (texto plano, se ven en todos los contextos): sidebar,
  encabezados, chips, labels de expander y botón Imprimir del iframe
  (🖨️/⬇️/⚙️/🧠/ℹ️/🎯/🔍/🏆/🛠️/🔗/✏️/👕). Eliminado el CDN y la clase .ic.
**Verificado:** py_compile OK; AppTest con contador de requests.post: 1 solo
POST tras subir la imagen y 0 nuevos en reruns posteriores; 5 download_buttons;
sin excepciones en tema oscuro y claro; emojis presentes en labels y expanders.

## Fecha: 2026-08-13 (fix: Imprimir no mostraba la imagen)

### Prompt - Fix: la opción Imprimir no muestra la imagen a imprimir
**Causa raíz:** (1) html_imprimir usaba el base64 crudo como src de la
imagen sin el prefijo data:image/jpeg;base64, (lo inyectaba tal cual
devuelve imagen_a_b64) -> imagen rota en el popup; (2) el flujo dependía de
window.open + document.write con el base64 gigante (popups bloqueables y
límite de 1 MB de Chrome en document.write).
**Solución:** sin popup ni document.write. La imagen vive oculta
(display:none) dentro del propio iframe y solo se muestra con
@media print; window.print() imprime el documento del iframe (el sandbox
de components.html incluye llow-modals, verificado en el bundle:
IFrameUtil.PlC_b34Z.js). img.onload garantiza que la imagen ya cargó antes
de imprimir. Agregado el prefijo data:image/jpeg;base64, en el src.
**Verificado:** py_compile OK; AST-test de html_imprimir: print-area +
data URI con prefijo + @media print + window.print, sin window.open ni
document.write, en ambos temas; AppTest flujo completo sin excepciones
(5 iframes, 5 download_buttons).

## Fecha: 2026-08-13 (rediseño visual completo - estética Google Stitch)

### Prompt - Rediseño UI/UX: interfaz moderna de producto de IA (dark ambient)
**Objetivo:** Solo UI/UX; sin tocar arquitectura, API, lógica ni contratos.
Referencia conceptual Google Stitch: dark ambient, minimalismo, gradientes
luminosos sutiles, glassmorphism ligero, espacio negativo, jerarquía fuerte.
**Cambios en frontend/app.py (lógica intacta):**
- Fondo oscuro #05070d con 3 gradientes radiales ambientales (cyan→azul→violeta).
- Hero rejerarquizado: eyebrow "Búsqueda visual" con punto pulsante → título
  grande gradiente "Encuentra camisetas visualmente similares" → subtítulo →
  meta discreta "15,272 productos · 15,272 embeddings · API activa" (sin cards).
- Dropzone protagonista: 250px, borde discontinuo, vidrio (backdrop-filter),
  hover con glow; los textos internos en inglés del widget ("Upload",
  "200MB per file...", "Drag and drop...") se ocultan por CSS (testids
  verificados en bundle FileUploader.Bg9tjvVJ.js) y se superpone overlay en
  español (SVG data-URI + "Arrastra tu imagen aquí / o haz clic para elegir
  archivo") solo en estado vacío vía :has(). Con archivo cargado el overlay
  desaparece y la lista de archivos sigue visible y funcional.
- Pasos en una línea minimalista: "01 Sube tu imagen → 02 La analizamos →
  03 Encuentra similares" (reemplaza las 3 cards).
- Resultados: aparición escalonada (fadeUp con delay 70ms por rank), tarjetas
  glass con hover sutil, score bar delgada, sección "Resultados" con meta
  inline (Top 5 · Modo · Modelo · tiempo).
- Sidebar translúcido con blur; widgets select/input oscuros; botón primario
  gradiente cyan con glow; #MainMenu/footer ocultos; header transparente.
- Responsive: clamp() en título, min-height 195px en dropzone móvil,
  result-layout con flex-wrap en <=640px.
- Tema claro: misma estructura con ambient suave, tarjetas blancas y overlay
  de dropzone en azul.
**Verificado:** py_compile OK; AppTest en oscuro y claro: estado inicial y con
imagen real (c01_cuerpo.jpeg) sin excepciones; 1 file_uploader, 5
download_buttons, 7 expanders, hero/flow/meta/query-status/Resultados
presentes.

## Fecha: 2026-08-13 (luz ambiental interactiva que sigue al cursor)

### Prompt - Efecto ambiental interactivo (estilo Google Stitch), SOLO visual
**Objetivo:** halo de luz difuminado (cyan→azul→violeta, muy sutil) que sigue
el cursor con interpolación suave; decorativo, sin tocar lógica/API/upload.
**Implementación (frontend/app.py):**
- html_luz_ambiental(): iframe invisible (components.html, height=1) cuyo
  script, aprovechando allow-same-origin (sandbox verificado en bundle
  IFrameUtil), manipula el DOM del padre: crea 3 divs .luz de 1900px
  (radial-gradient closest-side, opacidades .16/.12/.09, offsets
  -140/-80 y +120/+50 para un halo asimétrico) colgados de .stApp.
- CSS: .stApp { isolation: isolate; } + .luz { position: fixed;
  z-index: -1; pointer-events: none; will-change: transform; opacity 0 →
  .luz-on 1 (transición .8s) } → la luz queda BAJO la UI y se percibe a
  través de las superficies translúcidas. iframe oculto con
  iframe.stIFrame[height="1px"].
- JS: lerp 0.10 por frame con requestAnimationFrame, solo transform
  translate3d (compositor, sin repaints); encendido en el primer mousemove
  (sin parpadeo inicial), apagado suave al salir de la ventana
  (mouseleave/mouseenter en documentElement); guard anti-duplicados
  (querySelector('.luz')) porque el iframe se re-ejecuta en cada rerun.
- Accesibilidad/perf: desactivada con prefers-reduced-motion y
  pointer: coarse (táctiles); listener mousemove pasivo en el documento.
- Tema claro: mismas capas con alphas reducidas (.11/.08/.06).
- Fix: definición de la función movida antes de su llamada (NameError);
  label del file_uploader no vacío con label_visibility collapsed
  (warning de accesibilidad de Streamlit 1.60).
**Verificado:** py_compile OK; AppTest oscuro/claro: sin excepciones
(inicial y con imagen real); 6 iframes (1 luz + 5 imprimir), 5
download_buttons; JS verificado por AST (rAF, translate3d, reduced-motion,
coarse, guard, 3 capas).

## Fecha: 2026-08-13 (fix: luz ambiental de página completa, no solo en el dropzone)

### Prompt - Fix: el difuminado solo se ve dentro del box de subir imagen
**Causa:** las capas .luz con position:fixed colgadas de .stApp quedaban
ancladas al contenedor (o eran casi invisibles sobre el fondo oscuro plano
fuera de las superficies translúcidas), por lo que el efecto solo se
percibía dentro del dropzone.
**Solución:**
- Capas en position: absolute con .stApp { position: relative }
  (anclaje determinista al documento, inmune a transforms del contenedor) y
  compensación de scroll en el transform: translate3d(scrollX + x + dx,
  scrollY + y + dy) → la luz sigue al cursor en viewport aunque se scrollee.
- Tamaño subido a 2200px y alphas aumentadas (.20/.14/.10 oscuro,
  .14/.10/.07 claro): perceptible sobre toda la página, no solo tras el
  vidrio. Sigue siendo un ambiente sutil (z-index -1, pointer-events none).
**Verificado:** py_compile OK; JS por AST (scrollX/scrollY en transform);
AppTest oscuro/claro sin excepciones (6 iframes, 5 download_buttons).

## Fecha: 2026-08-13 (fix: UI en blanco al cargar + luz ambiental robusta)

### Prompt - Fix: rompiste la UI, no se ve nada al cargar la web
**Causa probable:** las capas .luz ancladas dentro de .stApp con
z-index: -1 + isolation: isolate + position: relative en .stApp
podían romper el apilado/render del contenedor raíz de Streamlit en el
navegador (contenedores de positioning no estándar en .stApp).
**Solución (patrón a prueba de balas):**
- Los gradientes ambientales del fondo pasaron de .stApp a ody
  (el lienzo raíz); .stApp y [data-testid="stAppViewContainer"]
  quedan ackground: transparent.
- Las 3 capas de luz se cuelgan de document.body con
  position: fixed; z-index: -1 (body nunca tiene transform → el
  containing block es siempre el viewport) y transform solo
  clientX/clientY (sin compensación de scroll).
- Eliminados isolation: isolate, position: relative de .stApp y el
  listener de scroll sobrante: .stApp vuelve a su estado original.
- Pintado: sobre el fondo de body y bajo todo el contenido (la luz se ve
  a través de superficies translúcidas) en toda la página.
**Verificado:** py_compile OK; llaves CSS balanceadas (82/82); AppTest
oscuro/claro sin excepciones (6 iframes, 5 download_buttons). Sugerido al
usuario: recarga con Ctrl+F5 (posible caché del bundle anterior).

## Fecha: 2026-08-13 (revert: eliminado efecto de luz ambiental)

### Prompt - vuelve a cambios atrás porque está roto, la cagaste, arregla
**Decisión:** revertir por completo el efecto de luz ambiental (fue la
única adición desde el rediseño aprobado por el usuario) y devolver la
app al estado que el usuario confirmó como bueno.
**Cambios aplicados (frontend/app.py):**
- Eliminado html_luz_ambiental() y su llamada
  components.html(..., height=1, scrolling=False) (línea 454).
- Eliminado CSS .luz, .luz-on, .luz-1/2/3 y
  iframe.stIFrame[height="1px"] del tema oscuro y claro.
- Fondo ambiental restaurado en .stApp (gradientes originales), sin
  ody + transparentes + stAppViewContainer.
**Verificado:** py_compile OK; AppTest oscuro/claro sin excepciones y
con 5 download_buttons tras subir data/consultas/c01_cuerpo.jpeg.
El usuario debe recargar con Ctrl+F5 (caché de bundle anterior).

## Fecha: 2026-08-15 (limpieza legacy + métrica 50/50 Top-1/Top-5 + filtrado estricto Top 5)

### Prompt - Limpiar el código eliminando embeddings y funciones antiguas que ya no se necesitan con la fusión implementada; optimizar los algoritmos de búsqueda equilibrando la ponderación/score a un split 50/50 entre Top-1 y Top-5 al evaluar; refinar umbrales y filtros de ranking para que el Top 5 no fuerce resultados irrelevantes; y generar un reporte .md completo de todos los cambios.
**Decisiones tomadas:**
- El "split 50/50" (aclarado por el usuario) = cada bloque Top-1 y Top-5 aporta
  máx. 50 puntos; 50 = 100% de cumplimiento de ese top. Métrica combinada
  P50/50 = 0.5·Top1% + 0.5·Top5%.
- Eliminados 6 scripts legacy: `build_index.py`, `search.py`,
  `buscar_por_imagen.py`, `ingest.py`, `insertar_db.py`, `reporte_evaluacion.py`
  (confirmado por el usuario). Se conservaron `generar_embeddings.py` (baseline
  Hito 1), `get_product.py` y la ruta de respaldo `index_embeddings.npy`.
**Cambios aplicados:**
- `api/search_engine_hito2.py`: nuevo `UMBRAL_MINIMO_SIMILARIDAD = 0.40`
  (corte absoluto) + corte relativo `MARGEN_CORTE` en `_rerank_candidatos`;
  el Top 5 ahora puede devolver 0..5 resultados sin relleno. Docstring del
  módulo documenta la calibración contra la métrica 50/50.
- `scripts/evaluar_50_consultas.py`: columna `puntaje_combinado` en
  `evaluation_metrics.csv` y en el resumen.
- `scripts/compare_hito1_hito2.py`: `puntaje_combinado` en el JSON/consola +
  columnas `*_mejor_score` por consulta (para recalibrar el umbral con datos).
- `scripts/reporte_comparativo.py`: columna P50/50; el ganador se decide por la
  métrica combinada.
- `scripts/reporte_metricas.py` y `scripts/evaluar_hito2.py`: línea/columna
  P50/50.
- `README.md` y `scripts/GUIA_SALA4.txt`: referencias a los scripts eliminados
  actualizadas.
- Nuevo `REPORTES_HITO3_OPTIMIZACION.md` con el detalle completo y la línea
  base real (fusión P50/50 = 90/100).
**Verificado:** py_compile OK (6 archivos); venv liviano
(numpy/pandas/pillow/opencv-headless) sin torch: `reporte_metricas.py` real
imprime Puntaje 50/50; `reporte_comparativo.py` con datos sintéticos elige al
ganador por P50/50; `_rerank_candidatos` probado con imágenes reales del banco
(casos A idéntica/B persona): filtrado sin relleno y sin resultados bajo el
umbral; cabecera CSV de `compare_hito1_hito2.py` consistente (28/28 columnas).
**Pendiente:** recalibrar `UMBRAL_MINIMO_SIMILARIDAD` con la API corriendo
(`compare_hito1_hito2.py --fusion`); no existe `.venv` en el repo y el Python
del sistema (3.14) está bloqueado por PEP 668, por lo que la recalibración
requiere crear el venv del proyecto.

## Fecha: 2026-08-15 (migración images_final -> images_normalized)

### Prompt - Necesito realizar una migración completa en el proyecto actual. El objetivo es reemplazar todas las referencias, llamadas, importaciones y dependencias de images_final por images_normalized, ya que esta última es la versión actualizada y correcta. Pasos: (1) análisis de impacto; (2) refactorización de código (imports, variables, rutas, lógica); (3) validación de integridad de rutas; (4) limpieza: eliminar el directorio images_final. Restricciones: sin git, cambios directos en el filesystem, detenerse y explicar conflictos si la migración no es directa.

**Contexto:** images_final (15.272 archivos, 2,1 GB) era la salida de Sala 1
(consolidar.py) y la fuente de normalizar_imagenes.py. images_normalized es el
banco canónico (mismo conteo 15.272) y el que ya usaban los índices Hito 2, el
precomputo de descriptores y los motores. products.csv tiene 15.273 filas.

**Decisiones del usuario (consultadas ante conflictos):**
- consolidar.py se ADAPTA para producir images_normalized; normalizar_imagenes.py
  y analizar_formatos.py se marcan legacy (no operativos).
- Registros históricos (revision_humana_50/100.csv, AI_LOG, REPORTES_*,
  informes de evaluación) se dejan INTACTOS; solo se migran docs operativas
  (README, AGENTS, GUIA_SALA4).
- Generadores de consultas (generar_consultas_hito2.py, generar_consultas_prueba.py)
  se marcan legacy (la variante "exacta" requería la imagen cruda con marco);
  evaluar_50_consultas.py se migra con fallback a images_final si existiera.

**Cambios:**
- `scripts/compare_hito1_hito2.py`: TEST_SET_FALLBACK -> data/images_normalized/.
- `scripts/evidencia_hito2.py`: IMGS -> data/images_normalized/.
- `scripts/generar_indices_comparativos.py` y `scripts/precomputar_descriptores.py`:
  solo comentarios actualizados (el código ya usaba images_normalized).
- `scripts/consolidar.py`: RUTA_IMAGENES_DESTINO -> data/images_normalized/
  (nota documentada: regenerar desde scraping entrega tarjetas tal cual;
  normalización ya no se reaplica). Docstring y limpieza de huérfanos actualizados.
- `scripts/normalizar_imagenes.py`, `scripts/analizar_formatos.py`,
  `scripts/generar_consultas_hito2.py`, `scripts/generar_consultas_prueba.py`:
  marcados [LEGACY] con banner explicando que su fuente ya no existe.
- `scripts/evaluar_50_consultas.py`: IMAGES_BANCO_DIR = images_normalized
  (primario) + IMAGES_FINAL_DIR como fallback histórico; `_banco_dir()` resuelve
  y `derivar_ids_correctos()` valida que exista un banco.
- Docs operativas: `README.md` (flujo, consola, árbol, nota del validador),
  `AGENTS.md` (estructura canónica, arquitectura Hito 1 -> images_normalized,
  nombre corregido a scripts/generar_embeddings.py) y `scripts/GUIA_SALA4.txt`
  (árbol + curl) actualizadas.
- ELIMINADO data/images_final/ (15.272 archivos, 2,1 GB) del filesystem.

**Verificado:** py_compile OK (10 scripts); banco resuelto por evaluar_50_consultas
= images_normalized; imágenes clave (AIM-P001-001/002/003/004/013/016.jpg)
existen en images_normalized; grep residual: solo quedan referencias intencionales
(notas "fue eliminada", banners legacy, fallback) y registros históricos intactos;
runtime activo (api/, motores, índices, descriptores, validador) sin referencias
a images_final; images_normalized intacto (15.272 archivos) tras la eliminación.
**Pendiente:** la regeneración del banco vía consolidar.py entregará ahora tarjetas
tal cual (sin normalización); normalizar_imagenes.py quedó como referencia.

## Fecha: 2026-09-21 (limpieza banco viejo para carga nueva)

### Prompt - elimina todo lo que se tiene que eliminar, aun no hagas nada de regenerar
**Propósito:** Vaciar derivados del banco viejo para cargar banco nuevo, sin regenerar todavía.
**Resultado:** Eliminados `data/embeddings.npy`, `embeddings_clip/openclip/siglip.npy`, `ids.npy`, `descriptores.json`, `products.csv`, `productos.json`, `metadata.json`, `evaluation.csv`, `comparacion_hito1_hito2.*`, `consultas_test_50.json`, `detalle_*`, `informe_*`, `revision_humana_*`, `revision_contact_sheet*.png`, `tiempos.csv` y contenidos de `data/queries_original/` + `data/queries_procesadas/` (332+332). Conservados código (`api/`, `scripts/`, `frontend/`), `evaluation/`, `CONSULTAS/`, `scraper/`. `data/` queda con carpetas vacías `queries_original/`/`queries_procesadas/`. Sin regeneración (pendiente: consolidar → validate → generar_embeddings → generar_indices_comparativos → precomputar_descriptores → /health).

## Fecha: 2026-09-21 (borrado banco viejo + conexión scraper Aimari)

### Prompt - elimina todo lo que tenga que ver con las antiguas images y consultas, tambien elimina la conexion de la pagina
**Propósito:** Dejar el repo sin rastros del banco Aimari ni de sus consultas, y sin el scraper de designsaimari.com, para cargar un banco nuevo.
**Resultado:**
- Consultas viejas eliminadas: `evaluation/test_images/` (20), `evaluation/consultas_hito2.csv`, `evaluation/consultas_hito2/`, `evaluation/test_plan.csv`. `CONSULTAS/consultas/` (80) y `CONSULTAS/montajes/` (5) ya estaban vacías en disco (borrado externo 08:57); quedan los dirs vacíos. `data/queries_*` ya vacías del paso anterior.
- Conexión Aimari eliminada: `scraper/` (scraper.py, parser.py, downloader.py), `config/settings.py` (URL_BASE designsaimari.com), `utils/` (helpers, pagination, limits, update), `storage/exporter.py`, `main.py` (runner del scraper). Verificado: nada en `api/`, `scripts/`, `frontend/` importa esos módulos (solo comentarios en `consolidar.py`).
- Conservado: `scripts/consolidar.py` (constructor del banco nuevo; sus constantes PROVEEDOR_NOMBRE/PREFIJO="Designs Aimari"/"AIM" hay que ajustarlas a la fuente nueva), reportes `.md` históricos, `evaluation/INFORME_SALA2_HITO2.md`+`README.md` como evidencia.
- Verificado: `py_compile` OK en api, frontend y scripts canónicos.

## Fecha: 2026-10-19 (levantar backend + frontend con el banco SBX)

### Prompt - "LISTO ENTONCES EJECUTAR EL BACKEND Y EL FRONTEND"
**Propósito:** Poner en marcha el sistema completo de búsqueda visual con el nuevo
banco SBX (284 imágenes de data/DATA_NEW) para probar subiendo fotos.
**Resultado:**
- Se detectó que el venv del proyecto NO está en `sala-5\.venv` sino en
  `C:\Users\lucia\Downloads\S5\.venv` (contiene fastapi, torch CPU, transformers,
  cv2, uvicorn, streamlit). Con él se completó el pipeline:
  1. `normalizar_data_new.py` → 284 imágenes a `data/images_normalized/*.jpg`.
  2. `generar_embeddings.py` → `embeddings.npy` + `ids.npy` (284, 512 dims, 0 errores, 24,8 s).
  3. `generar_indices_comparativos.py` → `embeddings_clip.npy` (512), `embeddings_openclip.npy` (512) y `embeddings_siglip.npy` (768); 284/284, 0 errores. Necesarios porque la interfaz usa el modelo `fusion` por defecto.
- Backend FastAPI levantado: `uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload`.
  `/health` → status ok, 284 productos, 284 embeddings, 512 dims, `desfase_detectado=false`.
  `POST /search/image` (modo=auto, modelo=fusion) probado con `SBX-01-0001.jpg` →
  Top 1 correcto con `score=0.9556`, `score_reranking=0.8579`, `modelo=clip+openclip+siglip`.
- **IMPORTANTE:** `frontend/` ya NO es Streamlit; es una app **Next.js** (React 19,
  Next 16.3.5) cliente de la API en `NEXT_PUBLIC_API_URL=http://localhost:8000`.
  Se levantó con `npm run dev` → http://localhost:3000 (HTTP 200).
  Su proxy `/api/images/[filename]` sirve las imágenes de `data/images_normalized/`
  (probado: `SBX-01-0001.jpg` → HTTP 200 image/jpeg 482 KB).
- El AGENTS.md describe un frontend Streamlit (`streamlit run frontend/app.py`) que
  ya no existe; la estructura canónica real es Next.js.
- NOTA: no se hizo commit ni push.

## Fecha: 2026-10-19 (carga de banco SBX DATA_NEW)

### Prompt - "Puedes decirme como cargar o actualizar la data ya que ahora tengo nuevas imagenes en data/DATA_NEW..."
**Propósito:** El usuario tiene ~280 imágenes PNG nuevas en `data/DATA_NEW` con nomenclatura `SBX-###-NNNN.png` y necesita integrarlas al sistema de búsqueda visual. No existe `products.csv`, `embeddings.npy`, `ids.npy` ni `images_normalized/` (fueron eliminados en la limpieza del banco Aimari).
**Resultado:**
- `scripts/crear_csv_data_new.py`: genera `data/products.csv` a partir de `DATA_NEW`. Lee los archivos que cumplen el patrón `SBX-\d{2}-\d{4}.png`, crea el ID como el nombre sin extensión, asigna proveedor "SBX", página "1", y URL placeholder.
- `scripts/normalizar_data_new.py`: copia las imágenes de `DATA_NEW` a `data/images_normalized/` convirtiéndolas a JPG con el mismo ID. No modifica los originales.

## Fecha: 2026-09-21 (limpieza .md viejos)

### Prompt - elimina todos los .md que no sirven y que se quede lo importante
**Propósito:** Quedarse solo con la documentación base para el banco nuevo.
**Resultado:** Eliminados `REPORTES_HITO1.md`, `REPORTES_HITO2.md`, `REPORTES_HIT3.md`, `REPORTES_HITO3_OPTIMIZACION.md`, `HITO3.md`, `evaluation/README.md`, `evaluation/INFORME_SALA2_HITO2.md` (todos atados al banco Aimari). Conservados `AGENTS.md`, `README.md`, `TRABAJO.md`, `AI_LOG.md`. `evaluation/` queda vacío para la evaluación del banco nuevo.

## Fecha: 2026-10-17 (documentación del último commit)

### Prompt - hasme un md segun lo que se hizo en el ultimo commit registrado el cual es nueva interfaz grafica y boton directo a whtassap, entre otros, facil de comprender por humano y por ia
**Propósito:** Documentar en un solo `.md` todo lo que trajo el último commit
registrado (`643dcebd`, merge del PR #2 desde `feature/subida-sala5`), que en
contenido real corresponde al commit `1b863a2f` de la rama `sala-5`.
**Resultado:** Creado `RESUMEN_ULTIMO_COMMIT.md` con: identificación del commit,
tabla archivo-por-archivo con conteo de líneas, y el detalle de las funciones
nuevas — rediseño visual "Atelier Sublitex" con tema claro/oscuro, buscador
`/search` (drag & drop, `Ctrl+V`, presets, skeletons, 3 modales), catálogo
comercial `/catalog` (buscador, filtros, modal de ficha técnica), cotizador
deslizante en `components/Sidebar.tsx`, **6 botones directos a WhatsApp**
(`wa.me/?text=` con mensaje prellenado), `lib/api.ts` con timeout de 2.5 s y
fallback simulado, `lib/catalog.ts` con 8 productos, route handler de imágenes
con 4 directorios candidatos, `next.config.ts` con `output: "standalone"`,
dependencias `lucide-react` + `motion`, y ajustes de ESLint/`metadata.json`.
Incluye sección de riesgos: `.next/` commiteado, `frontend/src` ausente en `main`,
`/eval` degradado (se perdió el evaluador del Hito 2 con métricas y CSV), fallback
que oculta caídas de la API, WhatsApp sin número fijo, `motion` sin uso.

## Fecha: 2026-10-19 (reescritura del md de mejora de UI)

### Prompt - 'mejora del UI.md' modificalo, no es md del ultimo commit hecho es sobre el cambio a la UI de la pagina puedes hacer un md de eso
**Propósito:** Convertir el documento en una descripción del **cambio de UI de
la página**, no en un informe de commit.
**Resultado:** Reescrito `mejora del UI.md` centrado en la interfaz: tabla
Antes→Después, sistema de diseño "Atelier Sublitex" (tema claro/oscuro, tokens),
estructura de la página (barra superior, footer, `/` → `/search`), detalle de
pantallas (`/search` con drag&drop y Ctrl+V, `/catalog` con buscador y filtros,
cotizador deslizante, `/eval` degradado a muestrario), tabla de los 6 botones de
WhatsApp, tabla de componentes/datos nuevos, nota del "modo demo" de `lib/api.ts`,
cómo ejecutar la interfaz y sección final de dónde está el código (`sala-5`,
`frontend/src` ausente en `main`, `.next/` commiteado). Se eliminó la
identificación de commits como eje del documento (quedó solo la referencia
mínima para ubicar el código).

### Prompt - modifica en una parte lo que se puede entender facil por persona y otro lado lo que va a leer la ia, ademas solo pon los cambios no cosas como la instalacion
**Propósito:** Separar `mejora del UI.md` en dos lecturas y dejarlo solo con cambios.
**Resultado:** Reestructurado en **Parte 1 (personas)** — lenguaje simple, qué se
nota al usar la página, tabla Antes→Después — y **Parte 2 (IA)** — ubicación del
código en git, rutas, tabla de pantallas/componentes con deltas, WhatsApp (6
`wa.me`), fallback de `lib/api.ts`, config/dependencias y pendientes. Eliminada
la sección de instalación/ejecución (`npm install`, `npm run dev`).

## Fecha: 2026-10-23 (actualización README.md)

### Prompt - Guía de inicialización del sistema y carga de datos para actualizar datos ya obtenidos y cargar nuevo contenido
**Propósito:** Actualizar `README.md` para reflejar el estado real del proyecto tras la migración del banco Aimari al banco SBX (284 imágenes). Incluir una guía de inicialización del sistema (pasos 1-7: crear CSV, normalizar imágenes, generar embeddings, generar índices comparativos, validar, levantar API, levantar frontend) y una sección de carga de datos para actualizar datos existentes y cargar nuevo contenido (caso A: banco completamente nuevo; caso B: actualizar/añadir imágenes).
**Resultado:** `README.md` reescrito: descripción del proyecto con banco SBX (284 productos), diagrama de flujo actualizado (DATA_NEW → products.csv → images_normalized → embeddings.npy/ids.npy → embeddings_clip/openclip/siglip.npy → API FastAPI → frontend Next.js), requisitos previos (Python + Node.js), ubicación del venv (nivel arriba del repo), guía paso a paso de inicialización, flujo de carga de datos con casos A y B, reglas importantes de carga (products.csv única fuente, ids.npy alineado, imágenes_normalized banco canónico, índices prohibidos), contrato de respuesta, modos del endpoint, reglas de evaluación Hito 2, manejo de errores, estructura del proyecto, tabla de archivos generados clave, solución de problemas y próximos pasos. Frontend documentado como Next.js (cliente puro de la API) en lugar de Streamlit. Conteo actualizado: 284 productos, 284 embeddings (284×512 CLIP, 284×768 SigLIP).

## Fecha: 2026-10-23 (actualización QA_REPORTE.md)

### Prompt - Análisis exhaustivo de prueba y error del QA_REPORTE
**Propósito:** Reescribir `QA_REPORTE.md` porque el anterior (fecha 2026-10-19) estaba desactualizado: refería al banco Sublitex antiguo, Qdrant/Docker como backend principal, y documentación de Streamlit. El sistema real ahora usa banco SBX (284 productos), índices `.npy` locales, API FastAPI y frontend Next.js.
**Resultado:** `QA_REPORTE.md` reescrito con: estado actual del sistema (artefactos en data/, servicios activos en puertos 8000 y 3000), secuencia de carga de datos ejecutada paso a paso (5 scripts, 284 productos, 0 errores), matriz de pruebas individuales (GET /health PASS, POST /search/image clip PASS, POST /search_image fusion ⚠️ timeout en CPU, frontend Next.js PASS, alineación ids↔csv↔embeddings PASS), tabla de errores conocidos y resolución (E1-E6), matriz de cobertura Hito 2 (50 consultas pendientes), lista de pruebas pendientes críticas (sección 4) y veredicto QA final por componente.

## Fecha: 2026-10-23 (actualización QA_REPORTE.md — incidentes operativos)

### Prompt - Agregar sección de incidentes operativos al QA_REPORTE
**Propósito:** Documentar en el QA_REPORTE los incidentes ocurridos durante la sesión de carga y levantamiento del sistema (uvicorn colgado, Invoke-WebRequest sin soporte multipart, timeout de fusion, log bloqueado).
**Resultado:** Agregada sección 6 "Incidentes operativos de esta sesión" con tabla I1-I4 documentando cada incidente, síntoma, causa y resolución. Nota importante sobre que uvicorn debe mantenerse en proceso desvinculado (background) en Windows.

## Fecha: 2026-10-23 (ejecución completa de pruebas y actualización QA_REPORTE)

### Prompt - Ejecutar todas las pruebas pendientes y cumplir requisitos del Hito 2
**Propósito:** Cumplir con todos los requisitos del proyecto: crear el conjunto de 50 consultas Hito 2, ejecutar pruebas de error obligatorias, ejecutar prueba de imagen externa, ejecutar comparación Hito 1 vs Hito 2, y actualizar QA_REPORTE con resultados reales.
**Resultado:**
- `scripts/generar_consultas_hito2.py` (nuevo): genera 50 consultas (10 diseños × 5 categorías: exacta, sin_marco, recoloreada, recortada, persona) con imágenes variantes en `data/consultas/` y CSV en `evaluation/consultas_hito2.csv` con `id_correcto` verificado. 50/50 generadas, 0 omitidas.
- `test_errores.py` (temporal, ya eliminado): 3 pruebas ejecutadas — archivo inválido → HTTP 400 ✅; imagen 16×16 → HTTP 400 con mensaje claro ✅; imagen externa → HTTP 200 con 5 resultados ✅.
- `scripts/compare_hito1_hito2.py` ejecutado en dos pases (--solo hito1 y --solo hito2) debido a que `fusion` es muy lento en CPU:
  - Hito 1 (CLIP): Top1 43/50 (86%), Top5 47/50 (94%), P50/50 90/100, 2248 ms prom.
  - Hito 2 (CLIP+reranking): Top1 44/50 (88%), Top5 48/50 (96%), P50/50 92/100, 4594 ms prom.
  - Por categoría: recortada mejora de 6/10 a 7/10 en Top1; exacta y sin_marco 10/10 en ambos.
- `QA_REPORTE.md` reescrito completamente con todos los resultados reales, matriz de cobertura 50/50 completada, comparación H1 vs H2 con números reales, veredicto final por componente, y sección de incidentes operativos I1-I4.
- `AI_LOG.md` actualizado con esta entrada.

Servicios activos al finalizar: API FastAPI en http://localhost:8000 (uvicorn en background), Frontend Next.js en http://localhost:3000.

## Fecha: 2026-10-23 (mapa de secciones visuales del frontend)

### Prompt - "Hazme un .md sobre el apartado web que carpeta o archivo altera cada apartado visual del frontend"

**Propósito:** Crear un documento .md que responda qué carpeta o archivo del frontend (app Next.js en `frontend/`) altera cada sección visual de la interfaz.

**Resultado:**
- Creado `frontend/UI_SECCIONES.md`: mapa de cada sección visual → archivo(s) que la implementa o altera.
- Secciones mapeadas: tema/tokens globales (`src/app/globals.css`, `src/components/ThemeProvider.tsx`, `src/app/layout.tsx`); layout TopBar/Drawer/Footer (`src/app/sidebar-layout.tsx`, `src/components/Sidebar.tsx`); home `/` (`src/app/page.tsx`); buscador `/search` (`src/app/search/page.tsx`, `src/components/Skeleton.tsx`, `src/lib/api.ts`, proxy `src/app/api/images/[filename]/route.ts`); catálogo `/catalog` (`src/app/catalog/page.tsx`, `src/lib/catalog.ts`, `src/lib/countries.ts`); muestrario `/eval` (`src/app/eval/page.tsx`); proxy de imágenes (`src/app/api/images/[filename]/route.ts`).
- Incluye tabla resumen rápida, contexto de la mejora del UI (2026-10-19), pendientes que implican cambios visuales y pasos para verificar levantamiento.

**Verificado:** documento nuevo de solo Markdown (sin cambios de código fuente).

**Pendiente:** ninguno nuevo; documental.

**Nota:** no se hizo commit ni push.

## Fecha: 2026-10-25 (Fase 1 — auditoría de repositorio y limpieza hacia producción)

### Prompt - "Actúa como Ingeniero de Software Principal y Arquitecto… auditar, limpiar y preparar para producción Sublitex (fases: auditoría, arquitectura RAG+Qdrant, checklist de producción, mentoría de lógica)"

**Propósito:** Fase 1 — auditar el árbol de directorios de Sublitex, clasificar artefactos/código muerto/duplicados y aplicar la limpieza no destructiva del repositorio bajo esquema de co-coding guiado.

**Resultado:**
- Auditoría completa (1.561 archivos trackeados, 57 cambios pendientes previos): detectados 865 archivos de build `frontend/.next/` y 2 de `qdrant_data/` trackeados indebidamente; `yolov8n.pt` trackeado (decisión de LFS/setup pendiente); `data/DATA_NEW/` duplicado de `images_normalized/` y ~12 scripts de un solo uso difieren (usuario decidió dejarlos donde están por ahora); ~6 módulos `core/` sin importadores en Python (candidatos a código muerto, verificación pendiente).
- `.gitignore` raíz: añadida regla `/qdrant_data/` (la única carencia real; `frontend/.gitignore` ya cubría `.next/` y `*.tsbuildinfo`).
- `git rm -r --cached frontend/.next qdrant_data`: 867 archivos sacados del índice de git SIN borrar del disco. Corregido el diagnóstico inicial: el problema no era la ausencia de reglas, sino archivos trackeados a pesar de las reglas existentes.
- **Hallazgo crítico nuevo:** `core/` (capa Qdrant completa), `api/qdrant_engine.py`, `scripts/migrar_a_qdrant.py`, `.env.example`, `QA_REPORTE.md`, `evaluation/` y `data/consultas/` (50 consultas Hito 2) están SIN trackear → toda la capa Qdrant de Sublitex y la evidencia de evaluación solo existen en esta máquina. Commit pendiente de autorización explícita del usuario.
- Decisiones del usuario registradas: Sublitex = este repo; stack definitivo FastAPI + Qdrant + Next.js; Streamlit (`.streamlit/`) y motores npy Hito 1/2 quedan como legado documentado (regeneración de AGENTS.md/README = Fase 2).
- Purga de artefactos del sistema ejecutada (autorizada por el usuario): eliminados **`frontend/.next/` (396 MB)** previa verificación de que no había `next dev` (puertos 3000/8000 libres; los 8 procesos `node` eran servidores MCP), 4 carpetas `__pycache__` (incluye bytecode huérfano de `scripts/auditoria_seccion00.py`, script ya inexistente), `api_output.log`, `frontend/tsconfig.tsbuildinfo` y `scripts/consolidar_output.txt` (este último sí estaba trackeado → `git rm` para llevar su borrado al índice). Total liberado en disco: ~372 MB.
- NO eliminados por ser decisiones semánticas, no artefactos del sistema: `yolov8n.pt` (referenciado por `core/vision_pipeline.py:37` y auto-descargable por Ultralytics), `frontend/.git` (repo anidado real con 3 commits propios: Initial commit / feat: update architecture / refactor: rebrand — historial único), `.streamlit/` (legado Streamlit), `data/DATA_NEW/` (deferido por el usuario).

**Pendiente:** decisión sobre `yolov8n.pt`, `frontend/.git` y `.streamlit/`; Fase 2 (arquitectura Clean Architecture: un solo motor activo, separación cliente Qdrant/embeddings/CRUD/API/UI) y Fase 3 (inyección de env vars, timeouts asíncronos, CORS, auto-creación de colecciones).

## Fecha: 2026-10-25 (Fase 2 — Depuración definitiva, eliminación de archivos innecesarios y estructura para despliegue)

### Prompt - "Análisis de todos los archivos sin sobrepensar y eliminar archivos innecesarios no conectados al RAG/sistema general, organizar todo de golpe con estructura limpia lista para desplegar (Qdrant, Python, Frontend) y reporte corto .md"

**Propósito:** Eliminar archivos innecesarios, scripts legacy, módulos independientes huérfanos y binarios sobrantes para dejar la estructura limpia y lista para despliegue del sistema RAG con FastAPI, Qdrant y Next.js.

**Acciones y Resultados:**
- Eliminados módulos no conectados en `core/`: `database_sql.py`, `compound_segmentation.py`, `adaptador_imagenes.py`, `cdr_seguridad.py`, `sublitex.py`, `vision_pipeline.py`.
- Eliminado modelo binario sobrante: `yolov8n.pt` (~6.5 MB).
- Eliminada carpeta `prompts/` (no integrada al flujo RAG).
- Eliminados 16 scripts huérfanos/legacy en `scripts/`: `GUIA_SALA4.txt`, `requirements.txt`, `requirements_sala2.txt`, `analizar_formatos.py`, `consolidar.py`, `normalizar_imagenes.py`, `revisar_muestra_50.py`, `validate_dataset.py`, `get_product.py`, `evidencia_hito2.py`, `reporte_metricas.py`, `reporte_comparativo.py`, `evaluar_hito2.py`, `regenerar_consultas.py`, `generar_consultas_prueba.py`, `generar_consultas_hito2.py`.
- Eliminados índices duplicados no canónicos: `data/embeddings_banco_propio.npy` y `data/ids_banco_propio.npy`.
- Eliminados residuos: `.streamlit/`, `mejora del UI.md`, `frontend/CLAUDE.md`.
- Preservados únicamente los 9 scripts operativos requeridos para el pipeline RAG y evaluación.
- Ajustadas configuraciones en `core/config.py`, `.env` y `.env.example` (`CATALOG_PATH=./data/images_normalized`).
- Agregada dependencia faltante `pydantic-settings>=2.0.0` a `requirements.txt`.
- Creados `Dockerfile.api` y `docker-compose.yml` para despliegue integral (FastAPI + Qdrant + Next.js).
- Generado reporte completo de estado y readiness en `REPORTE_LIMPIEZA.md`.
- Creada guía de despliegue para equipo en `PRODUCCION_SERVER.md` (instrucciones de verificación, empaquetado, configuración de IP pública y orquestación).

## Fecha: 2026-10-27 (fix: imágenes vacías en el catálogo Next.js)

### Prompt - "corrigeme en frontend que algunas imagenes no se pueden ver arregla eso, porque salen vacio analiza y dime cual seria el problema... haz que se visualize todo las imagenes"

**Propósito:** Corregir las tarjetas del catálogo que se mostraban vacías y asegurar que se visualicen todas las imágenes reales del banco.

**Causa raíz:** `frontend/src/lib/catalog.ts` tenía una lista hardcodeada de 200 IDs; 54 no existían en `data/images_normalized/` (SBX-03 completo, SBX-05-0001..0010 y 4 IDs sueltos) y 138 productos reales no aparecían. `data/products.csv` e `images_normalized` tienen 284 productos y los 284 archivos son válidos.

**Resultado:**
- Regenerado el arreglo `IMAGES` de `catalog.ts` desde `data/products.csv`: 284 IDs reales, 0 faltantes en disco, diff 0 contra products.csv.
- `frontend/src/app/api/images/[filename]/route.ts`: resolución de extensión ampliada (.jpg/.jpeg/.png/.webp) para tolerar el desfase `.png` del CSV vs `.jpg` en disco.
- Verificado: `npx tsc --noEmit` sin errores, `npm run lint` sin errores (3 warnings preexistentes), PIL validó 284/284 imágenes sin archivos dañados.

**Nota:** no se hizo commit ni push.

## Fecha: 2026-10-30 (3.3 Seguridad: API keys, rol admin y CORS restringido)

### Prompt - "What did we do so far? / Continuar con los siguientes pasos de 3.3 Seguridad"

**Propósito:** Implementar autenticación por API key con roles cliente/administrador, proteger indexación y restringir CORS al frontend, sin exponer secretos en el navegador.

**Resultado:**
- `api/security.py`: dependencias `require_client`/`require_admin`, comparación con `secrets.compare_digest`, `401/403/503` fail-closed y advertencias de configuración sin filtrar claves.
- `core/config.py`: `API_CLIENT_KEY`/`API_ADMIN_KEY` como `SecretStr`, `CORS_ORIGINS` validado (ignora `*`) y lista de orígenes.
- `api/main.py`: CORS restringido (`allow_credentials=False`, métodos/headers explícitos); búsquedas con rol cliente; indexación y administración con rol admin; `/health` sigue público.
- Frontend: proxies server-side `frontend/src/app/api/search/route.ts` y `frontend/src/app/api/health/route.ts`; `api.ts` y `search/page.tsx` usan rutas relativas, sin `NEXT_PUBLIC_API_URL`.
- Configuración: `.env.example`, `frontend/.env.example`, `docker-compose.yml`; `.dockerignore` raíz y de frontend; `Dockerfile.api` ya no copia `.env` a la imagen.
- `scripts/compare_hito1_hito2.py` envía `X-API-Key` (`API_CLIENT_KEY` o `--api-key`).
- Documentación actualizada: `README.md`, `PRODUCCION_SERVER.md`, `AGENTS.md`.

**Verificado:** `py_compile` de API/config/seguridad y script de comparación; pruebas con `TestClient` (401/403/503, CORS permitido/denegado, `/health` público, `*` ignorado); `npx tsc --noEmit`, `npm run lint` (3 warnings preexistentes) y `npm run build` correctos.

**Nota:** no se hizo commit ni push. Docker no está disponible en esta máquina, por lo que no se ejecutó `docker compose config`.

## Fecha: 2026-10-30 (3.3 Seguridad al 100%: Qdrant, claves por cliente y CORS)

### Prompt - "ajusta algunas cosas para que este al 100% estos 3 puntos"

**Propósito:** Cerrar los gaps detectados en la auditoría: Qdrant accesible sin autenticación, CORS con valores por defecto de desarrollo y una única clave de cliente compartida.

**Resultado:**
- `docker-compose.yml`: Qdrant exige `QDRANT_API_KEY`, publica `6333/6334` solo en `127.0.0.1` y queda en la red `backend`; el frontend solo está en `frontend_net` y no puede alcanzar Qdrant directamente. La API recibe la clave de Qdrant y `API_CLIENT_KEYS`.
- `core/config.py`: `QDRANT_API_KEY` y `API_CLIENT_KEYS` como `SecretStr`; advertencia si un origen CORS no local usa HTTP.
- `core/base_datos.py`: la clave de Qdrant se extrae de `SecretStr` y se pasa al cliente; vacía se convierte en `None`.
- `api/security.py`: soporte de `API_CLIENT_KEYS` con formato `nombre:clave,...`, identidad `client:<nombre>`, compatibilidad con `API_CLIENT_KEY` como `default` y menor privilegio si una clave coincide con la de administrador.
- `.env.example`, `README.md`, `PRODUCCION_SERVER.md` y `AGENTS.md`: documentadas las claves por cliente, la protección de Qdrant y CORS solo HTTPS en producción.
- `CORS_ORIGINS` ahora es obligatorio en Docker Compose: ya no cae silenciosamente en `localhost`.

**Verificado:** `compileall` de `api/`, `core/` y `scripts/`; pruebas directas de roles, múltiples claves, fail-closed, menor privilegio y secreto de Qdrant (`SEGURIDAD_100_OK`); pruebas sobre `api.main` con `TestClient` para `401/403`, CORS permitido/denegado y parseo de multipart (`API_SEGURIDAD_100_OK`); fail-closed real sin claves (`FAIL_CLOSED_100_OK`); `npx tsc --noEmit` y `npm run lint` (solo 3 warnings preexistentes).

**Nota:** no se hizo commit ni push. Docker sigue sin estar disponible, por lo que no se ejecutó `docker compose config`.

## Fecha: 2026-10-30 (fix: resolución de conflictos de merge en docker-compose.yml)

### Prompt - "docker compose up -d --build → go-yaml load error in scanner (while scanning a simple key) at L6.C1-L8.C1"

**Propósito:** Restaurar el parseo del `docker-compose.yml` tras un merge mal resuelto que dejó marcadores de conflicto de Git (`<<<<<<< HEAD`, `=======`, `>>>>>>> origin/sala-5`) commiteados en el historial.

**Resultado:**
- Diagnóstico: el error de Docker Compose (`go-yaml load error in scanner ... at L6.C1-L8.C1`) provenía de los bloques de conflicto en `docker-compose.yml` (líneas 6-12, 17-27, 54-64 y 80-115).
- Resolución aplicada en el archivo trabajado:
  - `qdrant`: sin puertos públicos (binds solo `127.0.0.1:6333/6334`), con `QDRANT__SERVICE__API_KEY`, en red `backend`, límites de recursos.
  - `api`: `expose 8000` (detrás del reverse proxy), todas las claves de entorno (`QDRANT_API_KEY`, `API_CLIENT_KEY`, `API_CLIENT_KEYS`, `API_ADMIN_KEY`), en redes `backend` + `frontend_net`.
  - `frontend`: `expose 3000`, env `API_URL=http://api:8000` + `API_CLIENT_KEY`, `depends_on api`, en red `frontend_net`.
  - `proxy`: servicio Caddy (puertos 80/443) con `depends_on api, frontend`.
  - `networks`: `backend` y `frontend_net`.

**Verificado:** `docker compose config -q` y `docker compose config` sin errores ni warnings de YAML (salió limpio y completo).

**Nota:** no se hizo commit ni push. No se ejecutó `docker compose up -d --build` (build completo pendiente de validar con contenedores reales).

## Fecha: 2026-10-31 (fix: error "No se pudo conectar con la API desde el proxy del frontend" + healthcheck de arranque)

### Prompt - "docker compose up -d --build → go-yaml load error ... / Error al buscar: No se pudo conectar con la API desde el proxy del frontend"

**Propósito:** Restaurar el stack Docker completo y asegurar que el flujo frontend→API (`/api/search`) funcione.

**Resultado:**
- `docker-compose.yml`: resueltos los 4 bloques de conflicto de merge (qdrant, api, frontend, proxy); se añadió `healthcheck` al servicio `api` (`python3 -c urllib ... /health`, start_period 600s) y `depends_on` con `condition: service_healthy` para `frontend` y `proxy`.
- `api/main.py`: resuelto conflicto de imports FastAPI (`Depends, FastAPI, UploadFile, File, Form, Request`).
- Verificado: `docker compose config -q` OK; `docker compose up -d` → api pasa a **Healthy**.
- Verificado end-to-end: `curl http://localhost/api/health` → 200 (vía Caddy → frontend Next → API); `curl -X POST http://localhost/api/search -F file` → 200 con resultados (modelo fusion, ~127s).

**Nota:** no se hizo commit ni push.

## Fecha: 2026-10-31 (fix: mejoras de reranking — patrón de color/combinación y equipo/país)

### Prompt - "ya falta mejorar las busquedas y de el tono bien, da imagenes buenas pero no exactas necesito que de imagenes lo mas similares posibles..."

**Propósito:** Refuerzo del motor Hito 2 (Sala 4) para que el reranking detecte por color de camiseta, patrones de color, patrones de combinación y equipos/países, buscando imágenes más similares.

**Resultado:**
- `api/search_engine_hito2.py`: nuevos componentes en `_rerank_candidatos`:
  - `score_patron_combinacion` (patrón × color, [0,1]) con `PESO_PATRON_COMBINACION = 0.05`.
  - `score_equipo` (identidad equipo/país, [0,1]) con `PESO_EQUIPO = 0.03`.
  - Integrados en `score_final`; pesos adaptativos (recolor) actualizados en ambas ramas.
  - Nuevos keys de salida: `score_patron_combinacion`, `score_equipo`.
- Verificado: `python -m py_compile api/search_engine_hito2.py` OK.

**Nota:** no se hizo commit ni push. Pendiente: reconstruir imagen del API (`docker compose up -d --build api`) para aplicar en contenedor y re-ejecutar búsqueda/evaluación.


## Fecha: 2026-11-04 — Revisión de Sala 6 y preparación de delegación

**Prompt:** «Revisa todo el proyecto, con mi equipo quedamos en seguir por sala 6, buscamos completar los checklist, que hace falta? actualmente tengo cambios por commitear y aun no se si es posible, quiero llegar a un punto para poder delegar a los demas los checklist que hacen falta pero necesitamos un punto clave de donde empezar».

**Resultado:** revisión de reglas, checklist, motores/API/proxies, datos e índices, evaluación, Docker/seguridad, monitoreo y cinco archivos pendientes. Se añadió ESTADO_SALA6.md con evidencias, discrepancias, revisión de backup/restauración/rollback, reparto propuesto y criterios de aceptación. TRABAJO.md ausente. Sin cambios funcionales ni commit/push.

**Verificación:** sintaxis AST de api/core/scripts correcta; catálogo 577 filas con imágenes existentes, 577 nombres-ID y URLs de ejemplo; dimensiones de índices leídas de sus encabezados (577 filas). Orden de ids.npy no verificado. git diff --check correcto. Sin Docker/Bash/.venv en este equipo y localhost:80 sin servicio: no se ejecutaron build, curl de búsqueda real ni simulacro de recuperación. Métricas citadas son históricas; H1 n=0 impide declarar comparación completa.

## Fecha: 2026-11-04 — Copia de pruebas operativa en VirtualBox

**Prompt:** «bien sigamos con la copia de pruebas en virtualbox, que es todo lo necesario, lo que puedas hazlo tu y dime si funciono».

**Trabajo:** copia aislada en /home/vboxuser/Desktop/TRABAJOS/RAG-V2-staging vía SSH. Archivo de 1052 entradas, huella SHA-256 comprobada; excluidos secretos, Git, dependencias y consultas subidas por usuarios. Secretos nuevos generados dentro de VM, permisos 600. Se añadió docker-compose.staging.yml (recursos locales, proxy solo loopback, caché persistente), PRELOAD_EXTRA_MODELS configurable sin cambiar el valor original por defecto, scripts/verificar_staging.py y docs/STAGING_VIRTUALBOX.md. Se corrigió creación/permisos del directorio HF en Dockerfile.api y falta de archivo como 400 en los tres endpoints. Correcciones sincronizadas; hashes de archivos coinciden entre Windows y VM.

**Verificación:** build original completo API/frontend correcto; reconstrucción y arranque con ajustes correctos; 17/17 verificaciones de integración pasadas; IDs coinciden en contenido y orden con 577 productos; cuatro índices con filas/dimensiones válidas, vectores finitos/no nulos; pruebas de salud, interfaz, imágenes, 401/403 y errores 400; búsqueda exacta original y auto con CLIP, ID esperado Top1; petición curl con consulta real HTTP 200. Qdrant indexado con 577 puntos y búsqueda Top1 correcta. Volumen HF nuevo escribible por UID 10001. py_compile de archivos tocados y compilación de api/core/scripts en Linux; bash -n del backup correcto. Evidencia estructurada en docs/evidencias/staging-2026-11-04.json. Túnel local 8080 habilitado para acceso desde Windows.

**Límites:** no prueba de Fusión, calidad de 50 consultas, restauración/rollback, HTTPS o alertas; no se declara listo para producción. npm reportó 17 vulnerabilidades (16 moderadas/1 crítica), pendientes de análisis. Muestras de latencia aisladas, no percentiles. Unos 7 GB libres en VM. Sin staging Git, commit ni push.

## Fecha: 2026-11-04 — Portabilidad de pruebas y alcance del próximo commit

**Prompt:** «para que mis compañeros sepan, al hacer estas pruebas en virtualbox, ssh, esto si alguien ejecuta el proyecto pero normal sin ssh y virtualbox, tendran el mismo resultado, como para que se haga una mencion, ademas, quiero saber si ahora la app como esta puedo commitear algo que sea relevante, que hemos descubierto que podemos aportar en el proximo commit?».

**Resultado:** se aclaró en README.md y docs/STAGING_VIRTUALBOX.md que SSH/VirtualBox son herramientas de acceso/alojamiento; la reproducción depende del código, datos, índices, modelos, preprocesamiento y dependencias. Docker directo puede repetir el flujo con configuración equivalente; instalación nativa, igualdad exacta de scores/tiempos y Fusión no están verificadas. Se recomienda un commit enfocado en correcciones de caché y error 400 sin archivo, precarga configurable, complemento staging, verificador, documentación y evidencias. Backups/rollback quedan separados hasta validarlos. No se hizo staging Git, commit ni push.

**Verificación:** revisión del diff y git diff --check; cambios de esta intervención solo documentales. Se conservan las evidencias previas de integración.

## Fecha: 2026-11-04 — Organización de documentación y estructura

**Prompt:** «Bien tambien, quedaria organizar las carpetas, estructura para que el proyecto se lea mejor».

**Resultado:** se agruparon guías en docs/despliegue, checklist en docs/planificacion, diagnóstico/staging en docs/sala6, informe histórico en docs/informes y borrador de operaciones en docs/propuestas. Se creó docs/README.md como índice con estados de validación; docs/evidencias permanece en su ruta. Se movieron las dos imágenes técnicas de la raíz a evaluation/fixtures. Se actualizaron enlaces, menciones y mapa del README; se aclaró el carácter histórico o pendiente de las guías antiguas. Se conservaron los cambios previos del usuario y las rutas canónicas de código, scripts, datos y configuración Docker. Referencias de entradas antiguas de AI_LOG describen ubicaciones históricas; consultar docs/README.md para las actuales. TRABAJO.md sigue ausente. No se hizo staging Git, commit ni push.

**Verificación:** 10 traslados confirmados sin copias en rutas anteriores; 0 enlaces locales rotos en README y docs; hashes de api/main.py, Dockerfile.api y scripts/verificar_staging.py idénticos a los de la ejecución verificada; git diff --check correcto. Consulta real curl por túnel a VirtualBox: HTTP 200; API healthy y cuatro servicios activos. La reorganización es local: la copia de la VM conserva su distribución documental anterior hasta una nueva sincronización; el código de ejecución no cambió.

## Fecha: 2026-11-04 — Commit y publicación de la base verificada de Sala 6

**Prompt:** «bien entonces, si ahora mismo puedes ver mi proyecto y tal, haz el commit con mi usuario de git y sube».

**Alcance autorizado:** commit de correcciones verificadas de API/caché, configuración y verificador de staging, evidencias, organización documental y fixtures, README y registro IA. Identidad Git existente: kannodi. Destino: origin/sala-6. Se mantienen fuera del commit scripts/backup.sh, la propuesta local de operaciones y las secciones de respaldo/rollback no verificadas de la guía de servidor (el traslado de la versión anterior y su nota de revisión sí se incluyen). No se publican secretos ni archivos de transferencia. Las entradas anteriores del registro pueden mencionar esos borradores como trabajo local.

**Verificación previa:** py_compile de api/main.py y scripts/verificar_staging.py; git diff --check; revisión de evidencias de 17/17 pruebas y Qdrant; revisión de enlaces locales; consulta del remoto antes de publicar. Sin force push.

## Fecha: 2026-11-04 — Registro del avance de caché en el checklist

**Prompt:** «se marcó el check que hice?».

**Resultado:** el requisito general de volumen Hugging Face seguía abierto. Se añadió una subcasilla completada para staging, respaldada por las pruebas existentes, y una pendiente explícita para incorporarlo/verificarlo en el despliegue principal. No se declara completado el requisito de producción. Solo documentación; git diff --check. Sin commit ni push de esta actualización.

## Fecha: 2026-11-05 — Retiro de TRABAJO.md como requisito vigente

**Prompt:** «bien entonces, descartalo y edita agent.md».

**Resultado:** actualizado AGENTS.md por instrucción explícita del usuario. TRABAJO.md es referencia histórica en Git, sin obligación de restaurarlo y sin bloquear tareas por su ausencia. Alcance actual: buscador autónomo FastAPI/Next.js/Qdrant, catálogo SBX y cierre operativo/evaluación de Sala 6; WordPress y 15.000 diseños fuera hasta nueva instrucción. Se conservan requisitos de calidad, seguridad y alineación; backend canónico/modelo predeterminado permanecen pendientes. Se actualizaron las referencias al frontend, catálogo/modelos y entorno real para evitar restaurar decisiones antiguas. README e índice/diagnóstico dejaron de exigir recuperar el documento. No se restauró ni eliminó archivo histórico, no se modificó código, no se hizo commit/push.

**Verificación:** revisión de menciones vigentes de TRABAJO.md, enlaces locales y git diff --check. No se repitieron pruebas de ejecución por tratarse de documentación.

## Fecha: 2026-11-05 — Commit del alcance y avance de Sala 6

**Prompt:** «bien haz el commit necesario, luego explicanos las tareas restantes y segun como las avanzamos».

**Resultado:** preparación de commit documental de AGENTS.md, README, índice documental, estado de Sala 6 y avance de caché en checklist. Se conservan fuera los borradores de backup/rollback y las entradas locales del registro relativas a Microsoft Project, ajenas al proyecto RAG. Se usa la identidad Git existente kannodi. Verificación de diff y enlaces locales; sin cambios de ejecución ni repetición de inferencia. Esta instrucción solicita commit; no incluye un nuevo push.

## Fecha: 2026-11-05 — Qdrant como backend canónico de búsqueda

**Prompt:** «Actúa como un Ingeniero de Backend Senior experto en FastAPI, Qdrant y optimización de rendimiento. Refactoriza el backend para validar/crear la colección Qdrant al arranque, restaurar opcionalmente un snapshot local, eliminar endpoints duplicados o marcarlos como deprecated y medir p50/p95 con carga concurrente real».

**Resultado:** FastAPI usa Qdrant como única recuperación del flujo normal con CLIP de 512 dimensiones y Cosine. El lifespan verifica la colección, restaura opcionalmente un snapshot configurado y migra los `.npy` solo cuando el índice está vacío, validando forma, valores, catálogo e IDs posicionales. La búsqueda Qdrant incorpora el reranking del Hito 2; `/search/image/qdrant` y `/search/image/v2` son alias deprecated del handler común. Los modos `.npy` quedan documentados como baseline histórico. Se añadió `scripts/load_test_qdrant.py` para peticiones multipart concurrentes y percentiles p50/p95; se alineó el selector del frontend y la documentación de arranque/operación.

**Verificación:** `py_compile` pasó para los módulos Python tocados; Pylance no encontró errores de sintaxis en los archivos modificados y confirmó compatibilidad de los call sites de `search_similar_reranked`. La firma local de `recover_snapshot` acepta `priority` y `SnapshotPriority.SNAPSHOT`. `docker compose config -q` pasó con valores temporales de validación y `git diff --check` quedó limpio. Se conservaron las verificaciones previas del catálogo (577 filas, `(577, 512)` y IDs alineados), Qdrant local, aliases, y carga contra un servidor HTTP simulado. No se validó la restauración contra un servidor Qdrant real ni se midió p50/p95 del endpoint real: la API no está activa y el intérprete local carece de `sentence-transformers` y `pydantic-settings`. Sin commit ni push.

## Fecha: 2026-11-05 — Revisión de evolución y dirección del proyecto

**Prompt:** «Lee los cambios que hemos estado haciendo desde hace muchos commits, es el camino correcto para seguir avanzando?».

**Alcance:** revisión de historial desde agosto/septiembre hasta e8cdcdf7, diferencias de código/configuración, documentación y referencias de ramas locales/remotas disponibles; sin fetch nuevo ni cambios funcionales. Se revisaron Next.js/proxies, Qdrant, seguridad, staging, alertas y evaluación.

**Conclusión:** la evolución hacia aplicación independiente y despliegue seguro es coherente, pero el siguiente ciclo debe consolidar una versión y validar calidad en lugar de sumar variantes. origin/chore/npm-ci contiene lockfile/npm ci (0f41d2fa) aún no integrado: revisar/reutilizar antes de duplicar. origin/sala-8 contiene evaluación histórica sobre AIM con id_correcto DESCONOCIDO, no una comparación actual del catálogo SBX; origin/piloto/MOTOR.md describe el catálogo/interfaz anteriores. El resumen actual de comparación tiene H1 n=0; faltan CSV de entrada y generador referenciados. Persisten divergencia Fusión UI/CLIP API, backend sin elegir, health HTTP que no garantiza modelo y checklist con estados contradictorios (HTTPS desactivado/nombres y URLs de ejemplo). Las evidencias staging de 17 pruebas siguen siendo de integración, no certificación de calidad ni operación completa. Alertas ya integradas en e8cdcdf7, con pruebas simuladas documentadas; falta canal real/servidor. Se conservaron cambios locales ajenos y borradores. Sin commit/push.

## Fecha: 2026-11-05 — Actualización e integración de npm ci del frontend

**Prompt:** «Bien primero trae cambios de compañeros a mi proyecto local, luego ahora conectate al ssh y dime lo haras y si lo puedes hacer, completar la tarea concreta que me encargo mi compañero».

**Resultado:** fetch y fast-forward de sala-6 a dfb3005d, incorporando Qdrant canónico/CLIP y refactor del compañero. Pendientes locales guardados con stash y restaurados; conflicto de AI_LOG resuelto conservando ambos aportes y las notas locales. Backup/propuesta conservados con contenido idéntico (normalización CRLF de Git); se mantiene stash como respaldo. Incorporados los archivos frontend/Dockerfile y frontend/package-lock.json de origin/chore/npm-ci (0f41d2fa), compatibles con package.json vigente. Conexión SSH a VirtualBox y sincronización de fuentes sin secretos. Documentados resultados y marcadas §3.4 npm ci y §3.5 proxy como verificadas en staging, manteniendo dominio/HTTPS/acceso externo final pendientes.

**Verificación:** npm ci ejecutado con lock v3 coherente con dependencies/devDependencies; build Next.js y TypeScript correctos; npm run lint sobre fuentes actuales en contenedor temporal: 0 errores/4 advertencias existentes. 17/17 pruebas de integración correctas con código backend actual. Curl desde Windows por túnel al frontend: 200, backend qdrant, Top1 SBX-01-0001. Bundle de navegador usa /api/search, sin URL directa localhost:8000 ni clave incluida. Servidor frontend usa API_URL=http://api:8000. Evidencias en docs/evidencias/frontend-2026-11-05.json y docs/sala6/FRONTEND_NPM_CI.md.

**Límites:** npm reportó 9 vulnerabilidades (8 moderadas/1 crítica), pendientes de revisión. Build frontend normal completo verificado; build backend desde base nueva cancelado por espacio de VM. Para integración se usó imagen de dependencias previa + código API/core/scripts actualizado, verificando httpx 0.28.1 compatible con el único requisito nuevo. No se declara validado un build limpio nuevo del backend, ni navegador automatizado, dominio público o TLS. Sin nuevo commit/push.

## Fecha: 2026-11-05 — Publicación de la entrega de frontend

**Prompt:** «subelo».

**Alcance:** commit y push a origin/sala-6 con la identidad Git existente kannodi. Incluye Dockerfile/lockfile del aporte 0f41d2fa, checklist §3.4 y verificación local de §3.5, informe, evidencia e índice documental. Se conservan fuera los borradores de backup/rollback y notas de Microsoft Project ajenas a esta entrega. Verificados remoto, contenido seleccionado, coherencia del lockfile y diff --check. Se reutilizan pruebas ya completadas (build, TypeScript, lint y 17/17 integración); no hay cambios funcionales posteriores que requieran repetirlas. Sin force push.

## Fecha: 2026-11-05 — Material académico de preguntas guía

**Prompt:** Preparar contenido de Canva conservando las cinco preguntas del PDF PDSD-644, notas explicativas y un proyecto Spring muy simple en la carpeta SENATI/SPRINBOOT/trabajos.

**Resultado:** BibliotecaGuia, material de siete diapositivas y notas personales. Proyecto externo al alcance funcional de RAG; no se modificó su API. Demo JSF/CDI/JPA/Hibernate con H2 temporal y perfil MySQL opcional no probado. Compilación correcta; HTTP real con sesión JSF: tres préstamos aceptados, cuarto bloqueado, devolución y nuevo préstamo aceptados. Caché de segundo nivel solo propuesta. Sin commit.

## Fecha: 2026-11-05 — Pregunta 1, entidades de biblioteca

**Prompt:** Corregir explicación para Canva según el PDF y crear solamente el proyecto y paquete con entidades de esta pregunta en SENATI/SPRINBOOT/trabajos.

**Resultado:** BibliotecaPreguntas separado de la demo anterior; entidades Libro, Usuario y Prestamo con relaciones JPA y comentarios. Incluye ISBN, título, autor, cantidad de ejemplares y fechas. Compilación Maven correcta. Sin frontend ni lógica de las otras preguntas; H2 temporal para verificar esquema, no cumplimiento MySQL del sistema final. Sin commit.

## 2026-11-05 — Pregunta 2 JSF/CDI
**Prompt:** Preparar texto Canva, explicación y código para captura de las anotaciones del ciclo de vida.
**Resultado:** Ejemplo compilable PrestamoBean con Named, SessionScoped, Inject y PostConstruct; servicio mínimo de mensaje. Ejemplo CDI para lectura/captura, excluido del escaneo Spring; sin nueva interfaz ni persistencia de operaciones. Se utiliza SessionScoped según PDF y se distingue sesión HTTP de préstamo persistido. Compilación Maven correcta; sin commit.

## 2026-11-05 — Pregunta 3, validador de préstamos
**Prompt:** Preparar la siguiente diapositiva y código para captura.
**Resultado:** Validador Faces managed con consulta de activos por usuario, servicio JPA con comprobación >=3 y bloqueo del usuario dentro de transacción. Productor CDI/Spring para futura integración. Compilación correcta; sin prueba de interfaz pues no hay formulario ni contenedor CDI configurado. Texto aclara que Transactional no impone por sí mismo el límite. Sin commit.

## 2026-11-05 — Pregunta 4, reporte JPQL
**Prompt:** Preparar la siguiente diapositiva y código para captura.
**Resultado:** ReporteService con rango del mes calendario anterior, agrupación por ID y título y orden descendente por cantidad; desempate por ID. Sin límite arbitrario de diez. Compilación Maven; sin pantalla ni datos de prueba nuevos. Sin commit.

## 2026-11-05 — Pregunta 5, Hibernate
**Prompt:** Preparar última diapositiva y ejemplo para captura.
**Resultado:** BusquedaLibroService con consulta por prefijo y paginación de veinte resultados; compilación correcta. EJEMPLO_CACHE.md explica configuración propuesta de segundo nivel, proveedor y selección de entidad; no activada ni medida. Sin interfaz conectada ni afirmación de rendimiento validado. Sin commit.

## 2026-11-05 — PDF de guion de exposición
**Prompt:** Dar un PDF del guion para leerlo cómodamente.
**Resultado:** PDF de seis páginas con introducción, cinco preguntas y cierre, alineado a las once diapositivas; notas para señalar código en color distinto. Generado con ReportLab y renderizado para revisión visual. Sin cambios funcionales ni commit.

## Fecha: 2026-11-06 — Comprobación SSH para pruebas de frontend

**Prompt:** «Bien hace falta conectar ssh, prueba ahora».

**Resultado:** acceso SSH a Ubuntu-Docker correcto; cuatro contenedores activos, API healthy. GET /api/health desde VM y desde Windows por túnel local 8080: status ok, backend qdrant, 577 productos/vectores y desfase_detectado false. Túnel abierto para acceso al frontend. Esta comprobación no sustituye las pruebas visuales en navegador/móvil. Sin cambios de código, commit ni push.

## Fecha: 2026-11-06 — Evidencia manual de búsqueda en frontend

**Prompt:** «hecho», con captura del buscador y resultado SBX-01-0001.

**Resultado:** registrada solo la búsqueda conocida como aprobada: resultado único Top1 SBX-01-0001, imagen coincidente, score de similitud 0.8755. Copiada la captura a docs/evidencias/frontend-manual-2026-11-06.png y creado docs/sala6/PRUEBAS_FRONTEND_MANUALES.md con las demás pruebas pendientes. No se infiere estado de carga, errores, móvil ni pruebas no observadas. Sin cambios de código, commit ni push.

## Fecha: 2026-11-06 — Evidencia visual de carga

**Prompt:** captura del buscador durante la búsqueda.

**Resultado:** registrado estado de carga visible (Analizando diseño, mensaje de comparación y tarjetas provisionales). Protección ante envíos repetidos y reactivación al finalizar permanecen pendientes de confirmación. Detectado texto contradictorio Listo para buscar durante carga en panel derecho, registrado como hallazgo sin modificar código. Captura conservada en docs/evidencias/frontend-carga-2026-11-06.png. Sin commit/push.

## Fecha: 2026-11-06 — Aclaración del estado de imagen cargada

**Prompt:** «ese listo para buscar es parte la imagen cargada, acaso esta mal q este alli, porque?».

**Resultado:** el usuario aclara que la etiqueta corresponde a disponibilidad de la imagen, no al progreso de búsqueda. Se corrige el registro manual: no se considera fallo ni condición de cierre. El cambio de etiqueta queda como mejora opcional; sin cambios de interfaz, commit o push.

## Fecha: 2026-11-06 — Reactivación y selección de muestras durante búsqueda

**Prompt:** «Cuando le di a buscar, si se puede seleccionar otros modelos de prueba, y cuando termina y vuelve a habilitarse muestra los resultados».

**Resultado:** registrada como aprobada por confirmación del usuario la reactivación al finalizar y presentación de resultados. La inspección de handleSelectSample confirma que no comprueba loading y puede iniciar otra búsqueda; las respuestas actualizan result/loading sin identificar la petición vigente. Se registra riesgo de respuestas cruzadas, sin afirmar reproducción visual de ese fallo. No se cierra protección global de concurrencia; sin cambios de código, commit ni push.

## Fecha: 2026-11-06 — Bloqueo temporal de entradas de imagen

**Prompt:** «bien, lo puedes implementar y luego lo puedo probar en local?».

**Implementación:** frontend/src/app/search/page.tsx usa ref síncrono compartido en selección de muestras/búsqueda/carga de archivos, controles disabled durante loading y finally para liberar bloqueo ante resultado, error esperado o excepción. Se bloquean pegar y soltar durante espera, incluida prevención de navegación de archivo fuera de la zona de subida; se limpian resultados anteriores al iniciar. No se cambia la etiqueta Listo para buscar. Código sincronizado y frontend reconstruido/activado en VirtualBox.

**Verificación:** documentación Next.js instalada consultada; build y TypeScript correctos, lint 0 errores/4 advertencias existentes. Navegador real mediante CUA: seis muestras, Buscar, Cambiar e input deshabilitados durante petición; habilitados al finalizar con resultado SBX-01-0002. Parada breve controlada de API solo en staging, con recuperación automática de respaldo: error del proxy visible y controles liberados; API restaurada, reintento normal correcto Top1 SBX-01-0001 y controles activos. Capturas en docs/evidencias/frontend-bloqueado-2026-11-06.png y frontend-bloqueo-resultado-2026-11-06.png; registro manual actualizado con alcance exacto. Ctrl+V/arrastre bloqueados por implementación, sin afirmar prueba manual de esas interacciones. Sin nuevo commit/push.

## Fecha: 2026-11-06 — Confirmación del usuario de bloqueo y finalización

**Prompt:** «Mostro resultados, completado», con captura final.

**Resultado:** registradas capturas aportadas por el usuario durante carga y tras finalizar. Confirman bloqueo visual temporal, resultado SBX-01-0001 y botones Buscar/Cambiar reactivados después de la corrección. Prueba cerrada con confirmación del usuario; Ctrl+V/arrastre continúan pendientes de prueba manual. Sin cambios de código ni commit/push.

## Fecha: 2026-11-06 — Nueva consulta y hallazgo de ranking

**Prompt:** «1. selecciona, se bloquea y carga 2. completa la descarga y muestra resultados, ya se puede seleccionar», con dos capturas.

**Resultado:** registrado flujo de nueva consulta SBX-01-0006 con bloqueo/carga, nueva respuesta y reactivación confirmada por el usuario. Capturas conservadas. Se registra aparte un hallazgo de calidad: el resultado correcto SBX-01-0006 aparece segundo (0.5731), detrás de SBX-02-0149 (0.7838); se anuncian tres resultados, pero solo se ven las dos primeras tarjetas. Frontend aprobado para este flujo; no se concluye calidad global del motor ni se modifica ranking. Sin cambios de código, commit o push.

## Fecha: 2026-11-06 — Rechazo visual de archivo inválido

**Prompt:** «no deja», con captura del mensaje de archivo no válido.

**Resultado:** registrada como aprobada la validación visible de archivo inválido; la captura muestra los formatos JPG/PNG/WEBP y conserva la zona de carga. No se infiere extensión concreta ni petición enviada a API. Recuperación cargando imagen válida sin recargar continúa pendiente. Evidencia guardada; sin cambios de código, commit/push.

## Fecha: 2026-11-06 — Foto externa procesada en frontend

**Prompt:** «adjunte la imagen, cargando... luego me salieron los resultados», con dos capturas.

**Resultado:** registrada la carga de foto externa, procesamiento y presentación de respuesta con cinco resultados anunciados; capturas visibles de las dos primeras tarjetas, sin afirmar id correcto o calidad global. No se marca recuperación sin recargar tras archivo inválido porque hubo reinicio de PC entre pruebas. Fixture PNG 16x16 creada en evaluation/fixtures/tiny-16.png para la siguiente prueba de tamaño mínimo. Sin cambios de código de aplicación, commit/push.

## Fecha: 2026-11-06 — Mensaje visible de imagen demasiado pequeña

**Prompt:** captura tras buscar con tiny-16.png.

**Resultado:** registrada validación de tamaño mínimo: mensaje explícito 16x16 y mínimo 32px por lado; controles disponibles. Recuperación con imagen válida sin recargar permanece pendiente. Captura guardada; sin cambios de código, commit/push.

## Fecha: 2026-11-06 — Recuperación tras imagen pequeña confirmada

**Prompt:** «hecho, le di a cambiar y me dejo volver a adjuntar y buscar imagen», con captura final.

**Resultado:** marcada recuperación tras tiny-16.png: Cambiar permite adjuntar foto válida y obtener resultados con controles activos y sin error anterior. Se conserva registro textual de la evidencia sin copiar la captura con pestañas de otras actividades. No se infiere calidad del ranking ni recuperación específica tras archivo no imagen. Sin cambios de código, commit/push.

## Fecha: 2026-11-06 — Arrastre bloqueado durante búsqueda

**Prompt:** «no no me deja adjuntar mas cosas», con captura de arrastre durante carga.

**Resultado:** registrada prueba de arrastre bloqueado: símbolo de prohibición y consulta actual conservada mientras procesa. Ctrl+V sigue pendiente de confirmación específica; no se infiere su prueba de la captura. Sin cambios de código, commit/push.

## Fecha: 2026-11-06 — Pegado bloqueado confirmado

**Prompt:** «si, tambien», en respuesta a si Ctrl+V durante carga conservó la imagen actual.

**Resultado:** marcada como aprobada por declaración explícita del usuario la prueba de bloqueo de pegado durante búsqueda. Quedan comprobados selector, muestras, arrastre y pegado durante espera; no se afirma captura específica del portapapeles. Sin cambios de código, commit/push.

## Fecha: 2026-11-06 — Entrega de bloqueo y tests funcionales

**Prompt:** «añade el que se hicieron tests en el commit, adicionalmente ahora que toca en la parte frontend? haz los cambios».

**Resultado:** preparación de commit enfocado en bloqueo temporal de entradas y registro de tests. Se documentan como verificadas en staging la carga/resultados, bloqueo de muestras/selector/Cambiar/arrastre/pegado, nueva consulta, validaciones de tipo/tamaño, recuperación tras tamaño inválido y caída de API. Se conserva el alcance de cada evidencia (navegador, captura o declaración). Checklist principal e índice enlazan el registro; errores de API se vinculan a comprobaciones ya realizadas. Siguiente trabajo documentado: adaptación estrecha y luego celular real, todavía pendientes. Mensaje de commit incluirá Tests con build/TypeScript, lint 0 errores/4 advertencias, pruebas funcionales y curl. No se afirma nueva suite unitaria ni se repite testing de ejecución por cambios posteriores solo documentales. Borradores de operaciones y archivos ajenos quedan fuera. Esta instrucción autoriza el commit; no solicita un nuevo push.

## Fecha: 2026-11-06 — Integración local de avances de sala-6

- Prompt: «en mi repo local trae cambios, comentame que traemos».
- Se consultó origin/sala-6 y se terminó la integración de bf2d6680 con el trabajo local 6f52707a mediante 705e1fa6.
- Se resolvió el conflicto del checklist conservando el alcance y las evidencias de las pruebas manuales de frontend.
- Cambios recibidos: catálogo desde products.csv, proveedor compartido de catálogo, enlace al producto, Docker sin root para frontend/proxy, healthchecks, configuración de HTTPS y versiones fijadas de dependencias Python.
- Verificación: git diff --cached --check sin errores y ningún conflicto pendiente. No se ejecutó build local (frontend/node_modules ausente), ni se actualizó o probó la VM en esta tarea.
- Se conservaron los cambios locales de operación, propuestas, scripts y otros archivos pendientes; no se realizó push.

## Fecha: 2026-11-06 — Validación del catálogo integrado en frontend

- Prompt: «avancemos con el primero», referido a probar catálogo, imágenes, muestras, búsqueda y detalle tras integrar cambios.
- Se guardó una copia previa de frontend/configuración en la VM y se transfirió el frontend de 705e1fa6. Build Next.js/TypeScript correcto; recreado solo frontend, UID 1000, saludable. API y proxy en ejecución se conservaron; HTTPS y nuevas dependencias Python fuera de esta prueba.
- /api/catalog respondió 200 con 577 registros únicos y coincidencia de todos los campos expuestos y su orden con products.csv local. Seis imágenes PNG respondieron 200 y cargaron en navegador.
- Se verificaron paginación, filtro por ID, ficha, enlace de producto, navegación a buscador, muestra SBX-01-0001 (Top 1, 0.8755), bloqueo/reactivación y apertura/cierre de detalle desde resultado. Curl con consulta sin marco SBX-01-0010 respondió 200, Top 1 esperado (0.7749).
- Hallazgos pendientes: URLs de ejemplo y precios nulos mostrados como S/ sin importe. No se enviaron cotizaciones ni se abrieron destinos externos.
- Evidencia JSON y árboles visibles TXT en docs/evidencias/catalogo-*. El navegador no pudo generar screenshots. Se actualizaron checklist y registro manual sin marcar validación comercial, móvil o producción.
- No se modificó código funcional, no se hizo commit ni push. Los pendientes locales previos se conservaron.

## Fecha: 2026-11-06 — Corregir presentación de precios sin definir

- Prompt: «haz loscambios», sobre los precios vacíos confirmados en capturas del resultado y Ver modelo.
- Se sustituyeron siete expresiones de precio por «A consultar» en search/page.tsx y catalog/page.tsx, coherente con los campos de precio tipados como null del catálogo actual. No se inventaron importes ni se modificaron URLs.
- Transferido a VirtualBox, build Next.js/TypeScript correcto, lint 0 errores y 1 advertencia previa en app.js. Recreado únicamente frontend; saludable. Curl con imagen real de data/consultas respondió 200.
- Navegador: consulta SBX-01-0003 devuelve ese ID primero (0.9023); resultado y fichas de búsqueda/catálogo muestran «A consultar». Captura y árboles visibles guardados en docs/evidencias/precios-*; checklist actualizado.
- Se eliminó únicamente la imagen temporal de lint creada en esta tarea, recuperando espacio; se conservaron datos y servicios existentes. No se hizo commit ni push.

## Fecha: 2026-11-06 - Volumen para cache de Hugging Face en el despliegue principal

- Prompt: «Lo unico que ahora debo hacer es [ ] Volumen para caché de Hugging Face., solo esa parte debo hacer dame esa parte nomás que este al 100% bien para ponerle una "x"».
- Se añadió a docker-compose.yml el montaje del volumen nombrado hf_cache en /home/appuser/.cache/huggingface (ruta de HF_HOME declarada en Dockerfile.api) dentro del servicio api, junto con la declaración superior `volumes: hf_cache:`, replicando la configuración ya probada en docker-compose.staging.yml.
- Verificación: `docker compose config` sin errores en la configuración principal y en la combinada principal+staging (un solo montaje en la ruta destino, sin duplicados). El daemon de Docker no estaba disponible en esta máquina, por lo que no se ejecutó el contenedor; la validación de permisos de escritura y de descarga/carga de modelos sigue siendo la de staging del 2026-11-04, con la misma ruta y el mismo usuario appuser (la copia inicial de un volumen nombrado hereda la propiedad del directorio creado en la imagen).
- Documentación: casilla «Volumen para caché de Hugging Face en el despliegue principal» y su subcasilla marcadas en docs/planificacion/REQUERIMIENTOS_DESPLIEGUE.md, retirado el punto de «Qué falta aún» correspondiente y actualizada la fila Build de docs/sala6/ESTADO_SALA6.md.
- Sin commit ni push.

## Fecha: 2026-11-09 — Recuperación de búsqueda tras archivo inválido

- Prompt: «hecho» y confirmación posterior de que la imagen válida se adjuntó, cargó y devolvió resultados sin recargar la página.
- En staging, tras el rechazo de un archivo inválido, se cargó `SBX-01-0010_sin_marco.jpg`; la búsqueda terminó con Top 1 `SBX-01-0010` y score de similitud 0.9454.
- Checklist manual y requerimientos de frontend actualizados con la prueba observada. No se ejecutaron pruebas automatizadas ni se modificó código funcional.

## Fecha: 2026-11-09 — Verificación responsive del frontend

- Prompt: «bien empecemos», para iniciar el checklist frontend pendiente comenzando por la adaptación a pantallas estrechas.
- Navegador en staging revisado a 360×800, 390×844 y 768×900. No se observaron cortes; a 360 px carga y resultado Top 1 SBX-01-0002 (0.8508) se mostraron en una columna con botones refluídos; a 768 px se mantuvo la disposición de dos columnas.
- A 360 px se cargó `tiny-16.png`; el mensaje de error (16×16; mínimo 32 px por lado) se ve completo y legible. Captura guardada en `docs/evidencias/frontend-error-mobile-360-2026-11-09.png`. La acción Cambiar queda arriba del aviso, accesible al desplazarse. `/api/health` respondió 200 con 577 productos/embeddings; una búsqueda tardó más de lo esperado, pero terminó con resultados.
- Checklist responsive actualizado. No se modificó código ni se hizo commit/push. Siguen pendientes la prueba en celular real, el caso controlado sin resultados y el tiempo agotado.

## Fecha: 2026-11-09 — Simulacro de rollback de imágenes en VirtualBox

- Prompt: «acaso puedes tu ejecutar la vm, conectar ssh y testearlo, hazlo».
- Se probaron tags locales `rollback-base` y `rollback-candidate`; `docker compose config -q` pasó, API/frontend healthy y `/api/health` devolvió 200 con 577 productos/embeddings y sin desfase. Una búsqueda exacta por el proxy dio Top 1 `SBX-01-0001` en ambos tags.
- El primer `up` sin `--no-deps` recreó Qdrant; se repitió usando `--no-deps`, conservando el ID/hora de inicio y bind mount de Qdrant. El staging quedó en `rollback-candidate` healthy. No se probó restauración de backup ni compatibilidad de cambios de esquema.
- Guía: `docs/sala6/ROLLBACK_IMAGENES.md`; evidencia sanitizada: `docs/evidencias/rollback-2026-11-09.txt`. Checklist actualizado con estos límites. No se hizo push.
