# **El evaluador del buscador**

*Sublitex · Ficha 03-A · Programación · Entrega: lunes*  
Construir la herramienta con la que una persona califica los resultados del buscador y el sistema saca el número. Esta ficha va paso a paso: si sigues los pasos en orden, llegas.  
---

**Qué tiene que existir el lunes:** una pantalla donde se ve una foto arriba, los cinco resultados del buscador abajo, y tres botones en cada resultado. Al final, un número.  
Trabajan en pareja. Los dos tienen que poder explicar cualquier parte del código. Entrega en **evaluador/** dentro de tu propia carpeta, no en la de otra pareja.

## ---

**01 · Lo que ya existe y no hay que construir**

El buscador ya está hecho y funcionando. Tu herramienta no busca nada: le pregunta al buscador y muestra lo que responde.

| Campo | Valor | Por qué |
| :---- | :---- | :---- |
| API que ya existe | **POST /search/image** | Le mandas una imagen y te devuelve los cinco diseños más parecidos. |
| Comprobar que está viva | **GET /health** | Si esto no responde, la API no está levantada. Ese es siempre el primer chequeo. |
| Lo que devuelve cada resultado | **id · nombre · imagen · url · score** | Cinco resultados en un arreglo JSON, del más parecido al menos parecido. |

## **02 · Los pasos**

> 1. **Levantar la API y comprobar que responde**  
>    Antes de escribir una línea de tu herramienta. Levanta la API del proyecto y entra a **/health** desde el navegador.  
>    Tienes que ver un JSON que dice cuántos productos y cuántos embeddings tiene cargados. **Anota esos dos números.** Si no son iguales entre sí, avisa al coordinador y no sigas: el índice está roto y cualquier medición que hagas va a estar mal.  
> 2. **Probar la API a mano, una sola vez**  
>    Con Swagger (entra a **/docs**), con Postman o con **curl**: manda **una** foto de camiseta y mira el JSON que vuelve.  
>    No pases al paso 3 hasta haber visto ese JSON con tus ojos. Sabrás exactamente qué campos tiene y cómo se llaman, y te vas a ahorrar dos horas de adivinar.  
> 3. **Armar tus 10 casos de prueba**  
>    Los diseñadores están armando 180 casos, pero todavía no están listos. Para construir y probar tu herramienta necesitas datos ahora, así que **tu pareja arma 10 casos**.  
>    Un caso es: una foto de una camiseta sacada de internet, y el código del diseño del catálogo que le corresponde. Abres la carpeta **data/images\_normalized**, eliges un diseño de un equipo conocido, buscas en Google una foto real de esa camiseta, y la guardas.  
>    Guárdalos así:  
>    *casos/*  
>    *  caso-001.jpg*  
>    *  caso-002.jpg*  
>    *  ...*  
>    *  casos.csv → caso,id\_correcto,tipo*  
>    **La foto no puede ser la imagen del catálogo.** Si la pregunta y la respuesta son la misma imagen, la medición no vale nada.  
> 4. **Construir la pantalla**  
>    Hazla en lo que ya sabes. HTML y JavaScript sueltos alcanza y sobra; si prefieres Next, también. No hace falta Python para esta parte.  
>    La pantalla muestra **un caso a la vez**, así:  
   * Arriba, grande: la foto de consulta.  
   * Abajo: los 5 resultados en fila, cada uno con su imagen, su nombre y su score.  
   * En cada resultado, tres botones: **Acierto** · **Sirve** · **No sirve**.  
   * Un botón «Siguiente» que pasa al caso que viene.  
   * Arriba a la derecha, el avance: «caso 7 de 10».

> Nada más. Sin login, sin base de datos, sin menús. Cuanto más simple, mejor la nota.

> 5. **Definir bien los tres botones**  
>    Este es el criterio, y no se cambia. Pónganlo escrito en la propia pantalla para que quien evalúe lo tenga a la vista:

| Botón | Cuándo se aprieta |
| :---- | :---- |
| Acierto | Es el mismo diseño, aunque cambie el color, el año, el escudo o el sponsor. |
| Sirve | No es el mismo, pero se lo mostrarías al cliente y lo aceptaría. |
| No sirve | Es otro diseño. |

> 6. **Guardar cada clic**  
>    Cada vez que alguien aprieta un botón, se guarda una fila en un archivo **resultados.csv** con exactamente estas columnas:  
>    *caso, id\_correcto, posicion, id\_resultado, score, juicio, quien, fecha*  
>    **Se guarda en el momento del clic, no al final.** Si el navegador se cierra a la mitad, no se puede perder el trabajo hecho.  
> 7. **Calcular los tres números**  
>    Una pantalla final, o un script aparte, que lea **resultados.csv** y saque esto:

| Número | Cómo se calcula |
| :---- | :---- |
| Top 1 | De todos los casos, en qué porcentaje el resultado de la **posición 1** recibió «Acierto». |
| Top 5 | De todos los casos, en qué porcentaje hubo un «Acierto» en **cualquiera** de las 5 posiciones. |
| Utilidad | Promedio de cuántos de los 5 resultados recibieron «Acierto» o «Sirve». Va de 0 a 5\. |

> 8.   
>    Los tres números **también divididos por tipo de foto** (persona, producto, captura, difícil). Esa división es la que dice dónde falla el buscador, y es la parte más útil de todo el trabajo.  
> 9. **Escribir el README**  
>    Un archivo corto, en la carpeta, con cuatro cosas: cómo se levanta, cómo se cargan los casos, dónde queda el CSV, y qué significan los tres números.  
>    Tiene que servir para que otra persona lo levante sin preguntarte nada. Va a probarse así.

## **03 · Cómo se va a revisar el lunes**

El coordinador va a hacer exactamente esto, delante de ustedes. Conviene que lo prueben antes.

> 1. Levantar la herramienta siguiendo solo el README, sin preguntar nada.  
> 2. Cargar los 10 casos y evaluarlos apretando botones.  
> 3. Cerrar el navegador a la mitad y volver a abrir. *Lo evaluado hasta ahí tiene que seguir estando.*  
> 4. Abrir el **resultados.csv** y ver que las filas están completas.  
> 5. Ver los tres números, en total y por tipo de foto.  
> 6. Preguntarle a cada uno de los dos, por separado, cómo se calcula el Top 5\. *Si uno de los dos no lo sabe explicar, la pareja no aprueba aunque el código funcione.*

## **04 · Reglas**

> * **\[Nunca\] No toquen el buscador ni el índice.** Ni los embeddings, ni **products.csv**, ni el motor de búsqueda. Tu herramienta solo consume la API. Si el buscador cambia mientras se mide, la medición no significa nada.  
> * **\[Nunca\] No inventen casos con imágenes del propio catálogo.** Es el error que ya arruinó la evaluación anterior del proyecto.  
> * **\[Con IA\] Usen IA todo lo que quieran, y anoten cada prompt en AI\_LOG.md.** Como en los hitos anteriores. No se acepta código que ninguno de los dos pueda explicar: qué recibe, qué devuelve y por qué está ahí.  
> * **\[Si se traban\] Más de 40 minutos atascados en lo mismo: escriban al coordinador.** Con qué intentaron y qué error sale. Trabarse es normal; trabarse en silencio tres días no.

## **05 · Informe diario**

Al final de cada día, cuatro líneas al grupo. Ni una más:  
*1\. Qué quedó funcionando hoy.*  
*2\. Qué no salió y por qué.*  
*3\. Cuánto tiempo se fue en lo que más costó.*  
*4\. Qué necesitan de otro para poder seguir mañana.*

## ---

**06 · Qué sigue después de esto**

> * **Si la herramienta funciona el lunes:** entran los 180 casos de los diseñadores y sale el primer número honesto del proyecto. Esa medición decide todo lo que viene después.  
> * **Si el número sale sobre 70%:** el motor sirve. Lo siguiente es meterle los diseños propios de Sublitex, que el equipo de diseño está exportando ahora mismo.  
> * **Si sale bajo 50%:** el motor no está listo, y lo siguiente es arreglarlo — con la ventaja de que ya tenemos una forma de saber si lo estamos mejorando o solo moviendo.  
> * **Esta herramienta no se tira nunca.** Cada vez que alguien toque el buscador, se vuelve a pasar el examen con ella. Es el instrumento de medida del proyecto, y por eso importa más que sea confiable a que sea bonita.

---

*Sublitex · Biblioteca visual · Ficha 03-A · Evaluador · Versión 1.0 · Entrega: lunes, revisión en vivo*  
