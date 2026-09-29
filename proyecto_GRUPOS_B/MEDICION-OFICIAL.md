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

| Quién preparó el set | Grupo B — Jhon Portugal, Edwin Salvatierra, Samir Ochoa y Andres Quispe. Consolidaron en `casos/casos-completo.csv` lo que entregaron 6 salas; la Sala 4 no entregó casos. |
| --- | --- |
| Quién auditó el set | Samir Ochoa y Andres Quispe |
| Quiénes juzgaron | Edwin Salvatierra y Samir Ochoa |
| Fecha de la medición | 2026-09-29 |
| Cómo se levanta la herramienta (una línea) | Con la API ya arriba (`python -m uvicorn api.main:app --port 8000`), `streamlit run app.py` dentro de `proyecto_GRUPOS_B/`. |

Los 15 casos los eligieron 5 personas: Sebastian Lopez 5, Esteban Moreno 4, Kevin Chacon 4, Luis Bazan 1 y Luciano Acuña 1. Salas 1, 3 y 4 no aportan ningún caso al set.

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

**Una línea:** ¿de qué sala vinieron la mayoría de los descartes y por qué motivo? No hubo descartes, así que no hay sala de la que vinieron. Los 48 que no entraron no se rechazaron: la ficha pide 15 casos y solo hacía falta esa cantidad.

Por sala entraron 1 de la Sala 2, 1 de la Sala 5, 4 de la Sala 6 y 9 de la Sala 7. De los dos filtros que sí se pueden correr con programa, `id_correcto` inexistente dio 0 de 63 contra los 15 272 ids de `data/products.csv`, y foto repetida dio 0 porque los 63 archivos de `casos/fotos-completo/` tienen 63 `sha256` distintos. Los otros dos filtros se resuelven mirando imágenes y no tienen registro escrito.

---

# 3 · Cómo quedó repartido por tipo

| Tipo | Casos |
| --- | ---: |
| persona | 4 |
| producto | 4 |
| captura | 4 |
| dificil | 3 |

**Si algún tipo quedó con menos de 8 casos, anotarlo acá:** los cuatro están por debajo de 8, así que ese número no es confiable todavía. `dificil` quedó con 3 casos y los otros tres con 4 cada uno. El tipo lo puso cada sala al armar su caso y no hay una definición escrita de los cuatro criterios.

---

# 4 · El número

| Número | Resultado |
| --- | ---: |
| Casos medidos (n) | 15 |
| Top 1 (%) | 46,7 % (7/15) |
| Top 5 (%) | 53,3 % (8/15) |
| Utilidad (de 0 a 5) | 2,60 |

Los dos jueces juzgaron los mismos 15 casos por separado y sus juicios se combinan posición por posición: `acierto` si alguno de los dos marcó `acierto`, si ninguno `sirve` si alguno marcó `sirve`, y `no_sirve` si ninguno marcó nada útil. Esa es la regla que da el 2,60 de arriba.

Si `acierto` exige que los dos jueces coincidan, el resultado es 40,0 % de Top 1 (6/15), 46,7 % de Top 5 (7/15) y 2,53 de utilidad. La regla no está fijada en ninguna ficha, así que reportamos la primera y dejamos la segunda escrita. Queda anotado en la sección 8.

Por separado: Edwin 46,7 % / 53,3 % / 2,40 y Samir 40,0 % / 46,7 % / 2,40.

---

# 5 · El número separado por tipo

| Tipo |  n | Top 1 | Top 5 | Utilidad |
| --- | -: | ---: | ---: | ---: |
| persona |  4 | 75,0 % (3/4) | 75,0 % (3/4) | 4,00 |
| producto |  4 | 50,0 % (2/4) | 50,0 % (2/4) | 1,75 |
| captura |  4 | 50,0 % (2/4) | 75,0 % (3/4) | 3,00 |
| dificil |  3 | 0,0 % (0/3) | 0,0 % (0/3) | 1,33 |

**Una línea:** ¿en qué tipo de foto se cae más el buscador? En `dificil`, con 0,0 % en las dos métricas: en ninguno de sus 3 casos ningún juez encontró el diseño entre las 5 posiciones.

---

# 6 · Prueba entre los dos jueces

Los mismos 15 casos, juzgados por dos personas por separado.

|  | Resultado |
| --- | ---: |
| En cuántos de los 15 coincidieron los dos jueces | 13 |
| En cuántos no coincidieron | 2 |
| El desacuerdo más común fue entre… | `sirve` y `no_sirve` |

Sobre las 75 posiciones, 69 tienen el mismo juicio en las dos sesiones y 6 no. De esas 6, cinco son `sirve` contra `no_sirve` y una sola es `acierto` contra `no_sirve`, en la posición 1 de `sala2_caso-001.jpg`. Los dos casos que no coincidieron en las 5 posiciones son `sala2_caso-001.jpg`, con 3 de 5 iguales, y `sala7_caso_08`, con 1 de 5.

**Si no coincidieron en más de 3, ¿qué se hizo para alinear el criterio antes de seguir midiendo?** No se documentó ninguna sesión de alineación. No se llegó a 3 casos, así que no hacía falta, y los 2 que quedaron se reportan tal cual, sin corregir ninguno de los dos jueces.

---

# 7 · Verificación

*La llena quien auditó, no quien midió.*

| Verificación | Resultado |
| --- | --- |
| ¿Los tres números se pueden recalcular desde el archivo en crudo y da lo mismo? | sí |
| ¿Las filas del archivo cuadran con la cantidad de casos × posiciones? | sí |
| ¿Se verificó uno por uno que cada id_correcto exista en products.csv? | sí |
| ¿Se descartó algún caso después de haber visto su resultado? | no |

Los tres números se recalcularon desde las 150 filas de `RESULTADO_JUECES.md` y dan lo mismo que las cifras de arriba. El archivo tiene 75 filas por juez, o sea 15 casos × 5 posiciones, 150 en total, sin filas repetidas dentro de un mismo juez, y los 15 `caso_id` son los de `casos/casos.csv`. Los 63 `id_correcto` de los casos recibidos existen en `data/products.csv`. No se descartó ningún caso después de ver su resultado: los 15 quedaron fijados antes de las dos sesiones de juicio.

Una advertencia para quien recalcule: la utilidad no es un promedio de puntos. Es la cantidad de posiciones cuyo juicio no es `no_sirve`, dividida por la cantidad de casos, y por eso su máximo es 5 (`calcular_metricas` en `proyecto_GRUPOS_B/app.py`). Con la intuición de promediar 5, 2 y 0 sobre las posiciones se obtiene 2,20 en vez de 2,40.

`data/juicios.csv`, que el README declara como almacenamiento activo, tiene solo la cabecera. Los juicios viven dentro de `RESULTADO_JUECES.md`.

---

# 8 · Qué no funciona o qué quedó débil

**1 · La regla de combinación no está escrita en ninguna ficha.** Hubo que elegir si `acierto` es cuando cualquiera de los dos lo marcó o solo cuando lo marcaron los dos. La primera da 46,7 / 53,3 / 2,60 y la segunda 40,0 / 46,7 / 2,53: 6,7 puntos de diferencia en las dos métricas. Elegir una u otra es decisión del equipo, no una consecuencia de los datos, y con 15 casos un solo caso ya son 6,7 puntos.

**2 · La columna `id_correcto` no sirve como verdad de referencia.** En 10 de los 15 casos su valor es un id de relleno, la serie `AIM-P001-001` a `AIM-P001-010`. Esos ids existen en `products.csv`, por eso el filtro automático no los agarró, pero no dicen qué camiseta es la correcta. Las métricas salen del juicio humano y no de esa columna; lo que no serviría es recalcular el Top 1 comparando ids desde el CSV.

**3 · n = 15 es poco y `dificil` tiene 3 casos.** Ninguna cifra de la sección 5 resiste que un solo caso cambie. El 0,0 % de `dificil` sale de 3 casos, y con 3 casos eso no distingue que el buscador falle de que esos tres casos sean difíciles.

**4 · La reducción de 63 a 15 no tiene criterio escrito.** No hubo descartes, pero tampoco quedó registrado por qué se eligieron esos 15. Entraron 9 de la Sala 7, 4 de la Sala 6, 1 de la Sala 2 y 1 de la Sala 5; Salas 1, 3 y 4 no aportan nada. Como cada sala eligió los suyos, el set refleja lo que cada sala quiso mostrar y no una muestra de las 7 salas.

---

# 9 · Archivos que acompañan

| Archivo | Nombre y ruta |
| --- | --- |
| Archivo de juicios en crudo | `proyecto_GRUPOS_B/RESULTADO_JUECES.md` — 150 filas de juicio, 75 de cada juez, con los resúmenes de métricas intercalados. |
| Planilla del set oficial (con la columna `quien_eligio`) | `proyecto_GRUPOS_B/casos/casos.csv` — 15 filas, columnas `caso_id,id_correcto,tipo,sala_origen,quien_eligio`. |
| Carpeta de fotos del set oficial | `proyecto_GRUPOS_B/casos/fotos/` — 15 imágenes, una por `caso_id`. Las 63 recibidas están en `proyecto_GRUPOS_B/casos/fotos-completo/`. |
| Lista de casos descartados, con el motivo de cada uno | `proyecto_GRUPOS_B/casos/casos-completo.csv` — 63 filas. No hubo descartes, así que esa lista no tiene contenido: restando las 15 filas de `casos.csv` salen los 48 que no se usaron, con su sala en la columna `sala_origen`. |

---

*Sublitex · Biblioteca visual · Ficha 05-A · Plantilla de entrega · Versión 1.0*
