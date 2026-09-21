# INFORME_DIARIO.md

## Día 1 — Construcción y preparación

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

## Día 2 — Intercambio de casos y cierre de brechas

> Jornada de la Ronda 2 de la Ficha 04: Sala 3 entregó su set propio de 10
> casos a Sala 4 y recibió el set de 10 casos de Sala 2. Sobre el set ajeno
> se ejecutó la misma herramienta de evaluación de Sala 3, generando 50
> juicios (10 casos × 5 posiciones).

### Resultados de la jornada

Evaluación del set recibido de Sala 2 (10 casos, 50 juicios):

- **Top 1:** 30.0 % (3/10).
- **Top 5:** 40.0 % (4/10).
- **Utilidad:** 2.20 / 5.

Métricas por tipo dentro del set recibido:

- `sin_marco`: 6 casos — Top 1 = 33.3 %, Top 5 = 33.3 %, Utilidad = 2.83/5.
- `con_marco`: 4 casos — Top 1 = 25.0 %, Top 5 = 50.0 %, Utilidad = 1.25/5.

### Comparación con el set propio

- Top 1: bajó de 90.0 % a 30.0 % (−60 puntos porcentuales).
- Top 5: bajó de 90.0 % a 40.0 % (−50 puntos porcentuales).
- Utilidad: subió de 1.90/5 a 2.20/5 (+0.30).

1. **Qué quedó funcionando hoy.**
   La herramienta de evaluación de Sala 3 se ejecutó sobre los 10 casos
   recibidos de Sala 2 y registró los 50 juicios completos en
   `data/juicios.jsonl`. El cálculo de Top 1, Top 5 y Utilidad, tanto global
   como separado por tipo (`con_marco` / `sin_marco`), funciona sobre el set
   ajeno sin necesidad de cambios en el código. La comunicación entre salas
   quedó documentada: Sala 3 entregó su set propio a Sala 4 y recibió el set
   de Sala 2.

2. **Qué no salió y por qué.**
   No se completaron las 4 líneas de la Ficha 04 con un diagnóstico causal
   cerrado: el set recibido produjo menos aciertos exactos en las primeras
   cinco posiciones, mientras que la utilidad aumentó ligeramente respecto al
   set propio. Los datos no permiten afirmar una causa única y definitiva
   para esa combinación de bajada de Top 1 / Top 5 y subida de Utilidad; queda
   registrada como observación a contrastar con las demás salas, no como
   conclusión.

3. **Qué número cambió al usar el set ajeno.**
   Top 1 pasó de 90.0 % a 30.0 % (−60 p.p.) y Top 5 pasó de 90.0 % a 40.0 %
   (−50 p.p.). En sentido contrario, la Utilidad subió de 1.90/5 a 2.20/5
   (+0.30). Por tipo, sobre el set recibido: `sin_marco` 33.3 / 33.3 / 2.83 y
   `con_marco` 25.0 / 50.0 / 1.25.

4. **Qué necesitan de otro para seguir mañana.**
   Que el coordinador de la Ficha 04 confirme si la subida de Utilidad junto
   con la caída de Top 1 / Top 5 se considera esperada (más resultados
   marcados como «Sirve» aunque baje el acierto exacto) o si requiere abrir
   una acción correctiva. Además, que las demás salas (Sala 4 ya tiene el
   set propio de Sala 3) compartan sus métricas sobre el set ajeno para
   poder triangular el comportamiento del buscador antes de la entrega.
