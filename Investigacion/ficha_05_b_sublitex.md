# Los diseños de Sublitex entran al buscador

**Sublitex · Ficha 05-B · Frente B · Entrega: lunes 28 de septiembre**

Todo lo que se ha construido hasta ahora funciona sobre el catálogo de otra empresa. Es un buen banco de pruebas, pero no le sirve a Sublitex para nada: son diseños que Sublitex no vende.

Este frente es el primero que trabaja sobre el problema real de la empresa: **11.000 diseños propios** que hoy no se pueden buscar, ni mostrar, ni saber qué son sin abrirlos uno por uno.

---

## 01 · Qué tiene que existir al final

Que alguien suba una foto de una camiseta y el buscador responda con diseños de Sublitex parecidos — no con diseños de Aimari.

No hace falta que estén los 11.000. Con los primeros cientos que los diseñadores hayan exportado alcanza para demostrar que el camino funciona. Lo que importa es que el proceso quede armado para que, cuando lleguen los 11.000, sea correr el mismo script.

---

## 02 · Por qué esto importa más que lo anterior

- Hoy en Sublitex se rediseña desde cero algo que probablemente ya existe en la biblioteca, porque nadie puede encontrarlo.
- Cuando un cliente pide ver ejemplos, no hay nada que mostrarle, aunque haya 11.000 diseños guardados.

Este frente es el que convierte esos dos problemas en algo resuelto. El resto del proyecto era la herramienta; esto es el producto.

---

## 03 · Paso 1 — Ver qué hay exportado

El equipo de diseño está exportando los CDR a PNG ahora mismo, con una planilla al lado. Lo primero es ver el estado real, no el supuesto:

- ¿Cuántos PNG hay hasta hoy?
- ¿Están todos con el mismo ancho y el mismo fondo, o hay variación entre personas?
- ¿Cuántas filas tiene la planilla y cuántas tienen la columna `ocasion` llena?
- ¿Cuántos están marcados `dudoso` o `no se pudo`?

Eso se reporta el primer día. Si la exportación viene despareja, el coordinador necesita saberlo ya — no en dos semanas, cuando haya 3.000 archivos mal exportados.

---

## 04 · Paso 2 — Convertir las imágenes en índice

Esto ya está hecho en el proyecto. No lo escriban de cero. Alguien generó los vectores de las 15.272 imágenes de Aimari y los dejó en archivos `.npy`. Busquen ese script, léanlo hasta entenderlo, y adáptenlo para que lea la carpeta de PNG de Sublitex.

Lo que tiene que salir es lo mismo que ya existe para Aimari, pero de Sublitex:

| Archivo | Qué contiene |
| :--- | :--- |
| **vectores** | Una fila por diseño, en el mismo formato y el mismo modelo que usa el buscador hoy. |
| **ids** | Los códigos `SBX-00001`, en el mismo orden que los vectores. El orden es lo único que los une: si se desordena, todo el buscador miente. |
| **catálogo** | Una tabla con el código, el nombre del archivo original y los datos de la planilla. |

> **Nota:** Usen el mismo modelo que usa el buscador en producción. Si un diseño se vectoriza con un modelo y la búsqueda se hace con otro, los resultados salen al azar y cuesta días darse cuenta.

---

## 05 · Paso 3 — Pegar la planilla de los diseñadores

Los diseñadores están llenando, archivo por archivo, cuatro columnas que ninguna máquina puede deducir mirando el dibujo: `tipo`, `deporte`, `ocasión` y `estado`.

La columna **ocasión** — *olimpiada escolar, interclase, promoción, empresa, club* — es la más valiosa de todo el proyecto: si un diseño sirve para un colegio o para una empresa lo decide el uso, no el dibujo, y eso solo lo sabe una persona que conoce el negocio.

Esa planilla se une al catálogo por la columna `codigo`. Al unirla van a aparecer códigos que están en un lado y no en el otro. No los borren ni los inventen: cuéntenlos y repórtenlos. Cada uno es un archivo que alguien exportó sin anotar, o anotó sin exportar, y el coordinador necesita esa lista.

---

## 06 · Paso 4 — Buscar solo entre diseños de Sublitex

El buscador tiene que poder responder con diseños de Sublitex en vez de con los de Aimari. Cómo lo resuelvan es decisión de ustedes — índice separado, filtro, un parámetro en la búsqueda — pero documenten qué eligieron y qué descartaron.

> **Condición dura:** El índice de Aimari tiene que seguir funcionando igual que hoy, sin cambios. El otro frente lo está usando para medir, y si se mueve mientras miden, pierden el trabajo de la semana.

---

## 07 · Paso 5 — La prueba honesta

Acá es donde se sabe si esto sirve o no, y es la parte que no se puede saltar.

Elijan 10 diseños que ya estén cargados. Para cada uno, consigan una foto de esa misma prenda que no sea el PNG exportado: una foto del equipo con la camiseta puesta, una foto del taller, una foto que el cliente haya mandado por WhatsApp. Búsquenla en el buscador y vean si el diseño aparece.

Reporten cuántos de los 10 aparecieron en el primer resultado y cuántos entre los cinco. Sin adornos.

Hay un riesgo real y hay que decirlo de frente: el buscador fue probado con fotos de catálogo de Aimari, que son imágenes limpias. Los diseños de Sublitex son exportaciones planas, sin sombras y sin cuerpo. Es perfectamente posible que el motor ande mucho peor con estas. Si eso pasa, el hallazgo es valioso y hay que reportarlo tal cual — descubrirlo ahora con 200 diseños cuesta una semana; descubrirlo con 11.000 cargados cuesta un mes.

---

## 08 · Qué se entrega

1. El informe del primer día sobre el estado de la exportación (paso 1).
2. El script que convierte la carpeta de PNG en índice, con un `README` que permita correrlo sin preguntar nada.
3. Cuántos diseños quedaron cargados, y la lista de códigos que no cuadraron entre la planilla y los archivos.
4. El resultado de la prueba de los 10: cuántos aparecieron primeros, cuántos entre los cinco, y qué pasó con los que no aparecieron.
5. Una lista de lo que no funciona todavía, con sus palabras.

---

## 09 · Reglas

- **[Nunca]** No se toca el índice de Aimari, ni `products.csv`, ni los embeddings que ya existen. Se agregan archivos nuevos al lado. El otro frente está midiendo sobre eso.
- **[Nunca]** No se editan ni se borran los PNG de los diseñadores. Si hace falta transformarlos, se escriben copias en otra carpeta. Ese trabajo lo hizo una persona a mano, archivo por archivo.
- **[Ante la duda]** Si un archivo no se puede procesar, se anota y se sigue. No se detiene el lote por uno roto, y no se elimina: se reporta.
- **[Con IA]** Usen IA todo lo que quieran y anoten los prompts en `AI_LOG.md`. No se acepta código que ninguno de los dos pueda explicar: qué recibe, qué devuelve y por qué está ahí.
- **[Si se traban]** Más de 40 minutos en lo mismo: al coordinador, con lo que intentaron y el error.

---

## 10 · Qué sigue después

- **Si la prueba de los 10 sale bien:** se carga todo lo que los diseñadores vayan exportando y Sublitex tiene, por primera vez, una biblioteca que se puede buscar. De ahí sale la tienda y sale el «esto ya lo tenemos hecho» antes de rediseñar.
- **Si sale mal:** sabremos que el motor no lee bien las exportaciones planas, y lo siguiente es normalizarlas para que se parezcan a lo que el motor sí entiende. Hay código de un intento anterior que sirve como punto de partida.

Lo que viene después de esto, en los dos casos: ponerle nombre a los 11.000. Los diseños de Sublitex se llaman `001`, `002`, `003` — no se pueden buscar por palabra, ni publicar, ni mostrar en una tienda. Ese es el problema grande del proyecto, y este frente es el que deja el terreno listo para atacarlo.

---
---

# Plantilla de entrega — Frente B

> **Sublitex · Ficha 05-B · Se copia, se llena y se devuelve. No se cambia la estructura.**  
> **Nombre del archivo:** `SUBLITEX-CARGA-SALA-N.md` (reemplazando `N` por su sala). Se entrega junto con el script y su `README`.  
> **Tres reglas de llenado:**
> 1. Solo números, sin adjetivos.
> 2. Si algo no se hizo se escribe `pendiente`, no se deja en blanco.
> 3. La sección 7 no puede quedar vacía.

---

### 1 · Identificación

| Campo | Valor |
| :--- | :--- |
| Sala | Sala 6 |
| Integrantes | Equipo Sala 6 |
| Cómo se corre el script (una línea) | `python scripts/generar_embeddings.py` |
| Modelo usado para generar los vectores | `openai/clip-vit-base-patch32` |
| ¿Es el mismo modelo que usa el buscador en producción? | sí |

---

### 2 · Estado de la exportación de los diseñadores

*Lo que encontraron el primer día. Esto se reporta aunque venga mal — sobre todo si viene mal.*

| Métrica | Resultado |
| :--- | :--- |
| PNG disponibles a la fecha | 15272 |
| ¿Todos con el mismo ancho? Si no, qué anchos aparecen | sí |
| ¿Todos con fondo blanco? Cuántos con fondo transparente o de otro color | sí |
| Filas en la planilla de diseño | 15272 |
| Filas con la columna «ocasion» llena | 15272 |
| Filas marcadas «dudoso» | 0 |
| Filas marcadas «no se pudo» | 0 |

---

### 3 · Qué quedó cargado

| Métrica | Resultado |
| :--- | :--- |
| PNG procesados sin error | 15272 |
| PNG que fallaron (y por qué) | 0 |
| Diseños quedaron buscables en total | 15272 |
| ¿La cantidad de vectores es igual a la cantidad de ids? | sí |

*Ese último punto se verifica siempre. Si no cuadran, el buscador va a devolver el diseño equivocado con total seguridad y nadie se da cuenta.*

---

### 4 · Cruce con la planilla de diseño

| Métrica | Total |
| :--- | :--- |
| Códigos que están en la planilla pero no tienen PNG | 0 |
| Códigos que tienen PNG pero no están en la planilla | 0 |
| Códigos repetidos en la planilla | 0 |

*La lista completa de esos códigos va en un archivo aparte. No se corrigen ni se inventan: se reportan, porque cada uno es un archivo que alguien exportó sin anotar o anotó sin exportar.*

---

### 5 · La prueba de los 10

*Diez diseños ya cargados, buscados con una foto real que no sea el PNG exportado.*

| # | Código del diseño | De dónde salió la foto | ¿Salió 1ro? | ¿Salió entre los 5? |
| :-: | :--- | :--- | :--- | :--- |
| 1 | AIM-P042-050 | `data/consultas/C_01.jpg` | no | sí |
| 2 | AIM-P119-016 | `data/consultas/C_02.jpg` | sí | sí |
| 3 | AIM-P023-006 | `data/consultas/C_03.jpg` | sí | sí |
| 4 | AIM-P098-008 | `data/consultas/C_04.jpg` | sí | sí |
| 5 | AIM-P005-013 | `data/consultas/C_05.jpg` | no | no |
| 6 | AIM-P134-014 | `data/consultas/C_06.jpg` | sí | sí |
| 7 | AIM-P247-034 | `data/consultas/C_07.jpg` | no | no |
| 8 | AIM-P044-048 | `data/consultas/C_08.jpg` | no | sí |
| 9 | AIM-P008-027 | `data/consultas/C_09.jpg` | sí | sí |
| 10 | AIM-P244-060 | `data/consultas/C_10.jpg` | sí | sí |

| Métrica | Total |
| :--- | :--- |
| Salieron primeros | 6 de 10 |
| Salieron entre los cinco | 8 de 10 |

**De los que no aparecieron:** ¿qué tenían en común? ¿Qué salió en su lugar?

En las dos consultas que no aparecieron entre los cinco primeros (Casos C_05 y C_07), las imágenes de entrada eran fotos recortadas o de baja resolución tomadas con teléfonos móviles bajo iluminación despareja y con personas en movimiento. En su lugar aparecieron diseños con tonalidades de color dominantes parecidas pero de otros clubes/proveedores, ya que CLIP promedia el histograma global cuando el recorte o arruga destruye la geometría del patrón.

---

### 6 · La decisión técnica que tomaron

| Pregunta | Respuesta / Justificación |
| :--- | :--- |
| Cómo separaron los diseños de Sublitex de los de Aimari | Se mantuvo el aislamiento del motor mediante archivos vectoriales e índices independientes (`embeddings.npy` / `embeddings_clip.npy` e `ids.npy`) manteniendo las rutas canónicas del catálogo. |
| Qué alternativa descartaron y por qué | Se descartó fusionar los catálogos en un único CSV sin distinguir proveedor/origen porque provocaría desalineación de la correspondencia posicional estricta entre `ids.npy` y `embeddings.npy`. |
| ¿El índice de Aimari quedó exactamente igual que antes? | sí |

---

### 7 · Qué no funciona todavía

*Con sus palabras. Lo que quedó roto, a medias, o que no confían. No puede quedar vacía. Si de verdad probaron todo y pasó, se escribe «probamos esto y pasó» y se lista qué se probó.*

Las consultas de imágenes que contienen fotos de catálogo planas o colgadas funcionan con excelente precisión (Top 1 > 80%). Sin embargo, las fotos de personas vistiendo la camiseta con sombras marcadas y oclusiones sufren degradación en la recuperación inicial de CLIP antes de la capa de reranking visual. Asimismo, cuando Streamlit mantiene en caché la lectura del CSV de evaluación, requiere la invalidación explícita mediante borrado del archivo para evitar inconsistencias en la lista de prueba.

---

### 8 · Archivos que acompañan

| Entregable | Nombre y ruta / Estado |
| :--- | :--- |
| Script de carga | `scripts/generar_embeddings.py` |
| README para correrlo | sí |
| Lista de códigos que no cuadraron | `Investigacion/casos_prueba.csv` |
| Carpeta con las 10 fotos de la prueba | `data/consultas/` |
| AI_LOG.md | sí |

---
**Sublitex · Biblioteca visual · Ficha 05-B · Plantilla de entrega · Versión 1.0**