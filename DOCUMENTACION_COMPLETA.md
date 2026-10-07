# Documentación Completa del Proyecto: RAG Visual de Camisetas Deportivas

Esta documentación ofrece una visión general, técnica y metodológica completa del proyecto de plataforma de búsqueda visual de camisetas deportivas (RAG-V2). Está basada en la consolidación de la arquitectura actual, las reglas de operación y las decisiones metodológicas documentadas en el repositorio.

---

## 1. Visión General del Proyecto

El proyecto es una **Plataforma de búsqueda visual de camisetas deportivas** basada en la extracción (scraping) de catálogos, consolidación de datos y un motor de recuperación híbrida utilizando modelos de visión y bases de datos vectoriales.

**Objetivo principal:** Permitir a un usuario subir una imagen de una camiseta (foto real, recortada, recoloreada, etc.) y recuperar el **Top 5 de diseños visualmente más parecidos** de un catálogo indexado, aplicando técnicas de normalización, preprocesamiento y _reranking_ visual.

### Características Clave (Hito 2/3)

- **Scraping y Normalización:** Extracción automatizada del catálogo y limpieza de las imágenes (eliminación de marcos, extracción de frente y espalda).
- **Motor Híbrido:** Combinación de embeddings de modelos de visión (CLIP, OpenCLIP, SigLIP) y descriptores visuales (color, estructura).
- **Búsqueda Robusta:** Capacidad de encontrar similitudes incluso cuando la consulta tiene ruido, ángulos distintos o no proviene del catálogo original.
- **Evaluación Experta:** Una interfaz web construida en Next.js para someter los resultados del buscador a validación humana estricta.

---

## 2. Arquitectura y Componentes del Sistema

El sistema está dividido en módulos funcionales claros que abarcan desde la recolección de datos hasta la exposición en interfaz de usuario.

### Estructura de Directorios Principal

```text
proyecto/
├── api/                    # API FastAPI
│   ├── main.py                 # Endpoints (/search/image, /search/image/v2)
│   ├── search_engine.py        # Motor de búsqueda base
│   ├── search_engine_hito2.py  # Motor avanzado con reranking
│   ├── preprocesar_consulta.py # Preparación y limpieza de la imagen del usuario
│   └── descriptores_visuales.py# Análisis de color y patrón
├── core/                   # Componentes base del motor
│   ├── vision_pipeline.py      # Pipeline YOLO/Rembg/Fashion-CLIP
│   ├── base_datos.py           # Gestor de Qdrant (Base de datos vectorial)
│   └── search_service.py       # Lógica de búsqueda híbrida
├── frontend/               # Aplicación Next.js (Interfaz de evaluación)
├── data/                   # Datos, imágenes normalizadas y embeddings canónicos
├── scraper/                # Motor de extracción de datos del catálogo original
├── scripts/                # Scripts de validación, generación y automatización
└── evaluation/             # Casos de prueba y planes de evaluación experta
```

### Modelos Utilizados

- **Modelos Base de Embeddings:** `CLIP`, `OpenCLIP`, y **`SigLIP`**. En las pruebas del Hito 2, **SigLIP** demostró ser el más efectivo para la recuperación visual de camisetas deportivas (92% de precisión Top 1 en el test base).
- **Segmentación:** `YOLOv8` (`yolov8n.pt`) para segmentación e identificación de regiones relevantes de la camiseta.

---

## 3. Flujo de Datos y Operación

El ciclo de vida de los datos sigue una secuencia estricta de procesamiento:

### Fase A: Preparación del Catálogo

1. **Scraping:** Se extraen las imágenes y metadatos con `scraper/main.py`.
2. **Consolidación:** Se genera el dataset canónico (`data/products.csv`) y se alinean las imágenes en `data/images_normalized/`.
3. **Normalización (Sala 1):** Las tarjetas del catálogo se transforman en imágenes limpias (frente y espalda, sin logos ni marcos).
4. **Generación de Embeddings (Sala 4):** Se procesan las imágenes con los modelos de visión, generando las matrices vectoriales finales (`embeddings_siglip.npy`, etc.) junto a sus `ids.npy`.

### Fase B: Ingesta y Búsqueda de Consultas

1. **Preprocesamiento (Sala 2):** Cuando un usuario hace una consulta, la imagen pasa por `api/preprocesar_consulta.py` para limpiarla antes de vectorizarla.
2. **Búsqueda Inicial:** El modelo vectorial busca los vecinos más cercanos en el espacio latente.
3. **Reranking (Sala 3):** El motor del Hito 2 (`/search/image/v2`) aplica descriptores visuales (color HSV global/regional y estructura del patrón) para reordenar los resultados recuperados, asegurando coherencia visual humana.

---

## 4. API Backend (FastAPI)

La API expone los servicios en el puerto `8000`.

- `GET /health`: Estado del sistema, cantidad de productos indexados.
- `POST /search/image`: Endpoint base que soporta múltiples modos:
  - `auto`: Prepara la consulta y devuelve una respuesta enriquecida.
  - `procesada`: Usa la imagen ya preparada.
  - `original`: Usa la consulta original sin limpiar.
  - `completo`: Integra el motor base con el reranking.
  - `legacy`: Solo lista de resultados base.
- `POST /search/image/v2`: Endpoint del motor del **Hito 2**. Combina recuperación amplia (Top 30) con el proceso de reranking, retornando desgloses de score detallados (`score_inicial`, `score_color_global`, `score_estructura`, `score_reranking`).

---

## 5. Frontend y Metodología de Evaluación (Sala 2)

El frontend no es solo una interfaz de demostración, sino una **Herramienta de Evaluación Experta** construida en **Next.js**.

### Criterios Metodológicos de Evaluación

Se descubrió que medir variaciones sintéticas (recortes, recoloreos del propio catálogo) no reflejaba el uso real. Por ello, la evaluación requiere **imágenes externas y reales**.

Se miden 3 métricas de negocio clave:

1. **Precision@1:** ¿El primer resultado es el diseño exacto que el usuario buscaba? (Eficiencia).
2. **Recall@5:** ¿El diseño correcto aparece entre los primeros 5 resultados? (Cobertura).
3. **Utilidad del Top 5:** ¿Los otros resultados sirven como alternativas aceptables para un cliente? (Calidad percibida).

### Funcionamiento de la Interfaz

- Operada mediante atajos de teclado para evitar la fatiga por uso del mouse en tandas largas de evaluación.
- Los juicios se guardan persistentemente en el navegador mediante `localStorage` para prevenir pérdida de datos.
- Por cada resultado, el experto debe clasificarlo bajo **criterios fijos**:
  - **Acierto (1):** Es el mismo diseño.
  - **Sirve (2):** No es igual, pero es una alternativa visual válida para ofrecer.
  - **No sirve (3):** Es un diseño completamente distinto.

---

## 6. Instrucciones de Ejecución Local

Para correr el entorno completo en local, es recomendable usar entornos virtuales de Python.

```bash
# 1. Instalar dependencias
python -m venv venv
source venv/bin/activate  # En Linux/macOS
venv\Scripts\activate     # En Windows
pip install -r requirements.txt

# 2. Levantar la API Backend
python -m uvicorn api.main:app --port 8000

# 3. Levantar la Interfaz Frontend
cd frontend
npm install
npm run dev
```

El proyecto también admite el uso de **Docker Compose** (`docker-compose.yml`) para levantar ambos servicios concurrentemente (`api` en 8000, `frontend` en 3000).

---

## 7. Directrices Adicionales (Reglas de la IA)

Cualquier desarrollo futuro sobre este código debe respetar las siguientes reglas:

- **No modificar archivos pesados**: Los pesos como `yolov8n.pt` o los índices en `qdrant_data/` están fuera del control de versiones (`.gitignore`).
- **Persistencia en Qdrant**: La evolución del sistema apunta a integrar Qdrant para manejo híbrido y escalable de los vectores, reemplazando el uso exclusivo de `.npy` en memoria si el volumen crece.
- **Frontend estricto:** Todo desarrollo de UI debe realizarse sobre la app Next.js existente. No se permite el uso de Streamlit.
- **Reranking activo:** Las mejoras al orden de resultados deben apoyarse en el uso de descriptores visuales (`descriptores.json`), que son obligatorios para el endpoint del Hito 2.
