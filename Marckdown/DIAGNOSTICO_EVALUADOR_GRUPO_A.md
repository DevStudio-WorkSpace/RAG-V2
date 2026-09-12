# INFORME DE DIAGNÓSTICO — Grupo A · "El evaluador del buscador"

Fase de inspección únicamente. **No se modificó ningún archivo del proyecto.**

---

## 1 · Resumen de requisitos del Grupo A (receta)

Fuente: `GRUPA A — El evaluador del buscador (formato Receta).md`

Herramienta en **`evaluador/`** que **consume** la API existente (no busca nada). Entrega: lunes, revisión en vivo. Pasos exigidos:

| # | Requisito | Detalle |
|---|---|---|
| 1 | Chequear `/health` | products == embeddings. Si no coinciden → avisar al coordinador y **no seguir** (índice roto). |
| 2 | Probar API a mano | Swagger `/docs`, Postman o `curl` con 1 foto de camiseta; ver el JSON real. |
| 3 | 10 casos de prueba | `casos/caso-001.jpg…` + `casos.csv` = `caso,id_correcto,tipo`. Fotos reales de internet, **nunca** del catálogo. |
| 4 | Pantalla | HTML+JS sueltos (sin Python): foto arriba, 5 resultados con imagen/nombre/score, 3 botones por resultado, botón «Siguiente», avance «caso X de 10». |
| 5 | Definir botones en pantalla | Acierto = mismo diseño (aunque cambie color/año/escudo/sponsor) · Sirve = se lo mostrarías al cliente · No sirve = otro diseño. |
| 6 | Guardar cada clic al instante | `resultados.csv` columnas exactas: `caso, id_correcto, posicion, id_resultado, score, juicio, quien, fecha`. No perder trabajo si el navegador se cierra. |
| 7 | Tres números | **Top 1** (% de casos con «Acierto» en posición 1), **Top 5** (% con «Acierto» en cualquiera), **Utilidad** (promedio 0–5 de «Acierto»+«Sirve» entre las 5 posiciones). |
| 8 | Por tipo de foto | Los 3 números también divididos por persona, producto, captura, difícil. |
| 9 | README corto | Cómo se levanta, cómo se cargan los casos, dónde queda el CSV, qué significan los 3 números. Debe levantar otra persona sin preguntar. |

Revisión del lunes: levantar solo con el README → cargar 10 casos → evaluar → **cerrar el navegador a mitad y reabrir (dato persistente)** → filas completas en CSV → 3 números total+por tipo → explicar el Top 5 individualmente.

Reglas duras: no tocar buscador/índice/`products.csv`; no usar imágenes del catálogo como casos; prompts de IA en `AI_LOG.md`; informe diario de 4 líneas.

---

## 2 · Módulos y código existente reutilizables

| Recurso | Archivo | Por qué se reutiliza |
|---|---|---|
| Endpoint de búsqueda | `api/main.py` — `POST /search/image` | Devuelve exactamente `id · nombre · imagen · url · proveedor · score`. CORS abierto a `*`. |
| Chequeo de salud | `api/main.py` — `GET /health` | Devuelve `status, products, embeddings, model, desfase_detectado, observacion`. **Verificado: 15272 productos = 15272 embeddings, IDs alineados.** |
| Swagger | FastAPI `/docs` | Listo para el paso 2 (probar la API a mano). |
| Cliente HTTP de ejemplo | `frontend/app.py` — `verificar_health()` y `buscar()` | Patrón a replicar en JS: multipart + FormData al endpoint, manejo de errores y timeout. |
| Score a mostrar | `frontend/app.py` — `obtener_score()` | Prioriza `score_reranking` y cae a `score`. |
| IDs → datos de producto | `scripts/get_product.py` + `data/products.csv` | `get_product_by_id("AIM-P001-001")` resuelve nombre/imagen/url. |
| Plantilla de casos | `evaluation/consultas_hito2.csv` | Columnas `consulta,categoria,ruta_imagen,id_correcto` → molde para `casos.csv`. |
| Set de consultas con id_correcto | `data/consultas_test_50.json` + `data/consultas/` (120 imgs) | Fuente de `id_correcto` válidos/verificados para poblar los 10 casos. |
| Persistencia CSV en clic | `frontend/app.py` — `guardar_evaluacion()` | Referencia del formato append-fila-por-clic. |
| Referencia de métricas | `scripts/reporte_metricas.py`, `scripts/evaluar_hito2.py`, `data/comparacion_hito1_hito2.csv` | Lógica Top 1 / Top 5 ya calibrada; adaptar al esquema Acierto/Sirve/No sirve. |

---

## 3 · Brechas y puntos fuertes del RAG actual

### Puntos fuertes (a favor del Grupo A)

- El contrato de la receta ya existe sin tocarlo: `POST /search/image` con CORS abierto y `/health` sano.
- El índice está sano: 15272 = 15272, `ids.npy` alineado con `products.csv`.
- Base sólida de datos: 15272 imágenes normalizadas, 120 consultas existentes, nomenclatura `AIM-P###-NNN`.
- El motor por defecto (`modo=auto`, `modelo=fusion`) es el mismo de producción → los resultados medidos serán los reales.

### Brechas (lo que falta / discrepancias)

1. **No existe `evaluador/`** ni nada del tool construido. Es todo de cero.
2. **Los «tipos» de la receta no existen en el proyecto.** La receta usa `persona, producto, captura, difícil`; el Hito 2 usa `exacta, sin_marco, recoloreada, recortada, mockup/persona`. Los 10 casos y el corte por tipo exigen la nomenclatura **de la receta**.
3. **Prohibido usar imágenes del catálogo** como casos. Las consultas existentes sirven para elegir `id_correcto`, pero **no** como `caso-XXX.jpg`: hay que descargar fotos reales de internet.
4. **Guardado instantáneo de CSV imposible con HTML/JS puro (`file://`).** Un navegador no puede escribir `resultados.csv` en disco. El criterio de la revisión de «cerrar el navegador a mitad y seguir» exige persistencia real. → Requiere un **micro-servidor dentro de `evaluador/`** (p. ej. `http.server` con un endpoint `/guardar` y servir las imágenes) y `localStorage` para el progreso. Esto **no toca la API**.
5. **La API no sirve imágenes estáticas.** Los resultados traen `imagen` (nombre de archivo) y `url` remota. Para mostrar las 5 imágenes hace falta servir `data/images_normalized/` (con el mismo micro-servidor) o usar la URL remota.
6. **El Top 5 puede traer menos de 5 resultados** (umbral dinámico). El evaluador debe tolerar 0–5 filas.
7. **Las métricas de la receta no existen.** Top 1 / Top 5 / Utilidad con juicios Acierto-Sirve-No sirve y corte por `tipo` no está implementado; hay que crear `evaluador/calcular.py` (o pantalla final).
8. **El README de la receta es obligatorio y probado en vivo** — la entrega no debe depender de la pareja: debe levantar quien quiera.

---

## 4 · Plan de acción recomendado (checklist, sin tocar buscador ni código aún)

**Fase 0 — Verificar el terreno**
- [ ] Levantar la API: `uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload`.
- [ ] `GET /health` → anotar products y embeddings (**deben ser 15272 = 15272**). Si desfase → avisar al coordinador y detenerse.
- [ ] `POST /search/image` una vez con `curl`/Swagger usando 1 foto real → observar el JSON exacto y confirmar si `modo=auto` puede devolver <5 resultados.

**Fase 1 — Estructura del entregable**
- [ ] Crear `evaluador/` con: `index.html`, `style.css`, `main.js`, `casos/`, `casos.csv`, `resultados.csv` (solo header exacto), `README.md` y **`server.py`** (http.server mínimo: sirve `index.html`, las imágenes de `data/images_normalized/`, y un POST `/guardar` que hace append a `resultados.csv`).
- [ ] `casos.csv`: columnas `caso,id_correcto,tipo` con `tipo ∈ {persona, producto, captura, difícil}`.

**Fase 2 — Datos (la pareja)**
- [ ] Elegir 10 diseños de equipos conocidos en `data/images_normalized/` (o usar `data/consultas_test_50.json` para `id_correcto` verificados) y descargar una foto real de internet por cada uno — **nunca** la imagen del catálogo.
- [ ] Guardar como `casos/caso-001.jpg`…`caso-010.jpg` y completar `casos.csv`. Distribución de tipos: ~3 producto, ~3 persona, ~2 captura, ~2 difícil.

**Fase 3 — Pantalla**
- [ ] `index.html`/`main.js`: chequear `/health` al cargar; por caso `fetch` a `/search/image` (FormData, `modo=auto`); render foto arriba + resultados (imagen, nombre, score) + 3 botones por resultado (definiciones escritas en pantalla) + «Siguiente» + «caso X de 10».
- [ ] Guardar al instante por clic: `POST /guardar` con `caso, id_correcto, posicion, id_resultado, score, juicio, quien, fecha`. `quien` ingresado una vez al inicio. Progreso en `localStorage`.

**Fase 4 — Métricas**
- [ ] `evaluador/calcular.py`: leer `resultados.csv` → Top 1, Top 5, Utilidad, **totales y por `tipo`**.

**Fase 5 — Documentación y verificación final**
- [ ] `README.md` corto (4 cosas: levantar, cargar casos, dónde queda el CSV, qué significan los 3 números).
- [ ] Ensayo de la revisión: levantar solo con el README → cargar 10 casos → evaluar → **cerrar el navegador a mitad y reabrir** (progreso intacto) → filas completas → 3 números total+por tipo.
- [ ] Ambos integrantes practican la explicación «cómo se calcula el Top 5».
- [ ] Registrar prompts en `AI_LOG.md` e informe diario de 4 líneas.

---

**Riesgo clave a decidir:** el micro-servidor `server.py` es la única forma de cumplir «guardar CSV al instante + sobrevivir al cierre del navegador» sin tocar la API. Alternativa de solo `localStorage` + exportar CSV a mano **no cumple** el criterio 3 de la revisión ni el paso 6 de la receta.