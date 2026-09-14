El evaluador del buscador
Sublitex · Ficha 03-B · Programación · Entrega: lunes
Esta ficha no dice cómo hacerlo. Dice qué tiene que existir el lunes y exactamente cómo se va a comprobar. El camino lo eligen ustedes.
El problema: el buscador visual reportó 92% de aciertos, pero esa medición se hizo con imágenes que un programa fabricó a partir del propio catálogo. Nadie sabe cuánto acierta de verdad.
Hace falta un instrumento para medirlo con búsquedas reales evaluadas por una persona. Eso es lo que tienen que construir.
01 · Lo que tiene que existir
Una herramienta que le permita a una persona mirar los resultados del buscador, juzgarlos, y obtener un número. Nada más, y nada menos.
Campo
Valor
Por qué
Entrada
Casos
Un conjunto de fotos de camisetas, cada una con el código del diseño del catálogo que es la respuesta correcta.
Proceso
Juicio humano
Por cada foto, alguien mira los 5 resultados del buscador y los califica uno por uno.
Salida
Tres números
Top 1, Top 5 y utilidad del Top 5 — en total y separados por tipo de foto.
Rastro
Un archivo
Cada juicio queda guardado en disco, fila por fila, para poder revisarlo y recalcularlo después.

El criterio de juicio es fijo y no lo deciden ustedes:
Juicio
Significa
Acierto
Es el mismo diseño, aunque cambie el color, el año, el escudo o el sponsor.
Sirve
No es el mismo, pero se lo mostrarías al cliente y lo aceptaría.
No sirve
Es otro diseño.

Y las tres métricas también:
Métrica
Definición
Top 1
% de casos donde el resultado en posición 1 recibió «Acierto».
Top 5
% de casos donde hubo un «Acierto» en cualquiera de las 5 posiciones.
Utilidad
Promedio de cuántos de los 5 recibieron «Acierto» o «Sirve». De 0 a 5.

02 · La prueba de aceptación
El lunes, el coordinador va a hacer esto delante de ustedes, en este orden. Cada punto se cumple o no se cumple. Pruébenlo antes ustedes mismos, con alguien que no haya tocado el código.
Se levanta leyendo solo el README, sin preguntar nada. Si el coordinador tiene que preguntar algo para arrancarlo, este punto no se cumple.
Trae 10 casos propios, ya cargados y listos para evaluar. Los 180 casos de los diseñadores aún no existen. Los 10 suyos son la prueba de que la herramienta funciona de punta a punta.
Ninguna de las 10 fotos sale del catálogo ni de la web de Aimari. Se va a verificar una por una. Una sola foto sacada del catálogo invalida la entrega completa.
Se pueden evaluar los 10 casos sin tocar código ni la consola. Solo con el mouse.
Al cerrar y reabrir el navegador a mitad de camino, lo evaluado sigue estando. Se va a probar exactamente así, sin avisar.
Existe un archivo en disco con una fila por cada juicio emitido. Se va a abrir y contar. Las filas tienen que cuadrar con los clics dados.
Los tres números se muestran, en total y separados por tipo de foto. Sin la separación por tipo, la medición no sirve para decidir nada.
Los números se pueden recalcular desde el archivo guardado. Se borra la pantalla, se recalcula, y tiene que dar lo mismo.
Cada integrante, por separado, explica cómo se calcula el Top 5. Si uno de los dos no lo sabe explicar, la pareja no aprueba aunque todo lo demás funcione.
Existe un AI_LOG.md con los prompts usados. Como en los hitos anteriores.
03 · Lo que ustedes deciden
Estas decisiones son suyas. No hay respuesta correcta esperada, y parte de la revisión es que sepan defender la que tomaron.
Decisión
Detalle
El lenguaje
Lo que sepan. El buscador ya existe y responde por HTTP; su herramienta solo le pregunta.
Cómo se ve
Un caso a la vez, todos en una lista, con teclado, con mouse. Lo que haga que evaluar 180 casos no sea una tortura.
Dónde se guarda
Archivo, base de datos, lo que sea, mientras se pueda abrir y leer sin su ayuda.
Cómo cargan los casos
Una carpeta, un CSV, un formulario. Ustedes eligen el formato — pero anótenlo en el README, porque los 180 casos van a venir después y tienen que entrar por ahí.

04 · Lo único prohibido
[Nunca] No se toca el buscador, ni el índice, ni products.csv, ni los embeddings. La herramienta mide; no modifica lo que mide. Si el buscador cambia mientras se mide, la medición no significa nada.
[Nunca] No se usan imágenes del catálogo como fotos de consulta. Si la pregunta y la respuesta son la misma imagen, el buscador aprueba sin saber nada. Es exactamente el error que hace falta corregir.
[Si se traban] Más de 40 minutos en lo mismo: al coordinador, con lo que intentaron y el error.
05 · Informe diario
Cuatro líneas al final del día. Ni una más:
1. Qué quedó funcionando hoy.
2. Qué no salió y por qué.
3. Qué decisión tomaron y qué descartaron.
4. Qué necesitan de otro para seguir mañana.
06 · Qué sigue después de esto
Si la herramienta pasa la prueba el lunes: entran los 180 casos que arman los diseñadores y sale el primer número honesto del proyecto.
Si el número sale sobre 70%: el motor sirve, y lo siguiente es cargarle los diseños propios de Sublitex.
Si sale bajo 50%: el motor no está listo, y lo siguiente es arreglarlo — ahora con una forma de saber si mejora o solo cambia.
La herramienta no se tira nunca. Cada vez que alguien toque el buscador, se vuelve a pasar el examen con ella.
Sublitex · Biblioteca visual · Ficha 03-B · Evaluador · Versión 1.0 · Entrega: lunes, revisión en vivo
