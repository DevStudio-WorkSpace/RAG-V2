# RONDA 2 — INTERCAMBIO DE CASOS Y CIERRE DE BRECHAS

# INFORME-2 GRUPO B — SALA 3

1. Edwin Salvatierra
2. Jhon Portugal

Documento de referencia para la **Ronda 2 — Intercambio de casos y cierre
de brechas** de la **Ficha 04**, continuación del trabajo de Sala 3 sobre el
evaluador del buscador descrito en `INFORME_GRUPO_B_SALA-3_EDWIN SALVATIERRA
Y JHON PORTUGAL.md`. Este informe se limita a la actividad de intercambio
de casos realizada en esta ronda y no repite la descripción general del
proyecto, que ya consta en el informe anterior.

---

## 1. Objetivo

La Ficha 04 plantea, en su Ronda 2, que las parejas que usan el buscador
RAG-V2 intercambien un conjunto de casos para evaluar la herramienta con
imágenes que **no fueron seleccionadas por la propia pareja**. El objetivo
es comprobar si el comportamiento observado sobre el set propio se mantiene,
mejora o se deteriora cuando el buscador y la herramienta reciben un set
ajeno, y dejar evidencia numérica de esa comparación.

Para Sala 3 esto significa:

- Entregar a otra sala el set de 10 casos preparado por el propio equipo.
- Recibir un set de 10 casos preparado por otra sala.
- Aplicar la misma herramienta de evaluación de Sala 3 sobre el set ajeno.
- Comparar los tres números (Top 1, Top 5 y Utilidad) entre ambos sets.

---

## 2. Intercambio de casos

El intercambio se realizó entre las salas del grupo según lo previsto en la
Ficha 04:

- **Sala 3 → Sala 4:** Sala 3 entregó su **set propio** de 10 casos a Sala 4.
- **Sala 2 → Sala 3:** Sala 3 recibió el **set ajeno** de 10 casos preparado
  por Sala 2.
- **Total de casos del set ajeno recibidos por Sala 3:** 10.
- **Casos propios entregados a otra sala:** 10.

No se mezclaron sets: Sala 3 evaluó de forma independiente los 10 casos
propios (resultado ya documentado en el informe anterior) y los 10 casos
recibidos de Sala 2, conservando la evidencia de cada evaluación en
archivos separados por sala (ver detalle en §3 sobre la organización de
la evidencia).

---

## 3. Ejecución de la prueba

Herramienta utilizada: la **misma herramienta de evaluación de Sala 3**
descrita en el informe anterior (`app.py`, aplicación Streamlit en
`proyecto_GRUPOS_B/`), que se conecta por HTTP al buscador RAG-V2 mediante
`POST /search/image` y registra cada juicio como `acierto`, `sirve` o
`no_sirve`.

### 3.1 Procedimiento aplicado sobre el set recibido de Sala 2

1. Los 10 casos recibidos de Sala 2 se conservan como evidencia histórica
   en los archivos separados por sala: el CSV del set recibido está en
   `casos/casos_sala-2.csv` y sus fotos en `casos/fotos_sala-2/`,
   manteniendo el formato `caso_id, foto, tipo, id_correcto`.
2. La herramienta se ejecutó cargando dicho set y se recorrió cada uno
   de los 10 casos.
3. Para cada caso, la herramienta envió la foto al buscador RAG-V2 y
   recibió 5 resultados.
4. Por cada uno de los 5 resultados se emitió un juicio humano
   (`Acierto / Sirve / No sirve`).
5. Cada clic se persistió siguiendo el mismo esquema de la Ronda 1
   (un registro por `(caso_id, posicion)`). La traza completa de los
   50 juicios del set recibido se conserva en `data/juicios_sala-2.jsonl`.
6. Al finalizar, las métricas Top 1, Top 5 y Utilidad, tanto globales como
   por tipo de foto, se recalcularon a partir de ese JSONL.

**Total de juicios generados sobre el set recibido de Sala 2:**
50 (10 casos × 5 posiciones).

### 3.2 Organización de los archivos y de la evidencia

La evidencia de cada evaluación se conserva deliberadamente en archivos
separados por sala, para no mezclar el set propio y el set recibido y para
mantener trazabilidad independiente de cada evaluación. En el árbol del
proyecto conviven dos tipos de archivos:

- **Archivos históricos separados por sala**, donde queda la evidencia
  de cada evaluación concreta:

  | Sala | CSV de casos | Carpeta de fotos | Archivo de juicios |
  |---|---|---|---|
  | Set propio (Sala 3) | `casos/casos_sala-3.csv` | `casos/fotos_sala-3/` | `data/juicios_sala-3.jsonl` |
  | Set recibido de Sala 2 | `casos/casos_sala-2.csv` | `casos/fotos_sala-2/` | `data/juicios_sala-2.jsonl` |

  Los 50 juicios del set recibido de Sala 2 son los que se contabilizan
  en este informe de Ronda 2; los 50 juicios del set propio son los que
  se documentaron en el informe de Ronda 1.

- **Archivos de trabajo que consume `app.py`** cuando se necesita cargar
  un conjunto determinado para ejecutar la herramienta:

  | Recurso de trabajo | Ruta |
  |---|---|
  | CSV de casos | `casos/casos.csv` |
  | Carpeta de fotos | `casos/fotos/` |
  | Archivo de juicios | `data/juicios.jsonl` |

  Estos son los archivos que `app.py` lee y escribe de forma directa
  (constan en `CASOS_CSV` y `JUICIOS_JSONL` del propio código). En el
  estado actual del repositorio no contienen una evaluación activa: la
  evidencia histórica de cada sala vive en los archivos
  `_sala-2` y `_sala-3` descritos arriba, y se conservan así a propósito
  para no mezclar ambas rondas ni perder la trazabilidad de cada set.

Esta separación es intencional y se mantiene a lo largo de toda la
Ronda 2.

---

## 4. Resultados del set propio

Corresponden a la Ronda 1, ya documentados en el informe anterior. Se
reproducen aquí para que la comparación de la sección 7 sea legible sin
tener que abrir el otro documento.

| Ámbito | n | Top 1 | Top 5 | Utilidad |
|---|---|---|---|---|
| **Global (set propio)** | 10 | 90.0 % | 90.0 % | 1.90 / 5 |
| `con_marco` | 5 | 80.0 % | 80.0 % | 2.00 / 5 |
| `sin_marco` | 5 | 100.0 % | 100.0 % | 1.80 / 5 |

---

## 5. Resultados del set recibido de Sala 2

Métricas obtenidas tras ejecutar la herramienta de Sala 3 sobre los 10
casos recibidos, con los 50 juicios registrados.

| Ámbito | n | Top 1 | Top 5 | Utilidad |
|---|---|---|---|---|
| **Global (set recibido)** | 10 | 30.0 % (3/10) | 40.0 % (4/10) | 2.20 / 5 |

---

## 6. Métricas por tipo del set recibido

El set recibido de Sala 2 estaba etiquetado con los mismos tipos de foto
que utiliza Sala 3, leídos desde el CSV del set recibido
(`casos/casos_sala-2.csv`, archivo histórico separado por sala). La
distribución por tipo no fue simétrica: 6 casos `sin_marco` y 4 casos
`con_marco`.

| Tipo | n casos | Top 1 | Top 5 | Utilidad |
|---|---|---|---|---|
| `sin_marco` | 6 | 33.3 % | 33.3 % | 2.83 / 5 |
| `con_marco` | 4 | 25.0 % | 50.0 % | 1.25 / 5 |

Observación: en el set recibido, el subconjunto `con_marco` tuvo menos
casos evaluados pero un Top 5 relativamente más alto; el subconjunto
`sin_marco` concentró la mayor parte de los casos y la Utilidad más alta
del set ajeno.

---

## 7. Comparación de resultados

Comparación directa entre los tres números del set propio y los tres
números del set recibido de Sala 2:

| Métrica | Set propio | Set recibido (Sala 2) | Variación |
|---|---|---|---|
| Top 1 | 90.0 % | 30.0 % | **−60 puntos porcentuales** |
| Top 5 | 90.0 % | 40.0 % | **−50 puntos porcentuales** |
| Utilidad | 1.90 / 5 | 2.20 / 5 | **+0.30** |

Sentido del cambio al pasar del set propio al set ajeno:

- **Top 1:** bajó.
- **Top 5:** bajó.
- **Utilidad:** subió.

En términos relativos, la caída de Top 1 (−60 p.p.) y de Top 5 (−50 p.p.)
es claramente mayor que la subida de Utilidad (+0.30 sobre 5). Los dos
indicadores de acierto exacto disminuyeron; el indicador que combina
aciertos y resultados "Sirve" aumentó ligeramente.

---

## 8. Interpretación

Los datos de esta ronda muestran que el comportamiento del buscador y de la
herramienta de Sala 3 cambió de forma apreciable al pasar del set propio
al set recibido de Sala 2: **hubo menos aciertos exactos en las primeras
posiciones**, mientras que **la utilidad subió ligeramente** porque se
incrementó la cantidad de resultados marcados como "Sirve" entre los cinco
devueltos por el buscador.

Este informe no afirma una causa concreta que los datos no demuestren. En
particular, no se presenta como hecho demostrado que la diferencia se deba
a una causa específica del motor, del algoritmo, de las imágenes
consultadas o de la dificultad del set, porque los números disponibles no
permiten aislar una única causa. La subida de Utilidad junto con la caída
de Top 1 / Top 5 queda registrada como una **observación** que debe
contrastarse con lo que reporten las demás salas al evaluar sus
respectivos sets ajenos.

Lo que sí es consistente con los datos:

- Sobre el set recibido, en 3 de cada 10 casos el resultado en posición 1
  fue un acierto exacto (frente a 9 de cada 10 en el set propio).
- Sobre el set recibido, en 4 de cada 10 casos apareció al menos un
  acierto exacto entre las cinco posiciones (frente a 9 de cada 10 en el
  set propio).
- Sobre el set recibido, el promedio de resultados marcados como
  "Acierto" o "Sirve" por caso fue 2.20 de 5, ligeramente por encima del
  1.90 de 5 obtenido sobre el set propio.

El significado de la prueba, según lo planteado por la Ficha 04, es
comprobar cómo se comporta la herramienta y el buscador cuando los casos
no son los seleccionados por la propia pareja. Eso es exactamente lo que
mide esta ronda, y la diferencia entre ambos sets queda documentada arriba.

---

## 9. Conclusiones

- El intercambio de la Ronda 2 se completó: Sala 3 entregó su set propio a
  Sala 4 y recibió el set de Sala 2, sobre el cual ejecutó su propia
  herramienta de extremo a extremo.
- Los tres números del set recibido son **Top 1 = 30.0 %, Top 5 = 40.0 %,
  Utilidad = 2.20 / 5**, obtenidos a partir de 50 juicios
  (10 casos × 5 posiciones).
- Frente al set propio, **Top 1 bajó 60 p.p., Top 5 bajó 50 p.p. y la
  Utilidad subió 0.30**. El acierto exacto en las primeras posiciones
  disminuyó claramente; la Utilidad subió ligeramente por la mayor
  presencia de resultados marcados como "Sirve".
- Las métricas por tipo del set recibido (`sin_marco` 6 casos:
  33.3 / 33.3 / 2.83; `con_marco` 4 casos: 25.0 / 50.0 / 1.25) muestran
  que la diferencia no se distribuye de forma uniforme entre tipos, pero
  el tamaño de cada subconjunto es pequeño y no permite extraer
  conclusiones sólidas por separado.
- La diferencia entre ambos conjuntos es **una observación**, no una
  causa demostrada: este informe no atribuye la caída de Top 1 / Top 5 ni
  la subida de Utilidad a un factor concreto del motor, del algoritmo o
  de las imágenes, porque los datos disponibles no lo demuestran.
- La herramienta de Sala 3 funcionó sin cambios sobre el set ajeno: la
  evaluación del set recibido se registró completa en
  `data/juicios_sala-2.jsonl` y las métricas se recalcularon de forma
  consistente con la fórmula utilizada en la Ronda 1. La separación
  entre archivos históricos por sala (`*_sala-2.*`, `*_sala-3.*`) y
  archivos de trabajo que consume `app.py` (`casos/casos.csv`,
  `casos/fotos/`, `data/juicios.jsonl`) se mantuvo durante toda la
  ronda, según se describe en §3.2.