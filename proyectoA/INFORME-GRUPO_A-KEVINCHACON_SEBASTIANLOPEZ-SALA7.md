# GRUPO A · Sala 7 — Ficha Técnica del Evaluador del Buscador Visual RAG

**Proyecto:** Plataforma de búsqueda visual de camisetas deportivas (CLIP / OpenCLIP / SigLIP)
**Módulo:** Evaluador del buscador + Search-10 de entrenamiento con retroalimentación
**Repositorio raíz:** `/home/satanic/RAG-V2`
**Raíz de trabajo:** `/home/satanic/RAG-V2/proyectoA`

---

## Integrantes

| Nombre | Rol |
|---|---|
| **Sebastian Lopes** | Armo los 10 casos de prueba de Search-10, migró el frontend completo a Next.js dentro de `proyectoA/frontend-next/`, diseño de la paleta visual y logo |
| **Kevin Chacon** | Implementó el módulo Evaluador, agregó Search-10 · Entrenar, configuró el modelo Fusión como motor por defecto (84% Top1 / 90% Top5), evaluaciones y todo el backend dedicado |

---

## Qué hicimos

Construimos el módulo completo **Evaluador del Buscador Visual** dentro de
`proyectoA/`. El sistema permite a una persona calificar los 5 resultados que
devuelve el buscador RAG para cada imagen de consulta, y acumula feedback que
mejora las búsquedas futuras. Concretamente:

1. **Frontend Next.js completo** (`proyectoA/frontend-next/`) con:
   - `/` — búsqueda visual por imagen con veredictos (Acierto / Sirve / No sirve).
   - `/evaluacion` — Evaluador + Search-10 en pestañas unificadas.
   - Selector de modelo de búsqueda (Fusión por defecto).
   - Tema claro / oscuro con logo y paleta roja (`#e01010`).

2. **Backend Search-10 dedicado** (`proyectoA/backend/main.py`, puerto 8400)
   que importa (no modifica) el motor RAG de la raíz. Exponne endpoints de
   búsqueda, feedback y persistencia en `Search-10/`.

3. **Motor Fusión como modelo por defecto** — combinación CLIP + OpenCLIP +
   SigLIP, el que mejores estadísticas tiene de la API:
   - CLIP solo: 60% Top 1 / 64% Top 5
   - **Fusión: 84% Top 1 / 90% Top 5** (ganador)

4. **Evaluador con persistencia real** — cada juicio se guarda en tiempo real
   y sobrevive al cierre del navegador (`resultados.csv` en `Search-10/`).

---

## Prompt más significativo utilizado

**PROMPT_ORIGEN_CONSTRUCCION_EVALUADOR_RAG**
(Referencia: `Marckdown/GRUPA A — El evaluador del buscador (formato Receta).md`)

Este es el prompt de la ficha 03-A que definió todo el trabajo. Contiene los
9 pasos exactos que se tuvieron que implementar:

> 1. Levantar la API y comprobar que responde (GET /health)
> 2. Probar la API a mano con una imagen real
> 3. Armar 10 casos de prueba (fotos reales de internet, nunca del catálogo)
> 4. Construir la pantalla: foto arriba, 5 resultados abajo, 3 botones por resultado
> 5. Definir bien los 3 botones: Acierto / Sirve / No sirve
> 6. Guardar cada clic al instante en un CSV (sobrevive al cierre del navegador)
> 7. Calcular Top 1, Top 5 y Utilidad
> 8. Dividir los 3 números por tipo de foto (persona, producto, captura, difícil)
> 9. Escribir un README que permita levantar la herramienta sin preguntar nada

El criterio de revisión del coordinador era: cerrar el navegador a la mitad
y volver a abrir — lo evaluado tiene que seguir estando. Este requisito obligó
a implementar un backend dedicado (no solo localStorage).

---

## Arquitectura del módulo

```text
proyectoA/
├── Search-10/                    # Imágenes de consulta (10 casos) + CSV
├── backend/
│   └── main.py                   # FastAPI Search-10 (puerto 8400)
├── .feedback/
│   └── feedback.json             # Persistencia del entrenamiento
├── frontend-next/
│   ├── app/
│   │   ├── layout.tsx            # Nav, logo, ThemeToggle
│   │   ├── page.tsx              # Búsqueda visual (/)
│   │   ├── components/
│   │   │   ├── ModelSelect.tsx   # Selector de modelo (Fusión por defecto)
│   │   │   └── ThemeToggle.tsx   # Toggle tema claro/oscuro
│   │   ├── evaluacion/           # Evaluador + Search-10 (/evaluacion)
│   │   │   ├── page.tsx
│   │   │   └── evaluacion.css
│   │   ├── search10/
│   │   │   ├── Search10Entrenar.tsx
│   │   │   └── search10.css
│   │   └── globals.css           # Paleta roja, tema claro/oscuro
│   └── package.json              # Next.js 16.3.5, React 19, TS 5
└── GRUPO_A_SALA_7_FICHA_TECNICA_EVALUADOR_BUSCADOR_VISUAL.md
```

---

## Cómo correrlo (3 terminales)

```fish
# Terminal 1 — API principal (motor RAG, puerto 8000)
cd /home/satanic/RAG-V2
./venv/bin/python -m uvicorn api.main:app --port 8000
```

```fish
# Terminal 2 — backend Search-10 (puerto 8400)
cd /home/satanic/RAG-V2/proyectoA
../venv/bin/python -m uvicorn backend.main:app --port 8400
```

```fish
# Terminal 3 — frontend Next.js
cd /home/satanic/RAG-V2/proyectoA/frontend-next
npm run dev        # → http://localhost:3000
```

| Ruta | Qué es |
|---|---|
| `/` | Búsqueda visual + calificación (usa API 8000) |
| `/evaluacion` | Evaluador + Search-10 en pestañas (usa API 8000 + 8400) |
| `/search10` | Search-10 como vista suelta (usa API 8400) |

---

## Endpoints

### API principal — `http://localhost:8000`

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/search/image` | `{file, modo, modelo}` → Top 5 de resultados |
| `GET` | `/evaluacion/veredictos` | Veredictos guardados |
| `POST` | `/evaluacion/guardar` | Guarda un juicio |
| `POST` | `/evaluacion/completar` | Marca un caso como evaluado |
| `GET` | `/evaluacion/estado` | Estado de la evaluación |

### Backend Search-10 — `http://localhost:8400`

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/search10/buscar` | Ranking real (exclusiones aplicadas) |
| `POST` | `/search10/feedback` | Guarda juicio de retroalimentación |
| `GET` | `/search10/feedback` | Estado completo del entrenamiento |
| `POST` | `/search10/feedback/limpiar` | Limpia feedback (una consulta o todo) |
| `GET` | `/search10/imagenes` | Lista de consultas disponibles |
| `GET` | `/search10/images/<archivo>` | Imagen de consulta (static) |

---

## Estadísticas del motor (evidencia de la fusión)

| Motor | Top 1 | Top 5 | Puntaje combinado |
|---|---|---|---|
| CLIP (Hito 1) | 60% | 64% | 62.0 |
| CLIP (Hito 2) | 60% | 66% | 63.0 |
| **Fusión (CLIP+OpenCLIP+SigLIP)** | **84%** | **90%** | **87.0** |

Fuente: `data/comparacion_hito1_hito2.json` (50 consultas de prueba)
