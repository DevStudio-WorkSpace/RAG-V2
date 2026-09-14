# INFORME_DIARIO.md

Informe diario del trabajo realizado para la Ficha 03-B (evaluador del buscador).

Las fechas se han reconstruido a partir de los `timestamp` presentes en
`data/juicios.jsonl` y de las marcas de modificación de los archivos del
proyecto. Cualquier fecha que no pueda derivarse de los archivos se omite.

## Jornada del 2026-09-13 / 2026-09-14

> Día único: la sesión de trabajo en `proyecto_GRUPOS_B` se concentró en este
> intervalo (los juicios almacenados van del `2026-09-13T23:08:25Z` al
> `2026-09-14T01:16:32Z`).

1. **Qué quedó funcionando hoy.**
   El evaluador de la Ficha 03-B levanta con `streamlit run app.py`, consulta
   RAG-V2 por HTTP, presenta los 5 resultados de cada caso, registra juicios
   `Acierto / Sirve / No sirve`, los persiste en `data/juicios.jsonl` y muestra
   las métricas Top 1, Top 5 y Utilidad en total y separadas por tipo de foto.
   Los 10 casos propios quedaron cargados en `casos/casos.csv` con sus fotos
   en `casos/fotos/01.jpg` … `10.jpg`, todos evaluados (50 juicios, 10 casos ×
   5 posiciones). Métricas finales: Top 1 = 90 %, Top 5 = 90 %, Utilidad =
   1.90/5.

2. **Qué no salió y por qué.**
   No se detectan bloqueos pendientes a la fecha del último timestamp del
   JSONL. Observaciones menores: (a) `__pycache__/` se generó automáticamente
   durante las pruebas y se eliminó en la limpieza final; (b) el archivo
   `GRUPOS_B.md` (manual original de la ficha) quedó dentro de la carpeta
   del proyecto por decisión explícita de no moverlo en esta tarea.

3. **Qué decisión tomaron y qué descartaron.**
   Se decidió: (a) mantener el evaluador separado del buscador y comunicarse
   con RAG-V2 únicamente por HTTP para no tocar el buscador, el índice, los
   embeddings ni `products.csv`; (b) persistir los juicios en JSONL (un
   registro por línea) por simplicidad y por la facilidad de recalcular las
   métricas a posteriori; (c) usar como tipos de foto `con_marco` y
   `sin_marco`, leídos dinámicamente desde `casos.csv`, porque la Ficha exige
   separar las métricas por tipo pero no fija nombres; (d) actualizar el
   juicio existente en lugar de duplicarlo cuando se vuelve a juzgar la
   misma `(caso_id, posicion)`. Se descartó: añadir clasificación automática
   de imágenes, hardcodear listas de tipos, modificar el buscador y modificar
   `products.csv`.

4. **Qué necesitan de otro para seguir mañana.**
   Nada bloqueante para la entrega. Pendiente menor: validar visualmente, el
   día de la aceptación, que las 10 fotos de `casos/fotos/` no procedan del
   catálogo ni de la web de Aimari (la verificación por hash realizada en
   desarrollo ya confirmó que ninguna coincide byte a byte con su homóloga
   del catálogo, pero el coordinador puede repetir la comprobación).
