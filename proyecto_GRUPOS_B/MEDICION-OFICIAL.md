# Plantilla de entrega — Frente A

*Sublitex · Ficha 05-A · Se copia, se llena y se devuelve. No se cambia la estructura.*

**Nombre del archivo:** `MEDICION-OFICIAL.md`

Se entrega junto con el archivo de juicios en crudo y la planilla del set oficial.

**Tres reglas de llenado:** solo números, sin adjetivos; si algo no se calculó se escribe **pendiente**; la sección 8 no puede quedar vacía.

---

# Integrantes:

- Jhon Portugal
- Edwin Salvatierra
- Samir Ochoa
- Andres Quispe

---

# 1 · Identificación

| Quién preparó el set | Grupo B — Jhon Portugal, Edwin Salvatierra, Samir Ochoa y Andres Quispe. Consolidaron en `casos/casos-completo.csv` lo entregado por 6 salas: 1, 2, 3, 5, 6 y 7. Sala 4 no entregó casos. |
| --- | --- |
| Quién auditó el set | Samir Ochoa y Andres Quispe |
| Quiénes juzgaron | Edwin Salvatierra y Samir Ochoa |
| Fecha de la medición | 2026-09-29 |
| Cómo se levanta la herramienta (una línea) | Con la API del buscador ya arriba (`python -m uvicorn api.main:app --port 8000`), `streamlit run app.py` dentro de `proyecto_GRUPOS_B/`. |

**Detalle de apoyo.** Los 15 casos fueron elegidos por 5 personas distintas, y la columna `quien_eligio` de `casos/casos.csv` lo deja registrado: Sebastian Lopez 5, Esteban Moreno 4, Kevin Chacon 4, Luis Bazan 1, Luciano Acuña 1. Ninguno eligio de las 7 salas: Sala 7 aporta dos de los cinco (Sebastian Lopez y Kevin Chacon), y Salas 2, 5 y 6 aportan uno cada una. Salas 1, 3 y 4 no aportan ningun caso. La fecha es la de los dos bloques de juicio de `RESULTADO_JUECES.md`, con marcas de tiempo entre 03:57:35Z y 13:58:36Z del 2026-09-29: el bloque de Edwin va de 03:57:35Z a 04:13:19Z y el de Samir de 13:48:04Z a 13:58:36Z.

---

# 2 · Cómo quedó el set oficial

|  | Cantidad |
| --- | ---: |
| Casos recibidos de las 7 salas | 63 |
| Descartados: la foto salía del catálogo (o recorte / recoloreada de ella) | 0 |
| Descartados: el id_correcto no existe en products.csv | 0 |
| Descartados: foto repetida entre dos salas | 0 |
| Descartados: mirando las dos imágenes, no son la misma camiseta | 0 |
| **Casos que entraron a la medición** | **15** |

**Una línea:** ¿de qué sala vinieron la mayoría de los descartes y por qué motivo? No aplica: no hubo descartes. Las cuatro causas de descarte dan 0. Los 48 casos que no entraron no se rechazaron por ninguna de esas cuatro razones, sino porque la ficha pide 15 casos para juzgar y solo hacía falta esa cantidad.

**Cómo se llegó de 63 a 15.** Las 6 salas entregaron 63 casos. Ninguno se descartó: se descartaron 0 por foto de catálogo, 0 por `id_correcto` inexistente, 0 por foto repetida y 0 por no ser la misma camiseta. Como la ficha 05-A pide 15 casos para juzgar, se tomaron 15 de los 63 y los otros 48 quedaron fuera por cantidad, no por defecto. La cuenta cuadra: 63 recibidos − 0 descartados = 15 medidos + 48 no usados.

**De dónde salieron los 15, y los 48 que no se usaron:**

| Sala | Casos recibidos | Casos usados | Casos no usados |
| --- | ---: | ---: | ---: |
| Sala 1 | 10 | 0 | 10 |
| Sala 2 | 10 | 1 | 9 |
| Sala 3 | 10 | 0 | 10 |
| Sala 4 | 0 | 0 | 0 |
| Sala 5 | 10 | 1 | 9 |
| Sala 6 | 13 | 4 | 9 |
| Sala 7 | 10 | 9 | 1 |
| **Total** | **63** | **15** | **48** |

**Comprobaciones automáticas sobre los 63 recibidos.** Ninguna da descartes:

- `id_correcto` inexistente en `data/products.csv` (15 272 ids): **0 de 63**.
- Foto repetida entre dos salas: **0**. Los 63 archivos de `casos/fotos-completo/` tienen 63 `sha256` distintos, uno por archivo.

Las otras dos causas de descarte —foto de catálogo y no ser la misma camiseta— se resuelven mirando las imágenes, y no hay ningún archivo que registre esa revisión caso por caso. Queda anotado en la sección 8.

---

# 3 · Cómo quedó repartido por tipo

| Tipo | Casos |
| --- | ---: |
| persona | 4 |
| producto | 4 |
| captura | 4 |
| dificil | 3 |

**Si algún tipo quedó con menos de 8 casos, anotarlo acá:** los cuatro tipos están por debajo de 8, así que ese número no es confiable todavía. `dificil` quedó con 3, y `persona`, `producto` y `captura` con 4 cada uno.

**Los 15 casos del set oficial, uno por uno:**

| Caso | Tipo | Sala | quien_eligio | id_correcto |
| --- | --- | --- | --- | --- |
| sala2_caso-001.jpg | producto | Sala 2 | Luis Bazan | AIM-P001-007 |
| sala5_c_01 | persona | Sala 5 | Luciano Acuña | AIM-P001-021 |
| sala6_caso-001 | persona | Sala 6 | Esteban Moreno | AIM-P208-034 |
| sala6_caso-005 | captura | Sala 6 | Esteban Moreno | AIM-P163-056 |
| sala6_caso-007 | producto | Sala 6 | Esteban Moreno | AIM-P111-040 |
| sala6_caso-011 | captura | Sala 6 | Esteban Moreno | AIM-P048-037 |
| sala7_caso_01 | persona | Sala 7 | Kevin Chacon | AIM-P001-001 |
| sala7_caso_02 | persona | Sala 7 | Sebastian Lopez | AIM-P001-002 |
| sala7_caso_03 | producto | Sala 7 | Kevin Chacon | AIM-P001-003 |
| sala7_caso_04 | producto | Sala 7 | Sebastian Lopez | AIM-P001-004 |
| sala7_caso_05 | captura | Sala 7 | Kevin Chacon | AIM-P001-005 |
| sala7_caso_06 | captura | Sala 7 | Sebastian Lopez | AIM-P001-006 |
| sala7_caso_08 | dificil | Sala 7 | Sebastian Lopez | AIM-P001-008 |
| sala7_caso_09 | dificil | Sala 7 | Kevin Chacon | AIM-P001-009 |
| sala7_caso_10 | dificil | Sala 7 | Sebastian Lopez | AIM-P001-010 |

El tipo lo puso cada sala al armar su caso. No hay una definición escrita de los cuatro criterios, así que las etiquetas se tomaron tal cual, sin revisión. Queda anotado en la sección 8.

---

# 4 · El número

| Número | Resultado |
| --- | ---: |
| Casos medidos (n) | 15 |
| Top 1 (%) | 46,7 % (7/15) |
| Top 5 (%) | 53,3 % (8/15) |
| Utilidad (de 0 a 5) | 2,60 |

**Cómo se llegó.** Los dos jueces juiciaron los mismos 15 casos, cada uno por su lado, y sus juicios se combinan en un resultado único por posición. Hay dos reglas posibles y la ficha 03-B no fija cuál usar, así que se midieron las dos:

| Regla de combinación | n | Top 1 | Top 5 | Utilidad |
| --- | ---: | ---: | ---: | ---: |
| **Máxima — la que se reporta arriba** | 15 | **46,7 % (7/15)** | **53,3 % (8/15)** | **2,60** |
| Estricta, la que dice la ficha 03-B | 15 | 40,0 % (6/15) | 46,7 % (7/15) | 2,53 |
| Diferencia entre las dos | — | 6,7 puntos | 6,7 puntos | 0,07 |

- **Regla máxima:** la posición vale `acierto` si cualquiera de los dos jueces marcó `acierto`; si ninguno, `sirve` si alguno marcó `sirve`; si no, `no_sirve`.
- **Regla estricta:** la posición vale `acierto` solo si **los dos** jueces marcaron `acierto`.

Se reporta la máxima porque es la que no descarta el acierto que uno de los dos jueces sí vio. La estricta se deja escrita porque la diferencia es de 6,7 puntos en las dos métricas, y porque la regla de combinación no está fijada en ninguna ficha: elegir una u otra es decisión del equipo, no una consecuencia de los datos.

**Cada juez por separado:**

| Juez | n | Top 1 | Top 5 | Utilidad |
| --- | ---: | ---: | ---: | ---: |
| Edwin Salvatierra | 15 | 46,7 % (7/15) | 53,3 % (8/15) | 2,40 |
| Samir Ochoa | 15 | 40,0 % (6/15) | 46,7 % (7/15) | 2,40 |
| Diferencia entre los jueces | — | 6,7 puntos | 6,7 puntos | 0,00 |

Edwin va 1 caso por delante en Top 1 y en Top 5. La utilidad le da igual a los dos. Y conviene decirlo sin rodeos: **el 46,7 % y el 53,3 % de la tabla de arriba son exactamente las cifras de Edwin solo**. Bajo la regla máxima el consolidado coincide con el juez que mejor quedó, y bajo la estricta coincide con el que peor quedó: el 40,0 % y el 46,7 % son los de Samir solo. El consolidado no agrega información que no esté ya en uno de los dos, y con 15 casos un solo caso de diferencia son 6,7 puntos.

La diferencia entre la regla máxima y la estricta viene de 1 solo caso: `sala2_caso-001.jpg`, en la posición 1 Edwin marcó `acierto` y Samir marcó `no_sirve`. Es el único caso del set en que exactamente uno de los dos dice `acierto` y el otro no, y por eso ese caso produce a la vez la diferencia de Top 1 (7 contra 6) y la de Top 5 (8 contra 7). Los otros 6 aciertos en Top 1 los marcaron los dos jueces, así que las dos reglas coinciden en ellos.

---

# 5 · El número separado por tipo

| Tipo |  n | Top 1 | Top 5 | Utilidad |
| --- | -: | ---: | ---: | ---: |
| persona |  4 | 75,0 % (3/4) | 75,0 % (3/4) | 4,00 |
| producto |  4 | 50,0 % (2/4) | 50,0 % (2/4) | 1,75 |
| captura |  4 | 50,0 % (2/4) | 75,0 % (3/4) | 3,00 |
| dificil |  3 | 0,0 % (0/3) | 0,0 % (0/3) | 1,33 |

**Una línea:** ¿en qué tipo de foto se cae más el buscador? En `dificil`, con 0,0 % de Top 1 y 0,0 % de Top 5: en ninguno de sus 3 casos ningún juez encontró el diseño entre las 5 posiciones.

**Los mismos números por tipo y por juez, y bajo las dos reglas de combinación:**

| Tipo | n | Edwin Top 1 | Edwin Top 5 | Edwin Util. | Samir Top 1 | Samir Top 5 | Samir Util. | Máx. Top 1 | Máx. Top 5 | Máx. Util. | Estr. Top 1 | Estr. Top 5 | Estr. Util. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| persona | 4 | 75,0 % | 75,0 % | 4,00 | 75,0 % | 75,0 % | 4,00 | 75,0 % | 75,0 % | 4,00 | 75,0 % | 75,0 % | 4,00 |
| producto | 4 | 50,0 % | 50,0 % | 1,50 | 25,0 % | 25,0 % | 1,50 | 50,0 % | 50,0 % | 1,75 | 25,0 % | 25,0 % | 1,50 |
| captura | 4 | 50,0 % | 75,0 % | 3,00 | 50,0 % | 75,0 % | 3,00 | 50,0 % | 75,0 % | 3,00 | 50,0 % | 75,0 % | 3,00 |
| dificil | 3 | 0,0 % | 0,0 % | 0,67 | 0,0 % | 0,0 % | 0,67 | 0,0 % | 0,0 % | 1,33 | 0,0 % | 0,0 % | 1,33 |

El tipo `producto` es el único donde los dos jueces se diferencian: Edwin encontró 2 de 4 en posición 1, Samir encontró 1 de 4. Con la regla máxima eso se suma a 2 de 4; con la estricta se queda en 1 de 4, o sea 25,0 %.

---

# 6 · Prueba entre los dos jueces

Los mismos 15 casos, juzgados por dos personas por separado.

| | Resultado |
| --- | ---: |
| En cuántos de los 15 coincidieron los dos jueces | 13 |
| En cuántos no coincidieron | 2 |
| El desacuerdo más común fue entre… | `sirve` contra `no_sirve`, en 5 de las 6 posiciones discrepantes. La sexta fue `acierto` contra `no_sirve`. |

**Qué significa "coincidieron".** Los dos juicios cubrieron las mismas 5 posiciones de cada caso. Coincidir un caso es que las 5 posiciones tengan el mismo juicio. A nivel de posición, la coincidencia es de 69 de 75, o sea 92,0 %.

| Medida de coincidencia | Resultado |
| --- | ---: |
| Casos con las 5 posiciones iguales | 13 de 15 |
| Casos con al menos 1 posición distinta | 2 de 15 |
| Posiciones con el mismo juicio | 69 de 75 (92,0 %) |
| Posiciones con juicio distinto | 6 de 75 (8,0 %) |

**Los 2 casos con desacuerdo, posición por posición:**

| Caso | Tipo | Posiciones iguales | Posiciones discrepantes (Edwin / Samir) |
| --- | --- | ---: | --- |
| sala2_caso-001.jpg | producto | 3 de 5 | pos 1: `acierto` / `no_sirve` · pos 5: `no_sirve` / `sirve` |
| sala7_caso_08 | dificil | 1 de 5 | pos 1: `sirve` / `no_sirve` · pos 2: `no_sirve` / `sirve` · pos 3: `sirve` / `no_sirve` · pos 5: `no_sirve` / `sirve` |

**Los desaciertos, agrupados por tipo de par:**

| Desacuerdo | Posiciones |
| --- | ---: |
| `sirve` contra `no_sirve` | 5 de las 6 discrepantes |
| `acierto` contra `no_sirve` | 1 de las 6 discrepantes |

El desacuerdo sobre si un resultado era `acierto` ocurrió 1 sola vez, en la posición 1 de `sala2_caso-001.jpg`. Las otras 5 posiciones discrepantes están en el borde entre `sirve` y `no_sirve`, que es el juicio más ambiguo de los tres.

**Coincidencia por tipo de caso:**

| Tipo | Casos con las 5 posiciones iguales |
| --- | ---: |
| persona | 4 de 4 |
| producto | 3 de 4 |
| captura | 4 de 4 |
| dificil | 2 de 3 |

**Si no coincidieron en más de 3, ¿qué se hizo para alinear el criterio antes de seguir midiendo?** No se activa: no coincidieron en 2, que no es más de 3. Se deja constancia igual de que los dos jueces trabajaron por separado, sin verse, y que las 6 posiciones discrepantes quedaron anotadas tal cual, sin resolver y sin tercera persona que desempatara. No hay registro de ninguna sesión de alineación de criterio.

---

# 7 · Verificación

*La llena quien auditó, no quien midió. En esta entrega la llenaron Samir Ochoa y Andres Quispe.*

| Verificación | Resultado |
| --- | --- |
| ¿Los tres números se pueden recalcular desde el archivo en crudo y da lo mismo? | sí |
| ¿Las filas del archivo cuadran con la cantidad de casos × posiciones? | sí |
| ¿Se verificó uno por uno que cada id_correcto exista en products.csv? | sí |
| ¿Se descartó algún caso después de haber visto su resultado? | no |

**Evidencia de cada respuesta.**

*Primera, los tres números se recalculan.* Las tres cifras de cada juez se recalcularon desde `RESULTADO_JUECES.md` con un script aparte y coinciden con las que ese mismo archivo trae impresas:

| Recalculado desde el archivo en crudo | n | Top 1 | Top 5 | Utilidad |
| --- | ---: | ---: | ---: | ---: |
| Edwin Salvatierra | 15 | 46,7 % | 53,3 % | 2,40 |
| Samir Ochoa | 15 | 40,0 % | 46,7 % | 2,40 |

Salen 46,7 / 53,3 / 2,40 para Edwin y 40,0 / 46,7 / 2,40 para Samir, que es exactamente lo que el archivo imprime. El 46,7 % de la sección 4 sale de combinar los dos jueces con la regla máxima. Con estos datos ese resultado coincide con las cifras de Edwin solo, y que la combinación no aporta una tercera cifra ya queda dicho en la sección 4 y en el punto 5 de la sección 8.

*Segunda, las filas cuadran.* El archivo tiene 75 filas por juez, o sea 15 casos × 5 posiciones, y 150 en total entre los dos jueces. No hay ninguna fila repetida dentro de un mismo juez para el par (caso, posición). Los 15 `caso_id` del archivo son los mismos 15 de `casos/casos.csv`, ninguno sobra y ninguno falta. Ninguno de los 48 casos que no se usaron aparece en el archivo de juicios.

*Tercera, los id_correcto existen.* Se revisó uno por uno el `id_correcto` de los 63 casos recibidos contra los 15 272 ids de `data/products.csv`: los 63 existen, 0 inexistentes. De los 15 del set oficial, los 15 existen.

*Cuarta, no hubo descarte posterior.* No hay ningún caso del archivo de juicios que esté fuera de `casos/casos.csv`, y las dos sesiones de juicio se corrieron sobre los mismos 15 casos con las 5 posiciones ya fijadas. No se cambió el set después de ver resultados.

**Aviso sobre el archivo en crudo.** `data/juicios.csv`, que el README declara como almacenamiento activo de `app.py`, tiene 61 bytes: la cabecera y nada más. Los 150 juicios están escritos dentro de `RESULTADO_JUECES.md`, en formato de texto con los dos resúmenes de métricas intercalados. Para recalcular hay que escribir un script que lea ese markdown. Queda anotado en la sección 8.

---

# 8 · Qué no funciona o qué quedó débil

**1 · La columna `id_correcto` no sirve como verdad de referencia.** En los 15 casos medidos, el `id_correcto` de `casos/casos.csv` coincide con algún resultado que un juez marcó como `acierto` solo en 3 de 15: `sala6_caso-001`, `sala6_caso-005` y `sala6_caso-007`. En los otros 12 no coincide con ninguno. En 10 de 15 el valor es un id de relleno, la serie `AIM-P001-001` … `AIM-P001-010`, y en `casos-completo.csv` hay 32 filas con esa misma serie. Esos ids sí existen en `products.csv`, por eso el filtro automático no los agarró, pero no dicen qué camiseta es la correcta. Las tres métricas salen del juicio humano y no de esa columna, así que los números de arriba no quedan invalidados. Lo que sí queda invalidado es recalcular Top 1 comparando ids desde el CSV: saldría otra cosa.

**2 · Los dos jueces no juzgaron la misma lista de resultados.** En 24 de las 75 posiciones (32,0 %) el `id_resultado` es distinto entre las dos sesiones. En 3 casos las 5 posiciones vinieron diferentes y en 8 de los 15 las 5 vinieron iguales. El caso más claro es `sala2_caso-001.jpg`, donde las 5 posiciones se compararon contra conjuntos de resultados distintos:

| Posición | Edwin vio | score | Samir vio | score |
| ---: | --- | ---: | --- | ---: |
| 1 | `AIM-P167-054` | 0,6681 | `AIM-P167-054` | 0,6826 |
| 2 | `AIM-P170-046` | 0,6637 | `AIM-P005-013` | 0,6810 |
| 3 | `AIM-P199-054` | 0,6574 | `AIM-P136-033` | 0,6786 |
| 4 | `AIM-P197-020` | 0,6534 | `AIM-P170-046` | 0,6775 |
| 5 | `AIM-P240-014` | 0,6528 | `AIM-P240-014` | 0,6744 |

3 de las 5 posiciones Traen un producto distinto. Además ningún score coincide, ni siquiera en las dos posiciones donde el producto sí es el mismo. El buscador no devolvió lo mismo en la corrida de las 03:57Z que en la de las 13:48Z. Con eso, la prueba entre jueces de la sección 6 mezcla dos cosas: desacuerdo de criterio y listas que no se pueden comparar una a una.

| Caso | Posiciones con `id_resultado` distinto |
| --- | ---: |
| sala6_caso-001 | 5 de 5 |
| sala7_caso_03 | 5 de 5 |
| sala7_caso_04 | 5 de 5 |
| sala2_caso-001.jpg | 3 de 5 |
| sala7_caso_02 | 2 de 5 |
| sala7_caso_08 | 2 de 5 |
| sala7_caso_10 | 2 de 5 |

**3 · La reducción de 63 a 15 no tiene criterio escrito.** No hubo descartes, y eso está bien, pero tampoco quedó registrado por qué se eligieron esos 15 y no otros. La consecuencia es visible en la cobertura: 9 de los 15 vienen de Sala 7, 4 de Sala 6, 1 de Sala 2 y 1 de Sala 5. Salas 1 y 3 no aportan ningún caso al set final, y Sala 4 nunca entregó. Si la elección de los 15 no fue al azar, y a la vista de la columna `quien_eligio` cada sala eligió los suyos, entonces el set final refleja lo que cada sala quiso mostrar y no una muestra de las 7 salas. La medición no se puede leer como una foto del comportamiento del buscador en general.

**4 · El tamaño del set no aguanta las preguntas que la ficha le hace.** n = 15 en total, y por tipo 3, 4, 4 y 4. El tipo `dificil`, que es el que sale peor, tiene 3 casos. Ninguna cifra de la sección 5 resiste el cambio de un solo caso. El Top 1 de `producto` sale de 2 aciertos sobre 4: con la regla estricta de la sección 4 baja a 25,0 %, o sea que un solo caso lo dobla o lo parte a la mitad.

**5 · La cifra oficial no es una tercera cifra: es la de uno de los jueces.** Con la regla máxima, el consolidado da 46,7 % de Top 1 y 53,3 % de Top 5, que son exactamente las cifras de Edwin solo. Con la regla estricta da 40,0 % y 46,7 %, que son exactamente las de Samir solo. La única posición del set en que un juez dice `acierto` y el otro `no_sirve` es la posición 1 de `sala2_caso-001.jpg`, y ese caso solo decide cuál de las dos cifras sale. Además la regla de combinación no está fijada en ninguna ficha: hubo que elegir entre `acierto` si cualquiera de los dos lo marcó o `acierto` solo si ambos lo marcaron, y la elección es del equipo. Con 2 casos de desacuerdo el efecto es chico, 6,7 puntos; con un set donde los jueces discrepan más, la diferencia crecería.

**6 · Los números por tipo no separan lo que quieren separar.** `persona`, `producto`, `captura` y `dificil` son etiquetas que puso cada sala al armar su caso, leídas del CSV tal cual, sin ninguna revisión de que correspondan a lo que dicen. No hay una definición escrita de los cuatro criterios. Con 3 o 4 casos por tipo, esa separación no puede sostenerse igual.

**7 · Las dos causas de descarte que se resuelven mirando imágenes no tienen registro.** El `id_correcto` inexistente dio 0 y la foto repetida dio 0, y los dos se comprobaron con programa sobre las 63 fotos. Pero «la foto salía del catálogo» y «no son la misma camiseta» se resuelven con el ojo, y no hay ningún archivo que deje por escrito esa revisión caso por caso. El 0 que aparece en la sección 2 para esas dos filas es el resultado de la decisión del equipo, no una cuenta que se pueda volver a correr. `auditoria_filtros.py` debía volcar el detalle en `data/lista_casos_descartados.txt` y ese archivo no existe; además `auditoria_finaliza_sin_las_reglas.py` tiene los contadores escritos a mano en las líneas 19 a 22, no leídos de ningún archivo.

**8 · La lista de los 48 casos que no se usaron no está en ninguna parte.** Con `casos/casos-completo.csv`, de 63 filas, se sabe exactamente cuáles 15 entraron y por lo tanto cuáles 48 quedaron fuera. Lo que no existe es un documento que liste esos 48 con la sala de origen y una nota de por qué no se midieron, que es lo que la ficha 05-A pide como cuarto archivo adjunto.

**9 · El archivo de juicios en crudo que pide la ficha no existe como archivo de datos.** `data/juicios.csv`, que el `README.md` declara como almacenamiento activo de `app.py`, tiene 61 bytes: la cabecera y nada más. Los 150 juicios están pegados dentro de un `.md`, `RESULTADO_JUECES.md`, con los dos resúmenes de métricas intercalados. Para recalcular hay que escribir un script que lea ese markdown; no es abrir una hoja de cálculo y contar filas.

**10 · No se puede comparar contra la medición anterior.** El 92 % que se quería corregir venía de imágenes fabricadas a partir del propio catálogo, y no quedó guardado el detalle de esa corrida. No hay línea base contra la cual leer estos 46,7 / 53,3.

---

# 9 · Archivos que acompañan

| Archivo | Nombre y ruta |
| --- | --- |
| Archivo de juicios en crudo | `proyecto_GRUPOS_B/RESULTADO_JUECES.md` — 150 filas de juicio, 75 de Edwin Salvatierra y 75 de Samir Ochoa, con los dos resúmenes de métricas intercalados. Nota: `proyecto_GRUPOS_B/data/juicios.csv`, que el README declara como almacenamiento activo, está vacío, solo la cabecera. |
| Planilla del set oficial (con la columna `quien_eligio`) | `proyecto_GRUPOS_B/casos/casos.csv` — 15 filas, columnas `caso_id,id_correcto,tipo,sala_origen,quien_eligio`. |
| Carpeta de fotos del set oficial | `proyecto_GRUPOS_B/casos/fotos/` — 15 archivos, uno por cada `caso_id`. Las 63 fotos recibidas de las 6 salas están en `proyecto_GRUPOS_B/casos/fotos-completo/`. |
| Lista de casos descartados, con el motivo de cada uno | `proyecto_GRUPOS_B/casos/casos-completo.csv` — 63 filas. No hubo descartes, así que no hay lista de descartados: este archivo marca los 63 casos recibidos y, al restar las 15 filas de `casos.csv`, se obtienen los 48 que no se usaron, con su sala de origen en la columna `sala_origen`. No hay columna de motivo porque no hubo motivos que registrar. |

**Nota sobre la lista de descartados.** La plantilla pide un cuarto archivo con los casos descartados y su motivo. En esta medición los cuatro contadores de descarte dan 0, así que ese archivo no tiene contenido que reportar. Lo que sí se puede dar es el complemento: los 48 casos que no entraron a la medición, identificables restando los dos CSV. Si en la revisión se considera que esa lista debe existir igual, el camino es agregarle a `casos-completo.csv` una columna `motivo_no_medido` y llenarla con el motivo por el que cada caso quedó fuera, que en esta versión no está escrito en ningún lado.

---

*Sublitex · Biblioteca visual · Ficha 05-A · Plantilla de entrega · Versión 1.0*
