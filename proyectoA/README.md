# proyectoA · Search-10 — Re-ranking con retroalimentación (feedback loop)

Módulo autocontenido para **entrenar/probar el buscador visual** con imágenes
de consulta que vives en **`proyectoA/Search-10/`** (las agregas/cambias tú a
mano). Todo el código nuevo vive aquí dentro: **no se modifica nada en `api/`**
de la raíz.

El flujo:

1. **Búsqueda y ranking REAL** — eliges una imagen de `Search-10/` y el sistema
   corre el motor RAG del proyecto (recuperación amplia CLIP + reranking
   visual) y devuelve el Top 5.
2. **Feedback (Correcto / Sirve / Incorrecto)** — cada tarjeta tiene los 3
   botones. Un clic guarda el juicio **al instante**.
3. **Persistencia del aprendizaje** — los resultados marcados **Incorrecto**
   quedan registrados y en futuras búsquedas con **esa misma imagen** no
   vuelven a aparecer: el Top K se rellena con las siguientes alternativas
   visuales válidas del pool (sin rellenar con basura; respeta el umbral
   dinámico del motor).

---

## Arquitectura

```text
proyectoA/
├── Search-10/                # Imágenes de consulta (agrega/cambia aquí)
├── backend/
│   └── main.py               # Servidor FastAPI propio (puerto 8400) — NO toca api/
├── .feedback/
│   └── feedback.json         # Entrenamiento persistente (creado solo)
├── frontend-next/
│   ├── app/search10/         # Search-10 como componente reutilizable
│   │   ├── Search10Entrenar.tsx
│   │   ├── page.tsx          # (ruta /search10, ya no enlazada)
│   │   └── search10.css
│   └── app/evaluacion/       # View unificada: pestañas Evaluador + Search-10
└── README.md                 # Este documento
```

El backend **importa** (no modifica) el motor RAG de la raíz:
`api.preprocesar_consulta`, `api.search_engine_hito2` y `api.main` (solo usa
sus helpers de embedding). Las rutas de datos de esos módulos son absolutas
relativas a sus propios archivos, así que apuntan a `data/` aunque el working
directory sea `proyectoA/`.

---

## 1 · Qué archivos se crearon/modificaron

Creados:
- `proyectoA/backend/main.py` — servidor FastAPI con:
  - `POST /search10/buscar` — ranking real sobre `Search-10/` con exclusiones aplicadas.
  - `POST /search10/feedback` — guarda el juicio `(imagen_consulta, id_resultado) → acierto|sirve|incorrecto`.
  - `GET /search10/feedback` — estado completo del entrenamiento.
  - `POST /search10/feedback/limpiar` — borra el feedback (de una consulta o de todo).
  - `GET /search10/imagenes` — lista las consultas de `Search-10/`.
  - `GET /search10/images/<archivo>` — sirve las imágenes de consulta (static).
- `proyectoA/frontend-next/app/search10/page.tsx` — la vista de entrenamiento.
- `proyectoA/frontend-next/app/search10/search10.css` — estilos (misma paleta del proyecto).
- `proyectoA/.gitignore` — ignora `.feedback/`, `node_modules/`, `.next/`.
- `proyectoA/README.md` — este documento.

Modificados (solo dentro de proyectoA):
- `proyectoA/frontend-next/app/layout.tsx` — barra de navegación superior con
  **🔍 Búsqueda** y **📋 Evaluador**.
- `proyectoA/frontend-next/app/evaluacion/page.tsx` — el **Evaluador** ahora
  integra **Search-10 · Entrenar** como pestaña (un solo lugar, todo visible
  desde `/` sin abrir `/search10`).

> **No se tocó `api/`**: el cambio previo en `api/evaluacion.py`
> (`CASOS_DIR → proyectoA/Search-10`) es del hito anterior de mover carpetas.

---

## 2 · Cómo correrlo

Necesitas los SERVICIOS (2 terminales; el backend Search-10 usa el venv de la
raíz):

```fish
# Terminal 1 — backend Search-10 (dedicado, puerto 8400)
cd /home/satanic/RAG-V2/proyectoA
../venv/bin/python -m uvicorn backend.main:app --port 8400
```

```fish
# Terminal 2 — frontend Next.js
cd /home/satanic/RAG-V2/proyectoA/frontend-next
npm run dev        # abre http://localhost:3000/evaluacion (pestaña Search-10 · Entrenar)
```

> El backend Search-10 es independiente del `uvicorn api.main:app --port 8000`
> (el motor RAG se importa directamente); la Búsqueda `/` y el Evaluador `/`
> siguen usando la API 8000 si la necesitas.

Health check del backend Search-10:

```bash
curl http://localhost:8400/search10/imagenes
```

---

## 3 · Probar el ciclo de entrenamiento (paso a paso)

1. Abre **http://localhost:3000/evaluacion** y selecciona la pestaña
   **🎯 Search-10 · Entrenar**. En el panel izquierdo verás las imágenes de
   `proyectoA/Search-10/`. (La ruta `/search10` también funciona pero ya no
   aparece en la barra de navegación).
2. Haz clic en una imagen de consulta → se ejecuta la búsqueda real y aparece
   el **Top 5** con su score.
3. Califica cada tarjeta:
   - **✅ Correcto** — el resultado es el mismo diseño.
   - **👍 Sirve** — no es el mismo, pero es aceptable.
   - **❌ Incorrecto** — es otro diseño → queda **excluido**.
4. Al marcar **Incorrecto**, el sistema **re-busca al instante** y ese
   resultado desaparece del Top 5; los siguientes candidatos válidos del pool
   toman su lugar.
5. Recarga la página o vuelve a esa consulta en otra sesión: los excluidos
   siguen sin aparecer (persistencia real en `proyectoA/.feedback/feedback.json`).
6. En el panel se muestra, por cada consulta, cuántos resultados tiene su
   feedback y cuántos quedaron excluidos.

Para probar el aprendizaje con datos nuevos: copia más imágenes a
`proyectoA/Search-10/`, recarga **http://localhost:3000/evaluacion** (pestaña
Search-10 · Entrenar, pulsa "↻ Actualizar feedback" si hiciera falta) y repite.

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

Manual: borra el archivo `proyectoA/.feedback/feedback.json` (o toda la
carpeta `.feedback/`). Al borrarlo, el sistema vuelve a permitir que todas las
alternativas aparezcan.

---

## 5 · Endpoints del backend Search-10

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/search10/buscar` | `{imagen, modelo?, top_k?}` → ranking real (exclusiones aplicadas) |
| `POST` | `/search10/feedback` | `{imagen, id_resultado, juicio}` → guarda `acierto/sirve/incorrecto` |
| `GET` | `/search10/feedback` | Estado completo `{consulta: {id: juicio}}` |
| `POST` | `/search10/feedback/limpiar` | `{imagen?}` → limpia una consulta o todo (si `imagen` es `null`) |
| `GET` | `/search10/imagenes` | Lista de consultas disponibles |
| `GET` | `/search10/images/<archivo>` | Imagen de consulta (static) |

El archivo de persistencia es `proyectoA/.feedback/feedback.json`.