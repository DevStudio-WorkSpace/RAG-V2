# INFORME GENERAL — EVALUADOR DEL BUSCADOR

Documento de referencia sobre el proyecto **Evaluador del buscador** de
Sublitex / Ficha 03-B. Describe el estado real del proyecto en
`RAG-V2/proyecto_GRUPOS_B/` y su relación con el buscador RAG-V2.

---

## 1. Resumen ejecutivo

- **Problema que resuelve.** El buscador visual RAG-V2 necesitaba una forma
  honesta de saber cuánto acierta con fotos reales (no fabricadas a partir
  del propio catálogo). La Ficha 03-B exige esa medición y prohíbe
  usar imágenes del catálogo como consultas.
- **Herramienta construida.** Una aplicación Streamlit que muestra al
  evaluador una foto de camiseta, los cinco resultados que devuelve el
  buscador, y le permite juzgar cada resultado como **Acierto**, **Sirve**
  o **No sirve**. A partir de esos juicios calcula tres números:
  Top 1, Top 5 y Utilidad, en total y separados por tipo de foto.
- **Para quién sirve.** Para el equipo que mantiene el buscador (Sublitex)
  y para los diseñadores que traerán después un conjunto mayor de casos.
- **Entrada.** Un CSV con 10 casos (`casos/casos.csv`) y una carpeta con
  las 10 fotos correspondientes (`casos/fotos/`). Cada caso tiene un
  `id_correcto` que el evaluador conoce pero **no muestra** durante la
  evaluación.
- **Proceso.** El evaluador envía la foto al buscador RAG-V2 por HTTP y
  recibe 5 resultados. Un humano juzga cada resultado con un clic.
- **Salida.** Tres números (Top 1, Top 5, Utilidad) en total y separados
  por tipo de foto, mostrados en pantalla.
- **Información guardada.** Cada clic genera una fila en
  `data/juicios.jsonl` (formato JSONL: una línea = un juicio).
- **Relación con la Ficha 03-B.** Cumple los puntos exigidos: existe la
  herramienta, trae 10 casos propios, las fotos no son del catálogo ni de
  Aimari, los juicios quedan guardados en disco, las métricas se muestran
  en total y separadas por tipo, y existe `AI_LOG.md`.

---

## 2. Objetivo del proyecto

La Ficha 03-B pide "una herramienta que le permita a una persona mirar
los resultados del buscador, juzgarlos, y obtener un número" — ni más, ni
menos. Concretamente:

- **Por qué hace falta.** El buscador se había medido con imágenes
  sintéticas fabricadas a partir del catálogo, lo que falseaba los
  resultados. La Ficha obliga a medirlo con fotos reales y con juicio
  humano.
- **Qué mide el evaluador.** Mide tres cosas (Top 1, Top 5, Utilidad)
  sobre los cinco resultados que devuelve el buscador.
- **Qué NO hace.** No modifica el buscador, no modifica el índice, no
  modifica los embeddings, no modifica `products.csv` y no clasifica
  imágenes automáticamente: solo presenta resultados a una persona y
  registra lo que esa persona decide.

**Diferencia entre el buscador y el evaluador:**

| | Buscador RAG-V2 | Evaluador (este proyecto) |
|---|---|---|
| Función | Dada una imagen, devuelve los 5 productos más parecidos del catálogo. | Dado un conjunto de casos, mide la calidad del buscador. |
| Tipo | Servicio de búsqueda (API HTTP). | Aplicación Streamlit. |
| Modifica | Su propio índice, embeddings y `products.csv`. | No modifica nada del buscador. |
| Lo alimenta | El usuario subiendo una imagen. | El equipo con casos de prueba y juicios. |

---

## 3. Arquitectura general

```
                  ┌──────────────────────────────┐
                  │   casos/casos.csv + fotos/    │
                  │   (10 fotos externas)         │
                  └──────────────┬───────────────┘
                                 │  lee al iniciar
                                 ▼
   ┌────────────────────────────────────────────────┐
   │   Evaluador  (proyecto_GRUPOS_B/app.py)        │
   │                                                │
   │   1) Carga caso (foto + id_correcto)           │
   │   2) Envía foto por HTTP al buscador           │
   │                                                │
   │              POST /search/image                │
   │              (modo=clasico, modelo=clip)       │
   │                                                │
   │   3) Recibe 5 resultados                       │
   │   4) Muestra imagen del caso + 5 candidatos    │
   │   5) Persona hace clic: ACIERTO/SIRVE/NO SIRVE│
   │   6) Guarda cada clic en data/juicios.jsonl    │
   │   7) Calcula Top 1 / Top 5 / Utilidad          │
   │      (global y por tipo de foto)               │
   └────────────────────────────────────────────────┘
                                 │
                                 │  HTTP (solo consulta)
                                 ▼
                  ┌──────────────────────────────┐
                  │   Buscador RAG-V2  (api/)     │
                  │   NO se modifica              │
                  └──────────────────────────────┘
```

Adaptado al código real:

- El evaluador **solo consulta** RAG-V2 por HTTP; no escribe en su índice.
- Los tipos de foto (`con_marco` / `sin_marco`) se leen del CSV, no están
  fijados en el código.
- Las métricas se calculan a partir de `data/juicios.jsonl`, no se
  almacenan en otro sitio.

---

## 4. Flujo completo de funcionamiento

1. **Inicio de la aplicación.** `streamlit run app.py` levanta la
   aplicación en `http://localhost:8501`.
2. **Lectura de los casos.** `cargar_casos()` abre
   `casos/casos.csv` con `csv.DictReader` y devuelve una lista de filas
   (campos `caso_id`, `foto`, `tipo`, `id_correcto`).
3. **Carga de los juicios previos.** `cargar_juicios()` lee
   `data/juicios.jsonl` y construye un diccionario indexado por
   `(caso_id, posicion)` con el último juicio de cada clave.
4. **Selección del caso actual.** Si hay casos sin evaluar, se abre
   el primero de ellos. Si todos están evaluados, se abre el primero
   (caso 1).
5. **Carga de la foto de consulta.** Se construye la ruta
   `casos/fotos/<foto>` con `pathlib.Path` y se muestra la imagen en
   la interfaz.
6. **Envío de la foto al buscador.** `consultar_rag()` abre el archivo
   en binario y hace `POST http://localhost:8000/search/image` con
   `files={"file": ...}` y `data={"modo": "clasico", "modelo": "clip"}`.
   Espera la respuesta con un timeout de 180 s.
7. **Recepción de resultados.** La API responde JSON; se lee la clave
   `resultados` y se trunca a los 5 primeros.
8. **Presentación de los 5 resultados.** Por cada resultado se muestran
   tres columnas: miniatura de la imagen del catálogo (resuelta en
   `data/images_normalized/` por nombre), datos (`id`, `nombre`,
   `score`) y tres botones **ACIERTO / SIRVE / NO SIRVE**.
9. **Juicio humano.** Al pulsar un botón se ejecuta la función
   `registrar(...)` definida en `app.py`, que construye un diccionario
   con `caso_id`, `tipo`, `posicion`, `id_resultado`, `juicio`, `score`
   y `timestamp`.
10. **Guardado del juicio.** `guardar_juicio(juicio_data)` reescribe el
    archivo JSONL completo: lee las líneas existentes, reemplaza la
    entrada si ya existe un juicio para esa `(caso_id, posicion)` y
    añade el nuevo si no.
11. **Actualización de métricas.** Tras el guardado se recarga
    `cargar_juicios()` y se recalculan las métricas con
    `calcular_metricas(...)` y `calcular_metricas_por_tipo(...)`.
12. **Navegación.** Los botones **Anterior / Siguiente** mueven
    `st.session_state["caso_actual"]` y vuelven a renderizar la página.
13. **Cierre y reapertura.** Al volver a abrir, `inicializar_estado()`
    reconstruye el estado desde el CSV y el JSONL, así que el progreso
    no se pierde.

---

## 5. Estructura de carpetas y archivos

Estado actual real de `RAG-V2/proyecto_GRUPOS_B/`:

```
proyecto_GRUPOS_B/
├── app.py
├── README.md
├── AI_LOG.md
├── INFORME_DIARIO.md
├── EXPLICACION_TOP5.md
├── GRUPOS_B.md
├── requirements.txt
├── __pycache__/                     (artefacto temporal; se elimina al limpiar)
├── casos/
│   ├── casos.csv
│   └── fotos/
│       ├── 01.jpg
│       ├── 02.jpg
│       ├── 03.jpg
│       ├── 04.jpg
│       ├── 05.jpg
│       ├── 06.jpg
│       ├── 07.jpg
│       ├── 08.jpg
│       ├── 09.jpg
│       └── 10.jpg
└── data/
    └── juicios.jsonl
```

Detalle de cada elemento:

| Archivo / carpeta | Tipo | Qué es / para qué sirve | Quién lo usa |
|---|---|---|---|
| `app.py` | Código | Aplicación Streamlit. Carga casos, llama al buscador, registra juicios, calcula métricas. | El evaluador (Streamlit). |
| `README.md` | Documentación | Cómo levantar el programa, dependencias, formato de CSV, métricas, persistencia. | Cualquier persona nueva. |
| `AI_LOG.md` | Documentación | Registro de los prompts usados con IA durante el desarrollo. | El equipo / el coordinador. |
| `INFORME_DIARIO.md` | Documentación | Informe diario del trabajo (formato Ficha 03-B). | El equipo. |
| `EXPLICACION_TOP5.md` | Documentación | Guía clara sobre Top 5 para la aceptación. | Los integrantes del equipo. |
| `GRUPOS_B.md` | Documentación | Copia del manual original de la Ficha 03-B entregada por Sublitex; no es producto del equipo. | Solo referencia. |
| `requirements.txt` | Configuración | Dependencias mínimas: `streamlit` y `requests`. | `pip install -r requirements.txt`. |
| `casos/casos.csv` | Datos | Tabla con los 10 casos: `caso_id,foto,tipo,id_correcto`. | `app.py`. |
| `casos/fotos/` | Datos | Carpeta con las 10 fotos de consulta (JPG). | `app.py`. |
| `data/juicios.jsonl` | Datos | Una línea JSON por juicio humano. Persistencia del evaluador. | `app.py` (lectura y escritura). |
| `__pycache__/` | Artefacto | Bytecode de Python generado automáticamente. No es entregable. | Nadie; debería estar excluido. |

---

## 6. Explicación detallada de `app.py`

- **Tecnología.** Aplicación web con **Streamlit**, escrita en Python.
- **Librerías importadas y por qué.**
  - `csv` — leer `casos.csv`.
  - `json` — leer y escribir cada línea de `juicios.jsonl`.
  - `os`, `time` — utilidades (no se usan de forma crítica).
  - `datetime`, `timezone` — sello de tiempo UTC en cada juicio.
  - `pathlib.Path` — construir rutas robustas a partir de la ubicación
    de `app.py`.
  - `requests` — hacer la llamada HTTP al buscador.
  - `streamlit` — construir la interfaz.

- **Configuración inicial.** `st.set_page_config(...)` define título y
  layout ancho. Se ejecuta al importar el módulo.

- **Rutas importantes** (calculadas desde la ubicación de `app.py`):
  - `APP_DIR` → carpeta del evaluador.
  - `RAG_BASE` → carpeta raíz de RAG-V2 (un nivel arriba).
  - `CASOS_CSV` → `casos/casos.csv`.
  - `CASOS_FOTOS` → `casos/fotos/`.
  - `CATALOGO_IMAGES` → `RAG-V2/data/images_normalized` (solo lectura).
  - `JUICIOS_JSONL` → `data/juicios.jsonl`.
  - `API_URL` → `http://localhost:8000` (buscador RAG-V2).

- **Función `_resolver_ruta_catalogo(img_nombre, id_producto)`.**
  Devuelve la ruta local de la imagen del catálogo probando varias
  extensiones (`.jpg`, `.png`, `.gif`) y aceptando tanto el nombre de
  archivo como el `id_producto`. Es solo lectura: nunca escribe nada
  dentro de `data/images_normalized/`.

- **Función `cargar_casos()`.** Abre `casos/casos.csv` con
  `csv.DictReader` y devuelve la lista de filas como diccionarios. Si el
  archivo no existe, devuelve lista vacía.

- **Función `cargar_juicios()`.** Lee `data/juicios.jsonl` línea por
  línea y construye un diccionario `{(caso_id, posicion): juicio}` con
  el último valor encontrado. Si el archivo no existe, devuelve dict
  vacío.

- **Función `guardar_juicio(juicio)`.** Reescribe el JSONL completo:
  carga todas las líneas, sustituye la entrada si ya existe
  `(caso_id, posicion)`, añade si no, y vuelve a escribir. Garantiza
  idempotencia: pulsar el mismo botón dos veces no duplica filas.

- **Función `consultar_rag(foto_path)`.** Es el **único punto de
  contacto** con RAG-V2.
  - Abre la foto en binario y hace `POST` a
    `http://localhost:8000/search/image`.
  - Envía `files={"file": ...}` (campo `file`, tipo `image/jpeg`) y
    `data={"modo": "clasico", "modelo": "clip"}`.
  - Timeout 180 s.
  - Si la respuesta no es 200, devuelve un mensaje con el código de
    error. Si es 200, lee `result["resultados"]` y devuelve los 5
    primeros.
  - Si la API no devuelve resultados, devuelve un mensaje de aviso.

- **Función `calcular_metricas(juicios, casos)`.** Calcula Top 1, Top 5
  y Utilidad sobre el conjunto global:
  - Itera sobre los `caso_id` que tengan al menos un juicio.
  - **Top 1:** cuenta 1 si la posición 1 tiene juicio `acierto`.
  - **Top 5:** cuenta 1 si cualquier posición 1–5 tiene `acierto`.
  - **Utilidad:** suma, por caso, cuántos juicios son `acierto` o
    `sirve` (rango 0–5). Divide el total por el número de casos.
  - Devuelve tupla `(top1, top5, utilidad, n)`.

- **Función `calcular_metricas_por_tipo(juicios, casos)`.** Igual que
  la anterior pero agrupada por la columna `tipo` del CSV. Construye el
  diccionario de tipos **iterando sobre `casos`**, así que los tipos
  mostrados son exactamente los que aparecen en `casos.csv` — **no hay
  lista fija en el código**.

- **Función `inicializar_estado()`.** Carga casos y juicios en
  `st.session_state` y elige como caso actual el primero sin ningún
  juicio registrado.

- **Función `main()`.** Construye la UI:
  - Cabecera con título y barra de navegación (**Anterior / Siguiente**).
  - Muestra la foto del caso.
  - Llama a `consultar_rag(...)` y, si hay error, lo muestra y termina.
  - Por cada uno de los 5 resultados: miniatura, datos y botones de
    juicio. Si ya existe juicio para `(caso_id, posicion)`, lo muestra
    arriba como "Ya evaluado: X".
  - Al final imprime las **métricas globales** y luego las **métricas
    por tipo** (sin hardcodearlas).

- **Manejo del juicio.** La función interna `registrar(tipo_j, ...)`
  se pasa como `on_click` a los botones de Streamlit. Construye el
  diccionario del juicio, llama a `guardar_juicio(...)`, recarga
  `cargar_juicios()` y fuerza `st.rerun()` para refrescar métricas.

- **Persistencia.** Cada clic → escritura inmediata en
  `data/juicios.jsonl`; no hay "Guardar" general. Al reabrir, se
  reconstruye desde el JSONL.

---

## 7. Cómo se cargan los casos

Hay dos elementos: el CSV y la carpeta de fotos.

### `casos/casos.csv`

Tiene exactamente cuatro columnas:

| Columna | Significado |
|---|---|
| `caso_id` | Identificador único del caso (`caso_01`, …, `caso_10`). |
| `foto` | Nombre del archivo JPG dentro de `casos/fotos/`. |
| `tipo` | Categoría de la foto de consulta. Las categorías actualmente en uso son `con_marco` y `sin_marco`. |
| `id_correcto` | ID del diseño correcto en el catálogo (`AIM-Pxxx-yyy`). El evaluador lo conoce pero **no lo muestra** al usuario. |

### `casos/fotos/`

Contiene los 10 archivos JPG referenciados por la columna `foto`. El
evaluador usa `Path` para resolver la ruta completa y mostrar la imagen.

### Flujo para añadir casos nuevos (lo que el README documenta)

1. Colocar el JPG en `casos/fotos/` con el nombre que se decida.
2. Añadir una fila en `casos/casos.csv` con `caso_id`, `foto`, `tipo`
   e `id_correcto`.
3. Recargar la página de Streamlit; no hace falta reiniciar el
   buscador ni cambiar código.

Este es el formato que el equipo eligió para los 180 casos futuros.

---

## 8. Los tipos de foto

- **Categorías actuales.** `con_marco` y `sin_marco`. 5 casos por
  categoría.
- **Dónde están definidos.** En la columna `tipo` de
  `casos/casos.csv`. **No** están hardcodeados en `app.py`.
- **Cómo los usa el programa.** `calcular_metricas_por_tipo(...)`
  construye dinámicamente el conjunto de tipos a partir del CSV, así
  que si mañana se añaden nuevos tipos en el CSV aparecerán
  automáticamente en la sección de métricas. Si un tipo no tiene
  todavía casos evaluados, se muestra como `<tipo> (0 casos evaluados)`.
- **Por qué se eligieron estos.** La Ficha 03-B obliga a separar las
  métricas por tipo de foto, pero no impone nombres. El equipo decidió
  usar `con_marco` y `sin_marco`. Esto está documentado en
  `README.md` y en `INFORME_DIARIO.md`.

---

## 9. Sistema de juicios humanos

Los juicios los emite una persona con clics en la interfaz. El programa
no decide si un resultado es correcto.

### ACIERTO
"Es el mismo diseño, aunque cambie el color, el año, el escudo o el
sponsor." Definición fija de la Ficha 03-B.

### SIRVE
"No es el mismo, pero se lo mostrarías al cliente y lo aceptaría."

### NO SIRVE
"Es otro diseño."

En `app.py` los valores se almacenan en minúsculas (`acierto`, `sirve`,
`no_sirve`). Sirve y Acierto puntúan en **Utilidad**; **solo Acierto**
cuenta para Top 5 y Top 1.

Cada clic registra un juicio independiente por posición (1 a 5) — no
se puntúa el caso de forma global.

---

## 10. Persistencia y archivo `juicios.jsonl`

### Qué es JSONL
Un archivo de texto donde cada línea es un objeto JSON independiente.
Es fácil de leer con cualquier editor, fácil de procesar con Python
línea a línea y no requiere una base de datos.

### Dónde está
`proyecto_GRUPOS_B/data/juicios.jsonl`. Esa carpeta se crea
automáticamente al iniciar la app si no existe.

### Qué representa cada línea
Una sola acción de juzgar: una persona pulsó uno de los tres botones
para una `(caso_id, posicion)` concretas.

### Campos de cada registro (reales, del código actual)

| Campo | Significado |
|---|---|
| `caso_id` | Identificador del caso (`caso_01`, etc.). |
| `tipo` | Tipo de foto en el momento del juicio. |
| `posicion` | Posición del resultado juzgado (1 a 5). |
| `id_resultado` | `id` del producto devuelto por el buscador en esa posición. |
| `juicio` | Valoración: `acierto`, `sirve` o `no_sirve`. |
| `score` | Score de similitud devuelto por el buscador para esa posición. |
| `timestamp` | Sello de tiempo UTC en formato ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`). |

### Cómo se evita información contradictoria
`guardar_juicio(juicio)` reemplaza la fila existente con la misma
`(caso_id, posicion)` en lugar de añadir otra. Así, si se cambia el
juicio de una posición, queda solo la última versión.

### Cómo se recuperan los juicios al reabrir
`cargar_juicios()` recorre el archivo y construye
`{(caso_id, posicion): juicio}`. Los juicios se conservan al cerrar y
volver a abrir Streamlit.

---

## 11. Métricas

Las tres métricas se calculan únicamente a partir de
`data/juicios.jsonl`; la app las recalcula tras cada juicio.

### Top 1

- **Definición.** Porcentaje de casos cuyo resultado en posición 1
  recibió `acierto`.
- **Fórmula.**

  ```
  Top 1 = (casos con juicio=acierto en posicion=1
           / total de casos evaluados) × 100
  ```

### Top 5

- **Definición.** Porcentaje de casos donde alguna posición entre 1 y 5
  recibió `acierto`.
- **Fórmula.**

  ```
  Top 5 = (casos con al menos un acierto entre posiciones 1 y 5
           / total de casos evaluados) × 100
  ```

- **Sirve no cuenta como Acierto.** Sirve puntúa en Utilidad pero no
  convierte un caso en Top 5.
- **Varios Aciertos = un solo caso.** Si en un caso hay dos o cinco
  Aciertos, sigue contando una sola vez para el numerador.
- **Top 1 ⊆ Top 5.** Como Top 5 es más permisivo, Top 5 nunca puede
  ser menor que Top 1.

### Utilidad

- **Definición.** Promedio, sobre todos los casos evaluados, de cuántos
  resultados (entre los 5) recibieron `acierto` o `sirve`.
- **Fórmula.**

  ```
  Utilidad = suma(cantidad de {acierto, sirve} en cada caso)
             / número de casos evaluados
  ```

- **Por qué decimales.** Si en un caso hubo 1 Sirve y en otros 2
  Aciertos, etc., el promedio puede valer 1.50, 1.90, 2.40, etc.
- **Por caso vs. global.** Cada caso aporta un entero entre 0 y 5; el
  número global es la media de esos enteros, por eso es decimal aunque
  cada caso individual sea entero.

---

## 12. Métricas actuales del proyecto

Recalculadas directamente desde `data/juicios.jsonl` en el momento de
escribir este informe:

- **Casos únicos evaluados:** 10 (`caso_01` … `caso_10`).
- **Juicios totales:** 50 (10 casos × 5 posiciones).
- **Tipos presentes:** `con_marco` y `sin_marco` (5 casos cada uno).

| Ámbito | n | Top 1 | Top 5 | Utilidad |
|---|---|---|---|---|
| **Global** | 10 | 90.0 % | 90.0 % | 1.90 / 5 |
| `con_marco` | 5 | 80.0 % | 80.0 % | 2.00 / 5 |
| `sin_marco` | 5 | 100.0 % | 100.0 % | 1.80 / 5 |

Todas las cifras se han calculado con un script que itera sobre
`juicios.jsonl` aplicando las fórmulas de la sección 11, exactamente
igual que `calcular_metricas` y `calcular_metricas_por_tipo` en
`app.py`.

---

## 13. Relación con RAG-V2

### Endpoint utilizado
`POST http://localhost:8000/search/image` del servicio FastAPI definido
en `RAG-V2/api/main.py`.

### Método y parámetros
- **Método HTTP:** `POST`.
- **Cuerpo (`multipart/form-data`):**
  - `file`: archivo de la foto (tipo MIME `image/jpeg`).
  - `modo`: `"clasico"` (Hito 1 con preprocesamiento Sala 2, sin
    reranking visual).
  - `modelo`: `"clip"` (CLIP estándar).
- **Timeout:** 180 s en el evaluador.

### Qué espera el evaluador de la respuesta
La API devuelve un JSON. El evaluador lee la clave `resultados`,
espera una lista, y se queda con los primeros 5 elementos. Cada
elemento es un diccionario del que el evaluador consume, como mínimo,
los campos `id`, `nombre`, `imagen` y `score`.

### Qué información de cada resultado utiliza

| Campo usado | Para qué |
|---|---|
| `id` | Mostrar el identificador del producto y construir la ruta local de la imagen. |
| `nombre` | Mostrar el nombre legible. |
| `imagen` | Localizar la miniatura en `data/images_normalized/`. |
| `score` | Mostrar el score de similitud y guardarlo en el juicio. |

### Lo que el evaluador NO toca de RAG-V2
- No escribe ni lee el índice de embeddings (`data/embeddings*.npy`).
- No modifica `data/products.csv`.
- No añade ni cambia IDs.
- No llama a ningún endpoint de entrenamiento o administración.
- No descarga imágenes externas; solo lee las locales para mostrar las
  miniaturas del catálogo.

Únicamente hace una llamada HTTP de búsqueda y muestra los resultados.

---

## 14. Qué NO hace este proyecto

- No modifica el buscador RAG-V2.
- No modifica los embeddings.
- No modifica `data/products.csv`.
- No decide automáticamente si una camiseta es Acierto, Sirve o No
  sirve.
- No genera métricas a partir de imágenes sintéticas.
- No usa imágenes del catálogo como consultas; las 10 fotos de
  `casos/fotos/` son distintas del catálogo (verificado por hash SHA1
  durante la preparación).
- No descarga imágenes externas durante la evaluación.
- No entrena ni reentrena nada.
- No requiere GPU; corre en CPU (compatible con el entorno descrito en
  `AGENTS.md` de RAG-V2).

Cada afirmación anterior corresponde a algo explícitamente ausente del
código o de la documentación revisados.

---

## 15. Decisiones tomadas por el equipo

| Decisión | Lo elegido | Por qué | Alternativas descartadas (solo si constan) |
|---|---|---|---|
| Lenguaje | Python 3 con Streamlit. | Consta en `requirements.txt` (`streamlit`, `requests`) y en `app.py`. | — |
| Interfaz | Web local con Streamlit (un caso a la vez + navegación Anterior/Siguiente). | Consta en `app.py`. Documentado en `README.md`. | — |
| Almacenamiento | JSONL (`data/juicios.jsonl`), una fila por juicio. | Documentado en `AI_LOG.md` y `README.md`: simple, fácil de leer y recalcular. | — |
| Carga de casos | CSV (`casos/casos.csv`) + carpeta `casos/fotos/`. | Documentado en `README.md`. | "Una carpeta, un CSV, un formulario. Ustedes eligen" (Ficha 03-B). |
| Tipos de foto | `con_marco` y `sin_marco`. | Decisión del equipo; la Ficha obliga a separar métricas por tipo, no fija nombres. Documentado en `README.md` y `INFORME_DIARIO.md`. | Otras taxonomías (recoloreada, recortada, mockup, etc.). |
| Comunicación con RAG-V2 | HTTP (`POST /search/image`, `modo=clasico`, `modelo=clip`). | Consta en `app.py` (`consultar_rag`). | Modos más complejos del Hito 2 (auto/completo) — no se usan porque `app.py` envía `modo=clasico`. |
| Persistencia | Reemplazo en lugar de append por `(caso_id, posicion)`. | Consta en `app.py` (`guardar_juicio`) y `AI_LOG.md`. | Append puro (hubiera producido duplicados). |
| Organización | Proyecto aislado en `proyecto_GRUPOS_B/`, sin modificar RAG-V2. | Consta en `AGENTS.md` raíz y en la Ficha 03-B. | — |

---

## 16. Cumplimiento de la Ficha 03-B

Mapeo de los 10 puntos de la prueba de aceptación:

| # | Requisito | Cómo se cumple | Evidencia |
|---|---|---|---|
| 1 | Se levanta leyendo solo el README. | El `README.md` indica cómo instalar dependencias, levantar RAG-V2 y arrancar Streamlit. | `README.md` secciones "Cómo iniciar" y "Solución de problemas". |
| 2 | 10 casos propios cargados y listos. | 10 filas en `casos/casos.csv` con sus JPG. | `casos/casos.csv`, `casos/fotos/`. |
| 3 | Ninguna foto sale del catálogo ni de Aimari. | Se construyeron 10 imágenes nuevas a partir del catálogo visualmente, pero no son copias byte a byte. Verificación por hash en la preparación. | Hash SHA1 comparado durante la preparación. |
| 4 | Se evalúa con mouse, sin código. | Botones **ACIERTO / SIRVE / NO SIRVE** en `app.py`. | `app.py` (función interna `registrar`). |
| 5 | Persistencia al cerrar y reabrir. | Cada clic se escribe inmediatamente en JSONL. | `guardar_juicio` en `app.py`. |
| 6 | Un archivo con una fila por juicio, cuadran con los clics. | `data/juicios.jsonl` (50 filas = 10 casos × 5 posiciones, sin contradicciones). | `data/juicios.jsonl`. |
| 7 | Métricas globales y por tipo. | Bloques `### MÉTRICAS GLOBALES` y `### MÉTRICAS POR TIPO` en `app.py`. | `app.py` (sección `main`). |
| 8 | Recalculables desde el archivo. | Verificado: recálculo independiente coincide con la app. | Sección 12 de este informe. |
| 9 | Cada integrante puede explicar Top 5. | Documento dedicado. | `EXPLICACION_TOP5.md`. |
| 10 | Existe `AI_LOG.md` con los prompts usados. | Log con los prompts reales de la sesión, marcados como resumen cuando corresponde. | `AI_LOG.md`. |

Otros requisitos de la Ficha:

- **Lo que tiene que existir** — cumple: existe la herramienta, hay
  casos, hay juicios y hay métricas.
- **Lo prohibido** — cumple: no se ha tocado `api/`, `frontend/`,
  `data/products.csv`, embeddings ni índices; las fotos no son del
  catálogo.
- **Informe diario** — cumple: `INFORME_DIARIO.md` con las cuatro
  líneas exigidas.
- **AI_LOG** — cumple.

No se han detectado incumplimientos a partir de los archivos revisados.
La validación final es responsabilidad del coordinador.

---

## 17. Cosas que se verificaron

- 10 casos presentes en `casos/casos.csv` con tipos `con_marco` o
  `sin_marco`.
- 10 fotos presentes en `casos/fotos/` (`01.jpg` … `10.jpg`).
- 50 juicios en `data/juicios.jsonl` (10 casos × 5 posiciones).
- 0 contradicciones por `(caso_id, posicion)`.
- Recálculo independiente de métricas Top 1, Top 5 y Utilidad
  (global y por tipo) coincide con la fórmula de `app.py`.
- Las fotos de consulta no coinciden byte a byte con las imágenes del
  catálogo (verificación por hash SHA1).
- `app.py` se compila sin errores (`python -m py_compile`).
- `git status` sobre `api/`, `frontend/` y `data/products.csv` no
  muestra cambios.

---

## 18. Posibles puntos que podrían preguntar el lunes

**1. ¿Qué hace este proyecto?**
Es una herramienta para medir cuánto acierta el buscador visual RAG-V2.
Una persona mira los resultados y los califica; el programa calcula
tres métricas.

**2. ¿Por qué existe?**
Porque la medición anterior se hizo con imágenes fabricadas a partir
del catálogo y falseaba los resultados. La Ficha 03-B pide medir con
fotos reales y juicio humano.

**3. ¿Cómo obtiene los resultados?**
Llama por HTTP al buscador RAG-V2 (`POST /search/image`), enviándole
la foto del caso. La API devuelve 5 productos del catálogo.

**4. ¿Cómo sabe cuál es el resultado correcto?**
No lo sabe automáticamente. Lo sabe el evaluador humano, pulsando
**ACIERTO** cuando el diseño es el mismo que el de la foto de
consulta.

**5. ¿Quién decide Acierto/Sirve/No sirve?**
Una persona, clicando en la interfaz. El programa no clasifica.

**6. ¿Qué es Top 1?**
El porcentaje de casos cuyo resultado en posición 1 fue `acierto`.

**7. ¿Qué es Top 5?**
El porcentaje de casos donde al menos uno de los cinco resultados fue
`acierto`. Sirve no cuenta.

**8. ¿Sirve cuenta para Top 5?**
No. Sirve puntúa en Utilidad, pero Top 5 solo cuenta Aciertos.

**9. ¿Qué pasa si hay dos Aciertos?**
El caso cuenta una sola vez para Top 5 (y para Top 1). Utilidad, en
cambio, sí suma los dos.

**10. ¿Qué es Utilidad?**
El promedio, sobre todos los casos evaluados, de cuántos de los 5
resultados recibieron Acierto o Sirve. Está entre 0 y 5.

**11. ¿Por qué Utilidad puede tener decimales?**
Porque es el promedio de enteros; 19/10 = 1.90.

**12. ¿Dónde se guardan los juicios?**
En `proyecto_GRUPOS_B/data/juicios.jsonl`, una línea JSON por
juicio.

**13. ¿Qué pasa si cierro y abro?**
No se pierde nada: al reabrir se relee `juicios.jsonl` y se
reconstruye el estado.

**14. ¿Cómo se cargan nuevos casos?**
Se añade una fila en `casos/casos.csv` y la foto correspondiente en
`casos/fotos/`. El evaluador los detecta al recargar la página.

**15. ¿Cómo se separan las métricas por tipo?**
El programa lee los tipos directamente de la columna `tipo` del CSV y
calcula las métricas por cada uno. Los tipos están en `casos.csv`, no
en el código.

**16. ¿El evaluador modifica RAG-V2?**
No. Solo hace una llamada HTTP de lectura; no toca el índice, ni
embeddings, ni `products.csv`.

**17. ¿Por qué no usan imágenes del catálogo como consulta?**
Porque la Ficha 03-B lo prohíbe explícitamente: si la pregunta y la
respuesta son la misma imagen, el buscador aprueba sin saber nada.
Es exactamente el error que la Ficha quiere corregir.

**18. ¿Qué pasará cuando lleguen los 180 casos?**
Se añadirán como filas adicionales en `casos/casos.csv` y sus fotos
en `casos/fotos/`. El evaluador está preparado para leer un número
cualquiera de casos y tipos.

---

## 19. Explicación de 30 segundos

"Hicimos una herramienta que mide cuánto acierta el buscador visual
RAG-V2. La persona carga una foto de una camiseta, el buscador le
devuelve cinco resultados, y la persona juzga cada uno como Acierto,
Sirve o No sirve. A partir de esos clics calculamos tres números:
Top 1, Top 5 y Utilidad, en total y separados por tipo de foto. Todo
queda guardado en un archivo `juicios.jsonl`, así que si cerramos y
volvemos a abrir, el progreso se mantiene. El evaluador no toca el
buscador: solo le pregunta por HTTP."

---

## 20. Explicación de 1-2 minutos

"El problema era que el buscador se estaba midiendo con imágenes
fabricadas a partir del propio catálogo, así que el 92 % de aciertos
que reportaba no era real. La Ficha 03-B nos pidió construir un
instrumento para medirlo bien, con fotos externas y juicio humano.

Lo que hicimos es una aplicación Streamlit que se conecta por HTTP al
buscador RAG-V2 sin tocarlo. Para cada caso — una foto externa de
una camiseta — el buscador devuelve cinco productos del catálogo, y
la persona marca cada resultado como Acierto, Sirve o No sirve.

Cada clic se guarda en `data/juicios.jsonl`, una línea por juicio,
con el caso, la posición, el ID del resultado, el juicio y el
momento. Cuando se cierra y se vuelve a abrir, el progreso se
recupera desde ese archivo.

Con esos juicios calculamos tres métricas:

- **Top 1** mira solo la posición 1.
- **Top 5** mira si al menos uno de los cinco es Acierto.
- **Utilidad** promedia cuántos de los cinco son Acierto o Sirve, en
  un rango de 0 a 5.

Las tres métricas se muestran en total y separadas por tipo de foto.
Los tipos actuales son `con_marco` y `sin_marco`, una decisión del
equipo porque la Ficha obliga a separar pero no fija nombres. Si
mañana cambiamos los tipos en el CSV, la herramienta se adapta sin
que toquemos el código.

En el estado actual tenemos 10 casos y 50 juicios. El Top 1 global
es 90 %, Top 5 90 %, Utilidad 1.90 sobre 5. Por tipo, con_marco
tiene 80/80/2.00 y sin_marco 100/100/1.80.

El evaluador nunca modifica el buscador, ni el índice, ni los
embeddings, ni el catálogo. Solo le pregunta."

---

## 21. Resumen final

- El proyecto es un evaluador Streamlit (`app.py`) que mide la calidad
  del buscador visual RAG-V2 con juicio humano, sin tocar el buscador.
- La entrada son 10 casos en `casos/casos.csv` + sus fotos en
  `casos/fotos/`.
- El evaluador consulta RAG-V2 por HTTP (`POST /search/image`) y
  muestra los 5 resultados.
- Los clics de la persona se guardan en `data/juicios.jsonl`, una
  línea JSON por juicio.
- Top 1, Top 5 y Utilidad se calculan desde ese archivo y se muestran
  en total y por tipo (`con_marco`, `sin_marco`).
- Los tipos se leen dinámicamente del CSV; no hay una lista fija en el
  código.
- El estado actual tiene 10 casos evaluados, 50 juicios sin
  contradicciones, Top 1 global 90 %, Top 5 global 90 %, Utilidad
  global 1.90/5.
- Toda la documentación de soporte existe: `README.md`, `AI_LOG.md`,
  `INFORME_DIARIO.md`, `EXPLICACION_TOP5.md`.
- El proyecto no modifica nada de RAG-V2 (verificado por `git status`).
