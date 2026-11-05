# AGENTS.md — Reglas de trabajo para la IA en este repositorio

> La IA DEBE leer este archivo al inicio de cada sesión y seguirlo.
> El alcance vigente se define por las instrucciones del usuario y las reglas
> de este archivo. La documentación se consulta desde **`docs/README.md`**.

## 1. Antes de tocar código: revisar el alcance vigente

Al comenzar cada sesión, leer este archivo, `README.md` y la documentación
aplicable a la tarea desde `docs/README.md`.

- `TRABAJO.md` queda descartado como requisito vigente por decisión del usuario
  del 2026-11-05. Es un antecedente conservado en Git: no recuperarlo, exigirlo
  ni bloquear tareas por su ausencia. No restablecer sus requisitos por defecto.
- Alcance actual: buscador visual autónomo con FastAPI, frontend Next.js y
  servicios Qdrant, sobre el catálogo SBX actual. Continuar Sala 6 con pruebas,
  reproducibilidad, seguridad, respaldos, recuperación, monitoreo y evaluación.
- WordPress/WooCommerce y la ampliación a 15.000 diseños quedan fuera del alcance
  actual hasta una nueva instrucción explícita del usuario.
- Consultar `docs/planificacion/REQUERIMIENTOS_DESPLIEGUE.md` para el checklist,
  `docs/sala6/ESTADO_SALA6.md` para el diagnóstico y
  `docs/sala6/STAGING_VIRTUALBOX.md` para las pruebas verificadas. Contienen
  antecedentes y pendientes: sus afirmaciones deben contrastarse con el código
  y las evidencias; una casilla marcada no sustituye una prueba.
- Se mantienen los requisitos de catálogo/IDs alineados, API como única vía de
  búsqueda del frontend, manejo de errores, evaluación comparativa sobre las
  mismas consultas y revisión humana del Top 5. Descartar el documento antiguo
  no elimina estos requisitos de calidad.
- Por instrucción explícita del usuario del 2026-11-05, Qdrant es el backend
  canónico de búsqueda y el modelo activo es CLIP de 512 dimensiones con Cosine.
  Los índices `.npy` quedan como fuente de migración y baseline histórico; no
  son backend de las búsquedas normales.

## 2. Objetivo del proyecto

Motor de búsqueda visual RAG para camisetas deportivas:

1. Se sube una imagen de consulta.
2. CLIP genera su embedding.
3. La API consulta la colección única de Qdrant (CLIP, 512 dimensiones).
4. La API devuelve Top 5 con ID, nombre, imagen, URL y score.
5. La interfaz muestra los resultados y registra evaluación.

Frase de validación: «Una imagen se carga una sola vez, se procesa con un solo
modelo, se compara contra un solo índice y los resultados se muestran en una
sola interfaz.»

## 3. Estructura canónica (NO crear copias ni rutas alternativas)

```
proyecto/
├── api/
│   ├── main.py                 # API FastAPI (endpoints /search/image y /health)
│   ├── search_engine.py        # baseline Hito 1 para evaluación/migración
│   └── search_engine_hito2.py  # recuperación Qdrant + reranking visual
├── data/
│   ├── products.csv            # ÚNICA fuente de productos
│   ├── embeddings.npy          # fuente de migración/baseline, no índice activo
│   ├── ids.npy                 # alineado posición a posición con embeddings.npy
│   ├── embeddings_clip.npy     # índice normalizado de Sala 4 (Hito 2)
│   ├── images_original/        # originales (NO modificar ni borrar)
│   ├── images_normalized/      # banco canónico de imágenes (Sala 1, Hito 2)
│   └── products.csv            # ÚNICA fuente de productos (mismo ID que images_normalized)
├── frontend/
│   ├── src/                    # Next.js = cliente de la API mediante proxies
│   └── app.py                  # cliente Streamlit anterior; no es la UI principal
├── scripts/                    # validación, embeddings, evaluación, etc.
├── requirements.txt
└── README.md
```

PROHIBIDO crear archivos tipo `index_embeddings.npy`, `embeddings_productos.npy`,
`embeddings_final_v2.npy` o duplicar rutas. Los únicos índices son los listados
arriba.

## 4. Contrato común de datos

- `products.csv` con columnas exactas: `id,proveedor,pagina,imagen,nombre_original,url`.
- `imagen` contiene SOLO el nombre de archivo (ej. `AIM-P001-001.jpg`).
- `ids.npy` debe conservar el MISMO orden que `embeddings.npy`
  (posición 0 → id 0, etc.). Si se desalinea, el sistema devuelve nombres
  incorrectos. SIEMPRE validar la alineación al cargar.
- El catálogo activo usa IDs SBX (ej. `SBX-01-0001`) e imágenes PNG.
  AIM corresponde al catálogo anterior. No renombrar IDs ni cambiar formatos
  para ajustarlos a ejemplos históricos.

## 5. Arquitectura de referencia

- **Modelo base verificado en staging:** `openai/clip-vit-base-patch32` (en código se usa
  `SentenceTransformer("clip-ViT-B-32")`).
- Existen índices comparativos `embeddings_openclip.npy` y
  `embeddings_siglip.npy` y un modo Fusión. No crear copias adicionales ni
  presentar Fusión como validado por las pruebas realizadas con CLIP.
- **Índice canónico:** colección Qdrant configurada en `QDRANT_COLLECTION_NAME`,
  vector CLIP de 512 dimensiones y Cosine. El arranque valida el esquema,
  restaura opcionalmente un snapshot y migra los `.npy` si la colección está vacía.
- **Archivos `.npy`:** `data/embeddings.npy` + `data/ids.npy` son la fuente de
  migración y baseline de evaluación del Hito 1; no se consultan en el flujo
  normal. `embeddings_clip.npy`, OpenCLIP y SigLIP permanecen como artefactos
  comparativos, no como índices activos de la API.
- **Motor Hito 2:** recuperación amplia desde Qdrant (30 candidatos) + reranking visual
  (color HSV por regiones frente/espalda, estructura 32×32, color dominante,
  gama, patrón, marco, franjas) + umbral dinámico (puede devolver < top_k).
- **La interfaz NO genera embeddings ni busca localmente.** Solo consume la API.

## 6. Contrato de respuesta

`POST /search/image` (form-data: `file` + `modo`) devuelve una lista de
objetos con al menos:

```json
[
  {
    "id": "AIM-P001-001",
    "nombre": "Guadalcacin Blue",
    "imagen": "AIM-P001-001.jpg",
    "url": "https://...",
    "proveedor": "Aimari",
    "score": 0.82,
    "score_reranking": 0.85,
    "posicion_final": 1,
    "modelo_utilizado": "clip+color+estructura+patron+marco+franjas"
  }
]
```

`GET /health` devuelve: `status`, `products`, `embeddings`, `model`,
`desfase_detectado`, `observacion`.

## 7. Modos del endpoint

- `auto` / `completo` / `procesada`: Qdrant + CLIP y reranking del Hito 2.
- `clasico` / `original` / `legacy`: compatibilidad `.npy` del Hito 1,
  exclusivamente para comparación histórica.

## 8. Reglas de la evaluación (Hito 2)

- Mínimo 50 consultas: 10 exactas, 10 sin marco, 10 recoloreadas, 10 recortadas,
  10 mockups/personas. Cada una con su `id_correcto`.
- Métricas: Top 1 exactitud, Top 5 recuperación y calidad Top 5 humana
  (Muy similar / Similar / Poco similar / No relacionado).
- Comparación obligatoria Hito 1 vs Hito 2 sobre las MISMAS consultas.
- No llamar al score «porcentaje de coincidencia» ni «confianza»: es un
  **score de similitud**.

## 9. Manejo de errores obligatorio en la API

La API NO debe cerrarse ante:
- Sin imagen / archivo no válido → 400 `{"error": "El archivo enviado no es una imagen válida"}`.
- Imagen demasiado pequeña (mínimo 32 px por lado) → 400 con mensaje claro.
- Falta `embeddings.npy`, falta `products.csv`, IDs desalineados, modelo no
  carga → 500 con mensaje, sin matar el servidor.
- Una imagen de un candidato que no puede abrirse: puntuar 0 en visuales, no
  romper la búsqueda.

## 10. Flujo de trabajo estándar para cada tarea

1. Leer este archivo y la documentación vigente aplicable (§1).
2. Explorar el código existente ANTES de modificar (buscar patrones, no asumir).
3. Implementar en la estructura canónica, sin duplicar motores ni índices.
4. Verificar: `python -m py_compile` de los archivos tocados y probar la API
   con `curl` (subir una imagen real de `data/consultas/`).
5. Correr lint/typecheck si existe; si no, compilar.
6. Actualizar `AI_LOG.md` con el prompt de IA usado (requisito del proyecto).
7. NO commitear a menos que lo pida el usuario explícitamente.

## 11. Medio ambiente de ejecución

- Comprobar el entorno real antes de ejecutar comandos. El repositorio se
  trabaja también desde Windows/PowerShell y se probó en Ubuntu/Docker dentro
  de VirtualBox por SSH. Adaptar comandos y activación de venv al sistema/shell.
- Para staging y acceso, seguir `docs/sala6/STAGING_VIRTUALBOX.md`.
- Las indicaciones fish siguientes aplican únicamente a ese entorno Linux.

- No usar pip del sistema (PEP 668). Usar el venv: `source .venv/bin/activate.fish`.
- La API se levanta con: `uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload`.
- La interfaz principal Next.js se inicia desde `frontend/` con `npm run dev`
  o mediante Docker. `streamlit run frontend/app.py` es el cliente anterior.
- El torch instalado es la build CPU (sin NVIDIA), por la falta de GPU y por
  espacio en `/tmp` (tmpfs). No reinstalar torch CUDA.
- Si falta espacio al instalar, apuntar `TMPDIR=/var/tmp` (el disco tiene ~400 GB).
- El usuario usa fish: los comandos de activación de venv son `.fish`, y
  «source .venv/bin/activate» falla.

## 12. Seguridad obligatoria de la API

- Nunca dejar CORS en `*`. Usar `CORS_ORIGINS` con orígenes explícitos; en
  producción, solo el dominio real con HTTPS.
- Los endpoints de búsqueda exigen `X-API-Key` de cliente o administrador.
  `API_CLIENT_KEY` es el cliente `default`; `API_CLIENT_KEYS` permite claves
  adicionales con formato `nombre:clave,...`.
- Indexación y administración (`/index/qdrant`, `/health/qdrant`,
  `/collections/qdrant`) exigen `API_ADMIN_KEY`.
- Qdrant exige `QDRANT_API_KEY`; sus puertos solo se publican en `127.0.0.1` y
  el frontend no comparte red con Qdrant.
- `GET /health` es público a propósito (liveness/readiness).
- Si faltan `API_CLIENT_KEY`/`API_CLIENT_KEYS`/`API_ADMIN_KEY`, fallar cerrado
  con 503; nunca abrir endpoints por defecto.
- Comparar claves con `secrets.compare_digest` y no registrarlas en logs.
- El frontend NO recibe claves: usa los proxies server-side `/api/search` y
  `/api/health`. Prohibido `NEXT_PUBLIC_*` para secretos.
- No copiar `.env` ni `.env.local` dentro de imágenes Docker.
