# AI_LOG.md — Evaluador Ficha 03-B

## Resumen

Este archivo documenta el uso de la IA (OpenCode / modelo `vireonix/auto`) durante
la construcción y corrección del evaluador de la Ficha 03-B dentro de
`RAG-V2/proyecto_GRUPOS_B/`.

Los prompts que se transcriben abajo son los que se enviaron realmente durante
esta sesión. Cuando una parte de un prompt fue larga y se parafraseó aquí, se
indica explícitamente como "resumen" para no presentar como literal algo que no
lo es.

## Prompt 1 — Auditoría inicial del evaluador

Solicitud al modelo (resumen):

> "Necesito hacer una corrección MUY limitada al evaluador de Ficha 03-B.
> NO modifiques archivos fuera de `RAG-V2/proyecto_GRUPOS_B/`.
> NO modifiques el buscador RAG-V2, ni `api/`, `frontend/`, `data/products.csv`,
> embeddings, índices ni ningún otro componente de RAG-V2.
> Revisa `casos/casos.csv`. La columna `tipo` seguirá existiendo con el formato
> `caso_id,foto,tipo,id_correcto`. El programa debe obtener dinámicamente los
> tipos desde el CSV. NO debe imponer categorías fijas como `exacto`, `sin_marco`,
> `recoloreada`, `recortada`, `mockup`. Si un tipo aparece en el CSV sin casos
> evaluados, mostrarlo como `<tipo> (0 casos evaluados)`. No cambies las
> métricas globales ni el formato de `data/juicios.jsonl`. Si mañana cambiamos
> los tipos del CSV, el programa debe adaptarse sin tocar `app.py`. NO añadas
> funcionalidades nuevas. Antes de modificar nada, inspecciona el código."

Resultado de la inspección:

- `app.py` ya obtenía los tipos dinámicamente en `calcular_metricas_por_tipo`
  iterando sobre `casos`; no había ninguna lista hardcodeada en el código.
- No fue necesario modificar `app.py`. Esa fue la única "corrección" pedida en
  este paso y consistió en confirmar el comportamiento, no en cambiar código.

## Prompt 2 — Preparación de los 10 casos propios

Solicitud al modelo (resumen):

> "Quiero que prepares los 10 casos propios de prueba para el evaluador de la
> Ficha 03-B. Genera 10 fotografías y guárdalas en
> `proyecto_GRUPOS_B/casos/fotos/` con nombres `01.jpg` … `10.jpg`. Los tipos
> deben ser únicamente `con_marco` y `sin_marco` (5/5). Actualiza
> `casos/casos.csv` con esas dos categorías, manteniendo las columnas
> `caso_id,foto,tipo,id_correcto`. Cada `id_correcto` debe corresponder a un
> diseño real de `RAG-V2/data/products.csv`. NO modifiques `products.csv`,
> embeddings, índices ni el buscador. NO modifiques `app.py`."

Decisiones tomadas durante la ejecución:

- Los IDs del catálogo asignados fueron `AIM-P001-001` a `AIM-P001-010`,
  uno por caso, distribuidos 5 a `con_marco` (casos 01, 03, 05, 07, 09) y 5 a
  `sin_marco` (casos 02, 04, 06, 08, 10).
- Se generó un script Python auxiliar (`generar_casos.py`) que producía las
  imágenes con Pillow y luego se eliminó para no dejar archivos extra en el
  proyecto.
- Las 5 imágenes `con_marco` se construyeron pegando la camiseta sobre un fondo
  gris azulado con marco interior visible. Las 5 `sin_marco` se generaron
  sobre fondo blanco limpio.
- Se verificó por hash SHA1 que ninguna de las 10 imágenes coincide byte a
  byte con su correspondiente del catálogo (`data/images_normalized`).

## Prompt 3 — Comprobaciones sin modificación

Solicitud al modelo (resumen):

> "Quiero que hagas una comprobación completa del evaluador actual. NO
> modifiques ningún archivo. Comprueba: (1) que los tipos son dinámicos en
> `app.py`; (2) existencia, formato y campos de `data/juicios.jsonl`; (3) que
> las métricas globales y por tipo coinciden con la Ficha 03-B; (4) que la
> interfaz muestra métricas globales y por tipo; (5) que `api/`, `frontend/`,
> `data/products.csv`, embeddings e índices no fueron modificados."

Resultado:

- Tipos dinámicos: ✓ confirmado.
- `juicios.jsonl`: ✓ existe, formato JSONL con 15 filas y los campos
  `caso_id, tipo, posicion, id_resultado, juicio, score, timestamp`.
- Métricas: ✓ recálculo independiente coincidía con la fórmula de la app.
- Interfaz: ✓ bloques `### MÉTRICAS GLOBALES` y `### MÉTRICAS POR TIPO`
  presentes en `main()`.
- RAG-V2 sin cambios: ✓ `git status` sobre `api/`, `frontend/`,
  `data/products.csv` no mostraba diferencias.

## Prompt 4 — Auditoría final contra el manual de la Ficha 03-B

Solicitud al modelo (resumen):

> "AUDITORÍA FINAL del proyecto `RAG-V2/proyecto_GRUPOS_B` comparándolo con
> el manual de la Ficha 03-B. NO modifiques nada en esta primera revisión.
> Inspecciona README, AI_LOG, casos, evaluador, juicios.jsonl. Haz un
> recálculo independiente. Identifica archivos innecesarios. Verifica que no
> se haya modificado nada fuera de `proyecto_GRUPOS_B`."

Resultado (resumen de los hallazgos, no se aplicaron cambios en este paso):

- El programa cumplía los criterios funcionales 1–9 de la Ficha.
- El README mencionaba ejemplos antiguos con tipos `exacta / sin_marco /
  recoloreada / recortada / mockup` y nombres `foto_01.jpg` que no
  coincidían con el estado real.
- El AI_LOG tenía solo 2 prompts resumidos y truncados; no reflejaba los
  prompts reales de esta sesión.
- Existía `__pycache__/app.cpython-310.pyc` como artefacto de ejecución.
- El recálculo independiente de métricas coincidía exactamente con la app.
- RAG-V2 seguía intacto.

## Prompt 5 — Corrección final limitada

Solicitud al modelo (resumen):

> "Corrección FINAL y MUY LIMITADA. El evaluador FUNCIONA; no toques la
> lógica ni `app.py`. Solo deja la documentación coherente con el estado
> real y limpia el `__pycache__`. Cambios: (1) actualizar `README.md` para
> que use los tipos `con_marco` / `sin_marco`, nombres `01.jpg`…`10.jpg` y
> documente la decisión del equipo sobre los tipos; (2) ampliar `AI_LOG.md`
> con los prompts reales de esta sesión sin inventar; (3) eliminar
> `__pycache__/`. NO modifiques `app.py`, `casos/casos.csv`, las 10 fotos,
> `data/juicios.jsonl`, `requirements.txt` (salvo necesidad real), ni nada
> fuera de `proyecto_GRUPOS_B`. NO borres `GRUPOS_B.md`."

Este prompt es el que dio lugar a la versión actual del README, este AI_LOG y
la eliminación del `__pycache__`.

## Decisiones técnicas adoptadas durante el desarrollo

1. **JSONL para persistencia de juicios.** Permite lectura línea por línea y es
   fácil de verificar manualmente.
2. **Rutas calculadas con `pathlib` desde `app.py`** (`Path(__file__).parent`),
   para que Streamlit pueda ejecutarse desde cualquier directorio.
3. **Juicios como actualización, no append.** Si ya existe un juicio para
   `(caso_id, posicion)`, se reemplaza; así no se duplican filas en
   `juicios.jsonl`.
4. **Tipos leídos dinámicamente del CSV.** El evaluador no tiene una lista
   fija de tipos; muestra exactamente los que aparecen en `casos.csv`.
5. **Tipos `con_marco` y `sin_marco`** decididos por el equipo porque la Ficha
   obliga a separar métricas por tipo pero no impone nombres.

## Archivos creados o modificados durante el trabajo con IA

- `proyecto_GRUPOS_B/requirements.txt`
- `proyecto_GRUPOS_B/casos/casos.csv`
- `proyecto_GRUPOS_B/casos/fotos/01.jpg` … `10.jpg`
- `proyecto_GRUPOS_B/app.py`
- `proyecto_GRUPOS_B/README.md`
- `proyecto_GRUPOS_B/AI_LOG.md`
- `proyecto_GRUPOS_B/data/juicios.jsonl` (creado por la app al primer juicio)
- `__pycache__/app.cpython-310.pyc` (generado por Python, eliminado en la
  corrección final)
