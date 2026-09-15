# REPORTE: Estado del Proyecto RAG Visual — Ficha 03-B (Evaluador del buscador)

**Fecha de auditoría:** 15/09/2026 — verificado mediante inspección directa del código fuente en `RAG-V2-sala-4` (lectura de archivos + conteo de directorios), no por revisión visual de la interfaz.

Este documento contrasta el **estado REAL del repositorio** contra los criterios de aceptación de la **Ficha 03-B: El evaluador del buscador** (entrega lunes, revisión en vivo).

---

## 📊 Resumen general

La Ficha 03-B está **INCOMPLETA**. Existe una maqueta visual (HTML/CSS/JS) bien encaminada y evidencia real de que el buscador fue consultado 261 veces, pero **el evaluador no guarda ningún juicio todavía**: los clics de Acierto/Sirve/No sirve solo cambian el DOM en memoria y se pierden al cerrar la pestaña. No hay ningún archivo en disco con juicios reales, y las métricas (Top 1 / Top 5 / Utilidad) están maquetadas visualmente pero no se calculan.

**Verificación técnica actual (real):**

| Ítem | Valor |
|---|---|
| Frontend vigente | `index.html` + `app.js` (vanilla JS). `evaluador.py` y `app.py` son prototipos Streamlit previos, no conectados al flujo actual |
| `evaluation/casos_prueba.csv` | 10 filas, columnas `consulta, tipo` (club/selección) — **sin columnas top1-top5 reales** |
| `evaluation/test_images_GRUPO4/` | 10 fotos reales (Barcelona, Real Madrid, Universitario, Alianza Lima, Sporting Cristal, Perú, Brasil, Argentina, Manchester City, AC Milan) — **confirmado: ninguna existe en el catálogo de 15.272 productos** (`data/products.csv`) |
| `evaluation/evaluacion.csv` | 4 líneas (encabezado + 3 dummy) con código placeholder `AIM-XXXXX` — **sin evaluaciones reales** |
| `data/queries_original/` y `data/queries_procesadas/` | **261 archivos cada una, coinciden 1 a 1** — evidencia de que el buscador SÍ fue consultado de verdad, entre el 11/08/2026 13:41 y el 13/09/2026 18:34 |
| Persistencia de juicios | **No existe.** Los clics solo modifican `dataset.juicio` en el DOM (memoria del navegador) |
| `AI_LOG.md` | Presente en la raíz, 371 líneas, historial de prompts desde el 07/08/2026 |

---

## ✅ Estado contra la prueba de aceptación (Ficha 03-B, sección 02)

| # | Criterio | Estado | Evidencia |
|---|---|:---:|---|
| 1 | Se levanta leyendo solo el README | ⏳ No verificado | No se auditó el README de este componente específico |
| 2 | 10 casos propios cargados y listos | ❌ NO | `app.js` requiere subir cada archivo a mano vía `<input type="file">`; ningún script lee `casos_prueba.csv` para precargar los 10 casos |
| 3 | Ninguna foto sale del catálogo ni de Aimari | ✅ SÍ | Las 10 fotos de `test_images_GRUPO4/` no coinciden con ningún producto de `data/products.csv` (15.272 filas) |
| 4 | Se evalúa solo con mouse, sin consola | ⚠️ PARCIAL | La API hay que levantarla por consola (`uvicorn`); una vez arriba, la carga de imagen y los clics de juicio sí son con mouse |
| 5 | Sobrevive cerrar/reabrir el navegador | ❌ NO | `evaluarResultado()` en `app.js` solo escribe en el DOM; no hay `localStorage`, backend, ni archivo — se pierde todo al recargar |
| 6 | Archivo en disco con una fila por juicio | ❌ NO | No existe ningún endpoint ni script que capture los clics y los guarde. `evaluacion.csv` sigue con 3 filas dummy sin tocar |
| 7 | Top 1 / Top 5 / Utilidad, por tipo de foto | ⚠️ PARCIAL | `index.html` tiene los contenedores (`#top1`, `#top5`, `#utilidad`, `#clubes-metricas`, `#selecciones-metricas`) pero `app.js` nunca los actualiza — quedan en `"-"` |
| 8 | Recalculable desde el archivo guardado | ⚠️ PARCIAL | Existe `scripts/reporte_evaluacion.py`, pero espera columnas `rank`/`correcto` que no coinciden con las columnas reales de `evaluacion.csv` (`posicion`/`juicio`) |
| 9 | Cada integrante explica cómo se calcula el Top 5 | ⏳ No verificable por código | Depende de cada persona, no del repositorio |
| 10 | Existe `AI_LOG.md` con los prompts | ✅ SÍ | 371 líneas, en la raíz del proyecto |

**Resultado: 2 de 8 puntos verificables por código están cumplidos (3 y 10). El resto está NO o PARCIAL.**

---

## 🔧 Lo que falta para pasar la prueba del lunes (en orden de bloqueo)

1. **Persistencia real de juicios** (bloquea los puntos 5, 6 y 8): `evaluarResultado()` en `app.js` necesita mandar cada clic a un backend que lo guarde — hoy no hay ningún endpoint que reciba esto.
2. **Precarga automática de los 10 casos** (punto 2): leer `casos_prueba.csv` y recorrer los casos sin que el usuario tenga que subir cada foto a mano.
3. **Cálculo real de métricas** (punto 7): conectar `#top1`, `#top5`, `#utilidad` a un cálculo real sobre los juicios guardados, con desglose por `tipo` (club/selección).
4. **Alinear `scripts/reporte_evaluacion.py`** con el esquema real de `evaluacion.csv` (punto 8): hoy usa columnas (`rank`, `correcto`) que no existen en el archivo real (`posicion`, `juicio`).
5. Confirmar que el `README.md` de este componente permite levantarlo sin preguntar nada (punto 1, no verificado en esta pasada).

---

## 📋 Informe diario (Ficha 03-B, sección 05)

1. **Qué quedó funcionando hoy:** interfaz visual completa (carga de imagen, consulta al buscador real vía `POST /search/image`, despliegue de 5 resultados con botones de juicio); confirmado que el motor fue consultado 261 veces reales.
2. **Qué no salió y por qué:** los juicios no se guardan en disco — `evaluarResultado()` solo actualiza el DOM; falta el backend/endpoint que reciba y persista cada clic.
3. **Qué decisión tomaron y qué descartaron:** se descartaron los prototipos en Streamlit (`evaluador.py`, `app.py`) en favor de un frontend HTML/JS vanilla conectado directo a la API.
4. **Qué necesitan de otro para seguir mañana:** definir dónde y cómo persistir los juicios (¿SQLite, CSV con append, otra API?) y quién arma el endpoint que los reciba desde `app.js`.

---

> Auditoría realizada por inspección directa de código (no por prueba visual de la interfaz corriendo). Los puntos marcados "no verificado" requieren revisión adicional en vivo.
