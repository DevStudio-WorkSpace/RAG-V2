# proyectoA · Búsqueda visual RAG + Evaluación + Search-10

Módulo autocontenido del proyecto de **búsqueda visual de camisetas deportivas**
basado en embeddings CLIP/OpenCLIP/SigLIP. Incluye el frontend Next.js completo
(búsqueda por imagen, evaluador con feedback y Search-10 de entrenamiento con
re-ranking) y el backend dedicado de Search-10. Aquí vive todo el código front
y los servicios que lo sirven; el motor RAG de la raíz (`api/`) se **importa,
no se modifica**.

## Participantes

- **Sebastian Lopes**
- **Kevin Chacon**

---

## Funcionalidades

1. **Búsqueda visual (`/`)** — subes una imagen de camiseta, la API devuelve el
   **Top 5** de diseños visualmente más parecidos con su score, y podes
   calificar cada resultado (**Acierto / Sirve / No sirve**). Los veredictos se
   persisten (localStorage + API) y las tarjetas marcadas como "No sirve" se
   ocultan en la vista.
2. **Modelo de búsqueda** — por defecto usa la **Fusión (CLIP + OpenCLIP +
   SigLIP)**, el motor con mejores estadísticas de la API (84% Top 1 / 90%
   Top 5, vs 60-66% del CLIP solo). Desde el selector también se pueden probar
   `CLIP` y `OpenCLIP`; la fusión está marcada como "(mejor)".
3. **Evaluador (`/evaluacion`)** — panel unificado con dos pestañas:
   - **📋 Evaluador** — recorre los casos de `proyectoA/Search-10/`, califica
     los 5 resultados y guarda cada juicio usando **siempre el modelo Fusión**
     (fijo, para que la evaluación sea consistente).
   - **🎯 Search-10 · Entrenar** — ranking real con **retroalimentación**:
     cada tarjeta se califica y los resultados **Incorrecto** quedan excluidos
     de forma persistente en futuras búsquedas de esa misma imagen.
4. **Tema claro/oscuro + branding** — logo, paleta roja (`#e01010`) y toggle de
   tema en la barra de navegación.

---

## Arquitectura

```text
proyectoA/
├── Search-10/                # Imágenes de consulta (agrega/cambia aquí)
├── backend/
│   └── main.py               # Servidor FastAPI Search-10 (puerto 8400) — NO toca api/
├── .feedback/
│   └── feedback.json         # Entrenamiento persistente (se crea solo)
├── frontend-next/            # Frontend Next.js completo
│   ├── app/
│   │   ├── layout.tsx        # Barra de navegación, logo, ThemeToggle
│   │   ├── page.tsx          # Búsqueda visual (/)
│   │   ├── evaluacion/       # Evaluador + Search-10 en pestañas (/evaluacion)
│   │   ├── search10/         # Search-10 como vista propia (/search10)
│   │   ├── components/       # ThemeToggle.tsx, ModelSelect.tsx
│   │   ├── globals.css       # Paleta roja, tema claro/oscuro
│   │   └── public/sublitex.png
│   └── package.json
└── README.md                 # Este documento
```

El backend de Search-10 **importa** (no modifica) el motor RAG de la raíz:
`api.preprocesar_consulta`, `api.search_engine_hito2` y `api.main` (solo usa sus
helpers de embedding). Las rutas de datos son relativas a sus propios archivos,
así que apuntan a `data/` aunque el working directory sea `proyectoA/`.

---

## 1 · Servicios y cómo correrlo

Necesitas los 3 servicios (3 terminales; usan el venv de la raíz):

```fish
# Terminal 1 — API principal (motor RAG, puerto 8000) — desde la raíz
cd /home/satanic/RAG-V2
./venv/bin/python -m uvicorn api.main:app --port 8000
```

```fish
# Terminal 2 — backend Search-10 (puerto 8400) — desde proyectoA
cd /home/satanic/RAG-V2/proyectoA
../venv/bin/python -m uvicorn backend.main:app --port 8400
```

```fish
# Terminal 3 — frontend Next.js
cd /home/satanic/RAG-V2/proyectoA/frontend-next
npm run dev        # abre http://localhost:3000
```

Con el frontend en `http://localhost:3000`:

| Ruta | Qué es |
|---|---|
| `/` | Búsqueda visual + calificación (usa API 8000) |
| `/evaluacion` | Evaluador + Search-10 · Entrenar en pestañas |
| `/search10` | Search-10 como vista suelta (usa API 8400) |

Health check del backend Search-10:

```bash
curl http://localhost:8400/search10/imagenes
```

---

## 2 · Endpoints

### API principal — `http://localhost:8000`

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/search/image` | `{file, modo, modelo}` → Top 5 de resultados |
| `GET` | `/evaluacion/veredictos` | Veredictos guardados para la web |
| `POST` | `/evaluacion/guardar` | Guarda un juicio `(caso, id_resultado, juicio)` |
| `POST` | `/evaluacion/completar` | Marca un caso como evaluado |
| `GET` | `/evaluacion/estado` | Estado de la evaluación (casos pendientes) |

### Backend Search-10 — `http://localhost:8400`

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/search10/buscar` | `{imagen, modelo?, top_k?}` → ranking real (exclusiones aplicadas) |
| `POST` | `/search10/feedback` | `{imagen, id_resultado, juicio}` → guarda `acierto/sirve/incorrecto` |
| `GET` | `/search10/feedback` | Estado completo `{consulta: {id: juicio}}` |
| `POST` | `/search10/feedback/limpiar` | `{imagen?}` → limpia una consulta o todo (`imagen: null`) |
| `GET` | `/search10/imagenes` | Lista de consultas disponibles |
| `GET` | `/search10/images/<archivo>` | Imagen de consulta (static) |

El archivo de persistencia del entrenamiento es `proyectoA/.feedback/feedback.json`.

---

## 3 · Ciclo de entrenamiento (Search-10)

1. Abre **http://localhost:3000/evaluacion** y selecciona la pestaña
   **🎯 Search-10 · Entrenar**.
2. Haz clic en una imagen de consulta → se ejecuta la búsqueda real y aparece
   el **Top 5** con su score.
3. Califica cada tarjeta:
   - **✅ Correcto** — el resultado es el mismo diseño.
   - **👍 Sirve** — no es el mismo, pero es aceptable.
   - **❌ Incorrecto** — es otro diseño → queda **excluido**.
4. Al marcar **Incorrecto**, el sistema **re-busca al instante** y ese resultado
   desaparece del Top 5; los siguientes candidatos válidos del pool toman su
   lugar.
5. Recarga la página o vuelve a esa consulta en otra sesión: los excluidos
   siguen sin aparecer (persistencia real en `proyectoA/.feedback/feedback.json`).

Para probar con datos nuevos: copia más imágenes a `proyectoA/Search-10/`,
recarga y pulsa **"↻ Actualizar feedback"** si hiciera falta.

---

## 4 · Reiniciar / limpiar el feedback

Desde la interfaz:

- **Borrar feedback de esta consulta** — limpia solo la consulta seleccionada.
- **Limpiar TODO el feedback** — borra todo el historial de entrenamiento.

Por API:

```bash
# Limpiar una consulta:
curl -X POST http://localhost:8400/search10/feedback/limpiar \
  -H "Content-Type: application/json" -d '{"imagen":"messi.jpg"}'

# Limpiar todo:
curl -X POST http://localhost:8400/search10/feedback/limpiar \
  -H "Content-Type: application/json" -d '{"imagen":null}'
```

Manual: borra el archivo `proyectoA/.feedback/feedback.json` (o toda la carpeta
`.feedback/`). Al borrarlo, el sistema vuelve a permitir que todas las
alternativas aparezcan.