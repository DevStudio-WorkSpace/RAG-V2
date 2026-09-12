# Estructura de Carpetas del Proyecto

| Carpeta | Propósito |
|---|---|
| **`api/`** | API FastAPI. Contiene el servidor (`main.py`), el motor de búsqueda Hito 1 (`search_engine.py`), Hito 2 con reranking (`search_engine_hito2.py`), descriptores visuales y preprocesamiento de consultas. |
| **`config/`** | Configuración global (`settings.py`). |
| **`data/`** | Datos del proyecto: imágenes originales (`images/`), imágenes normalizadas (`images_normalized/`), embeddings CLIP/SigLIP/OpenCLIP (`.npy`), `products.csv`, consultas de prueba, descriptores JSON, informes de normalización y revisiones humanas. |
| **`evaluation/`** | Evaluación del Hito 2: consultas de test, imágenes de test, plan de tests e informes de resultados. |
| **`frontend/`** | Interfaz Streamlit (`app.py`) — cliente puro de la API, no genera embeddings ni busca localmente. |
| **`prompts/`** | Prompt para identificación de país de camisetas (`country_identification.py`). |
| **`scraper/`** | Scraping web: parser HTML, descargador de imágenes y orquestador del scraping. |
| **`scripts/`** | Scripts auxiliares: generación de embeddings, normalización de imágenes, consolidación de datos, evaluación de 50 consultas, comparación Hito 1 vs Hito 2, validación de dataset, etc. |
| **`storage/`** | Exportador de datos (`exporter.py`). |
| **`CONSULTAS/`** | Consultas de prueba y montajes generados para evaluación. |
| **`.streamlit/`** | Configuración del tema de Streamlit. |
