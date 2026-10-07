# AGENTS.md — Reglas de trabajo para la IA en este repositorio (Actualizado Hito 2/3)

> La IA DEBE leer este archivo al inicio de cada sesión y seguirlo.
> Este archivo resume las reglas operativas, actualizadas para reflejar las mejoras del Hito 2/3.

## 1. Antes de tocar código: leer la documentación vigente

Al comenzar cada sesión, la IA DEBE revisar `README.md` y `DECISIONES.md`. Estos archivos contienen la arquitectura real y actual del sistema, la cual ha evolucionado más allá del prototipo original. El trabajo siempre debe alinearse con la arquitectura de Next.js, FastAPI y Qdrant.

## 2. Objetivo del proyecto

Plataforma de búsqueda visual de camisetas deportivas que integra Scraping, un Motor Híbrido (Vectorial + YOLO) y Reranking:

1. Se scrapea el catálogo y se normalizan las imágenes.
2. Un pipeline extrae embeddings y segmenta con YOLO/Fashion-CLIP.
3. Se almacena y busca mediante una base de datos vectorial (Qdrant).
4. El motor puede aplicar reranking visual (color/estructura) y preprocesar imágenes subidas.
5. Una interfaz Next.js permite la evaluación experta (Acierto/Sirve/No sirve).

## 3. Estructura canónica permitida

El proyecto se divide en múltiples módulos funcionales:

```
proyecto/
├── api/                    # API FastAPI
│   ├── main.py                 # Endpoints (/search/image, /search/image/v2)
│   ├── search_engine.py        # Motor híbrido Qdrant + YOLO + core
│   ├── search_engine_hito2.py  # Motor con reranking y descriptores
│   ├── preprocesar_consulta.py # Preparación de la imagen (limpieza)
│   └── descriptores_visuales.py# Generación de métricas de color/patrón
├── core/                   # Componentes base del motor (Fusionado)
│   ├── vision_pipeline.py      # Pipeline YOLO/Rembg/Fashion-CLIP
│   ├── base_datos.py           # Gestor de Qdrant (QdrantManager)
│   └── search_service.py       # Lógica de búsqueda híbrida
├── frontend/               # Aplicación Next.js (Evaluación)
│   └── src/, package.json, etc.
├── data/                   # Datos, embeddings canónicos, descriptores
├── qdrant_data/            # Base de datos vectorial persistente
├── scraper/                # Motor de extracción de datos
├── scripts/                # Scripts de validación, generación y normalización
├── utils/, config/, storage/ # Utilidades para el scraper
├── evaluation/             # Planes e imágenes de testeo (Sala 2)
├── main.py                 # Punto de entrada del scraper
├── yolov8n.pt              # Modelo de segmentación YOLO
├── docker-compose.yml      # Despliegue de servicios (API + Frontend)
└── requirements.txt, README.md, DECISIONES.md
```

## 4. Contrato de datos y Modelos

- Los embeddings principales son `embeddings_clip.npy` e `ids.npy`. El sistema también soporta la base de datos `Qdrant` para búsqueda persistente e híbrida.
- Los modelos pesados como `yolov8n.pt` o los índices vectoriales (`qdrant_data/`) forman parte oficial del pipeline de ejecución y son ignorados en git.
- **Reranking:** `data/descriptores.json` es requerido por el motor Hito 2 para ordenar los resultados por similitud visual de color y estructura.

## 5. Arquitectura de referencia

El buscador actual tiene múltiples pipelines de búsqueda, diseñados para evaluar la calidad (Hito 2/3):

- **Motor Qdrant (search_engine.py):** Búsqueda híbrida usando YOLO, Rembg y Fashion-CLIP.
- **Motor Hito 2 (search_engine_hito2.py):** Recuperación amplia y reranking visual basado en color y estructura, precomputados en `descriptores.json`.
- **Preprocesamiento:** La consulta del usuario puede ser limpiada (`preprocesar_consulta.py`) antes de enviarse al modelo de embedding.

## 6. Frontend y Evaluación

- El frontend es una **aplicación Next.js** (`frontend/`) operada por atajos de teclado y `localStorage` (como se detalla en `DECISIONES.md`).
- **NO usar Streamlit**. Todo desarrollo de interfaz debe hacerse sobre la app en `frontend/` y exponerse en el puerto 3000 vía Docker.
- Los botones de juicio fijo (Acierto / Sirve / No sirve) son inamovibles.

## 7. Medio ambiente de ejecución

- El ecosistema se puede levantar localmente en un virtual environment (`python -m uvicorn api.main:app` y `npm run dev`), o preferiblemente mediante **Docker Compose**.
- `docker-compose.yml` levanta ambos contenedores (`api` en 8000, `frontend` en 3000).

## 8. Modificaciones al código

1. Leer siempre `README.md` y `DECISIONES.md` para contexto.
2. Explorar el código existente (`api/`, `core/`, `frontend/`) antes de modificar.
3. Actualizar los scripts de `/scripts/` si hay cambios en los esquemas de datos.
4. NO commitear archivos pesados, revisar siempre `.gitignore`.
