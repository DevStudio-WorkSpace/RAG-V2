# Pruebas manuales del frontend

Entorno: Windows, navegador integrado, frontend de VirtualBox accesible por túnel SSH en `http://localhost:8080/search`. Fecha de registro inicial: 2026-11-06. Estas pruebas complementan las de integración; no certifican publicación, HTTPS ni calidad sobre las 50 consultas.

- [x] Búsqueda conocida: captura aportada por el usuario. Consulta `sbx-01-0001.jpg`, motor mostrado CLIP + Qdrant; resultado único, posición 1, ID `SBX-01-0001`, imagen coincidente y score de similitud 0.8755. La captura acredita resultado y visualización, no el estado durante la espera. [Evidencia](../evidencias/frontend-manual-2026-11-06.png).
- [x] Estado de carga visible: captura del usuario con botón “Analizando diseño…”, mensaje “Comparando con toda la colección del catálogo…” y tarjetas provisionales. [Evidencia](../evidencias/frontend-carga-2026-11-06.png).
- [x] Reactivación al finalizar y presentación de resultados: confirmado por el usuario el 2026-11-06.
  - Confirmación adicional del usuario tras instalar el bloqueo: capturas de [búsqueda en curso](../evidencias/frontend-bloqueo-usuario-2026-11-06.png) y [resultado final](../evidencias/frontend-confirmacion-usuario-2026-11-06.png). Se observan controles atenuados durante carga, botones Buscar/Cambiar habilitados al finalizar y Top 1 SBX-01-0001 con score de similitud 0.8755. Esto cierra la prueba de bloqueo temporal y recuperación normal; las comprobaciones posteriores de Ctrl+V y arrastre se registran por separado abajo.
- [x] Muestras, botón Buscar, Cambiar y selector de archivos bloqueados durante la petición: verificado en navegador el 2026-11-06 tras la corrección. Las seis muestras y el input estaban deshabilitados; se reactivaron al finalizar y tras error de conexión. Se utiliza bloqueo síncrono compartido para impedir entradas repetidas antes del siguiente render.
- [x] Arrastre durante búsqueda bloqueado: usuario indica que no permite adjuntar otra imagen; captura muestra archivo arrastrado con símbolo de prohibición sobre la consulta actual mientras procesa. La consulta visible se mantiene y no se observa navegación al archivo. [Evidencia](../evidencias/frontend-arrastre-bloqueado-2026-11-06.png).
- [x] Ctrl+V durante búsqueda bloqueado: confirmación explícita del usuario el 2026-11-06 de que también intentó pegar otra imagen durante carga y se conservó la consulta actual. Evidencia por declaración del usuario, sin captura específica de la interacción del portapapeles.
- [x] Nueva búsqueda: usuario selecciona SBX-01-0006 tras la consulta anterior; captura muestra nueva imagen, bloqueo y tarjetas provisionales, seguida de nuevos resultados. El usuario confirma reactivación de la selección. Evidencias de [carga](../evidencias/frontend-nueva-consulta-carga-2026-11-06.png) y [respuesta](../evidencias/frontend-nueva-consulta-resultado-2026-11-06.png). Aprobado el flujo de interfaz; la exactitud del orden se registra aparte.
- [x] Rechazo de archivo inválido con mensaje visible: usuario confirma que no permite cargarlo; captura muestra “Por favor sube un archivo de imagen válido (JPG, PNG o WEBP)” y la zona de carga disponible. [Evidencia](../evidencias/frontend-archivo-invalido-2026-11-06.png). La captura no identifica la extensión del archivo intentado.
- [x] Recuperación tras archivo inválido: el 2026-11-09, después del mensaje de rechazo, el usuario cargó `SBX-01-0010_sin_marco.jpg` y completó la búsqueda sin recargar. Resultado Top 1 `SBX-01-0010`, score 0.9454. Evidencia: captura del usuario del 2026-11-09.
- [x] Imagen inferior a 32 px: captura del usuario muestra rechazo de `tiny-16.png` con mensaje “La imagen es demasiado pequeña (16x16); se requiere un mínimo de 32px por lado para una búsqueda fiable.” Botones Buscar/Cambiar disponibles. [Evidencia](../evidencias/frontend-imagen-pequena-2026-11-06.png). Fixture: `evaluation/fixtures/tiny-16.png`.
- [x] Recuperación tras imagen pequeña: usuario confirma el 2026-11-06 que pulsó Cambiar, adjuntó una foto válida y completó la búsqueda. La captura muestra nueva imagen de consulta, cinco resultados anunciados, botones habilitados y ausencia del error anterior; visibles SBX-03-0006 y SBX-03-0008. Se registra su confirmación y observación, sin copiar esta captura que también incluye pestañas ajenas a la prueba.
- [x] Imagen externa: usuario adjunta foto de persona con camiseta, observa carga y luego resultados. La interfaz anuncia 5 resultados; la captura permite ver SBX-03-0006 primero (0.7491) y SBX-03-0008 segundo (0.7464). No se conoce id_correcto ni se ven las cinco tarjetas, por lo que no se certifican exactitud ni calidad completa. Evidencias de [carga](../evidencias/frontend-foto-externa-carga-2026-11-06.png) y [respuesta](../evidencias/frontend-foto-externa-resultado-2026-11-06.png).
- [x] Fallo de conexión y recuperación: parada breve controlada de API en staging, mensaje de error visible y controles habilitados; API restaurada y reintento correcto con Top 1 SBX-01-0001. Verificado en navegador el 2026-11-06.
- [x] Adaptación a pantalla estrecha sin controles importantes cortados. Revisada el 2026-11-09 a 360×800, 390×844 y 768×900: contenido apilado en 360/390 px y dos columnas a 768 px; no se observaron cortes. A 360 px se observó la carga y resultado Top 1 SBX-01-0002 (0.8508), y el error de `tiny-16.png` (16×16) completo y legible. [Evidencia del error a 360 px](../evidencias/frontend-error-mobile-360-2026-11-09.png). Una búsqueda tardó más de lo esperado; `/api/health` respondió 200. La captura muestra el error; para volver al botón Cambiar se desplaza hacia arriba.
- [ ] Prueba en celular real con acceso de red preparado.
<<<<<<< HEAD
- [x] Respuesta sin resultados, con un caso controlado. Verificado el 2026-11-13 en el build de producción del frontend con un upstream controlado que responde `200 {"resultados": []}` (mismo contrato que la API cuando no hay coincidencias). Se observó el panel «Sin resultados para esta imagen» con explicación, sugerencias y botones «Reintentar búsqueda» / «Probar con otra imagen»; sin tarjetas ni encabezado de resultados. El motor real no devolvió 0 resultados con cinco imágenes no relacionadas (paisaje sintético, captura de UI, negro, blanco y ruido): la normalización min-max del score de embeddings fija un piso cercano a 0.50 y el umbral absoluto es 0.40. [Captura](../evidencias/frontend-sin-resultados-2026-11-13.png) · [árbol visible](../evidencias/frontend-sin-resultados-2026-11-13.txt) · [detalle del método](../evidencias/frontend-estados-controlados-2026-11-13.txt).
- [x] Tiempo agotado, con un caso controlado. Verificado el 2026-11-13 contra la API real local (CLIP + Qdrant con 577 puntos) arrancando el frontend con `SEARCH_TIMEOUT_MS=4000`: la búsqueda real tarda ~10–30 s y el proxy devuelve 504 `code=timeout`. Se observó «Tiempo de espera agotado», el mensaje con el presupuesto de 4 segundos, la imagen de consulta conservada y los botones «Reintentar búsqueda» / «Elegir otra imagen», sin resultados parciales. Una consulta normal con timeout por defecto siguió devolviendo Top 1 `SBX-01-0001`. [Captura](../evidencias/frontend-timeout-2026-11-13.png) · [árbol visible](../evidencias/frontend-timeout-2026-11-13.txt) · [resultado real de control](../evidencias/frontend-resultado-real-2026-11-13.png).
=======
- [x] Respuesta sin resultados controlada (2026-11-09): frontend local de producción apuntado a un stub aislado en `127.0.0.1:8765`, que respondió HTTP 200 con `{"resultados":[]}`. Al seleccionar la primera muestra, la interfaz terminó la carga y el árbol accesible mostró “No encontramos coincidencias”, el texto para probar otra imagen y el botón “Probar otra imagen”; no apareció estado de error. No se consultó la API real ni se evaluó el ranking. [Registro reproducible de la observación](../evidencias/frontend-sin-resultados-2026-11-09.txt).
- [ ] Tiempo agotado, con un caso controlado.
>>>>>>> 96994780732963df20c3417993b6dbf768fe9256

Cada casilla requiere resultado observado y evidencia. Las pruebas automáticas anteriores de errores de API no sustituyen la comprobación visual del mensaje en el navegador. No se identifican navegador/versiones o dispositivo móvil que la evidencia no demuestre.

## Siguiente paso de frontend

### Validación del catálogo integrado — 2026-11-06

Se transfirió el frontend del commit `705e1fa6` a la copia de VirtualBox, se
construyó su imagen (build/TypeScript correctos) y se recreó únicamente el servicio
frontend. Corre con UID 1000 (`node`) y su healthcheck quedó saludable. No se
reconstruyó la API ni se validaron los nuevos ajustes de HTTPS/proxy o las nuevas
versiones de requirements.txt. La prueba utiliza el proxy HTTP que ya estaba
ejecutándose y el túnel local de staging.

- [x] `/api/catalog` responde 200: 577 productos y 577 IDs únicos; todos los registros y su orden coinciden con el CSV local, comparando ID, nombre, imagen, proveedor y URL.
- [x] Las seis imágenes de muestra responden 200 con tipo `image/png`; en navegador se comprobaron cargadas, con ancho natural de 2000 px.
- [x] Catálogo con 577 modelos y paginación a la página 2; filtro por SBX-01-0001 reduce a un modelo y vuelve a página 1.
- [x] Ficha del catálogo abre el modelo filtrado. El enlace «Ver producto» coincide con la URL del CSV. No se comprobó un destino comercial real.
- [x] «Buscar Similares» lleva al buscador. La muestra SBX-01-0001 bloquea controles mientras procesa, devuelve ese ID en Top 1 (0.8755) y los reactiva al terminar.
- [x] «Ver modelo» desde ese resultado abre la ficha de SBX-01-0001 y puede cerrarse.
- [x] Petición curl al proxy `/api/search` con `data/consultas/SBX-01-0010_sin_marco.jpg`, CLIP/auto: 200 y Top 1 SBX-01-0010 (0.7749).
- [ ] Sustituir URLs de ejemplo por destinos reales acordados por el equipo: el enlace comprobado apunta a `https://ejemplo.com/SBX-01-0001`.
- [x] Precios sin definir corregidos: resultado y fichas de búsqueda/catálogo muestran «A consultar» en las siete ubicaciones afectadas. Verificado en navegador con SBX-01-0003 tras reconstruir frontend; build/TypeScript correctos, lint sin errores (una advertencia previa en app.js), servicio saludable y curl de búsqueda 200. [Captura de ficha corregida](../evidencias/precios-corregidos-2026-11-06.png); árboles visibles de [resultado](../evidencias/precios-resultado-2026-11-06.txt), [ficha de búsqueda](../evidencias/precios-ficha-2026-11-06.txt) y [ficha de catálogo](../evidencias/precios-catalogo-2026-11-06.txt).

Evidencias: [comparación e imágenes](../evidencias/catalogo-2026-11-06.json),
[respuesta de búsqueda](../evidencias/catalogo-busqueda-2026-11-06.json),
[recorrido observado](../evidencias/catalogo-recorrido-2026-11-06.txt) y
[detalle observado](../evidencias/catalogo-detalle-2026-11-06.txt).
El navegador no pudo generar capturas en esta ejecución; los TXT registran su
árbol visible, no son capturas de pantalla. No se inspeccionaron visualmente los
577 modelos ni se certificó calidad global del ranking.

Revisar la adaptación a pantallas estrechas antes de pasar a un celular real.
Comprobar, por ejemplo, anchos de 360, 390 y 768 píxeles: que no haya desbordamiento
horizontal, que muestras, selector, botones y mensajes puedan usarse y que los
resultados sigan legibles. Probar carga, error y resultado, no solo la pantalla inicial.
Registrar capturas y corregir únicamente los problemas observados; simular un ancho
no sustituye la prueba en teléfono real. Estas comprobaciones aún no se realizaron.

## Observaciones de interpretación

- Estado sin resultados: el motor no devolvió 0 resultados con cinco imágenes no relacionadas (2026-11-13). La normalización min-max del score de embeddings asigna 1.0 al mejor candidato y el embedding pesa 0.50, por lo que el piso del score final es ~0.50 y el umbral absoluto `UMBRAL_MINIMO_SIMILARIDAD=0.40` no filtra mientras Qdrant devuelva candidatos. El panel «Sin resultados» queda como defensa de interfaz y solo se alcanzaría si la recuperación devuelve cero candidatos. Revisar la calibración del umbral con las 50 consultas antes de asumir que el motor puede responder vacío; no se modificó el motor en esta tarea.

- Calidad de ranking pendiente: consulta de muestra SBX-01-0006. La captura final muestra 3 resultados anunciados, con SBX-02-0149 primero (0.7838) y la coincidencia SBX-01-0006 segunda (0.5731). La tercera tarjeta no es visible en la captura. La coincidencia correcta aparece en Top 5 pero no en Top 1; investigar en la evaluación del motor/preprocesamiento. No se atribuye a la interfaz ni se declara validada la calidad por aprobar el ciclo de carga.

- Corregido el riesgo de respuestas superpuestas bloqueando nuevas entradas hasta finalizar. También se limpian los resultados anteriores al iniciar y se libera el bloqueo con `finally`. Se verificaron búsquedas de SBX-01-0001 y SBX-01-0002, reactivación de controles y recuperación tras fallo. [Controles durante la petición](../evidencias/frontend-bloqueado-2026-11-06.png) y [resultado tras reintentar](../evidencias/frontend-bloqueo-resultado-2026-11-06.png). Build Next.js/TypeScript correcto; lint 0 errores y 4 advertencias preexistentes. El texto “Listo para buscar” conserva su significado de imagen disponible.

- El usuario aclara que “Listo para buscar” pertenece al estado de la imagen cargada, no al progreso de la petición. Bajo esa interpretación es válido mantenerlo: la imagen continúa disponible durante y después de la búsqueda. Se retira su clasificación anterior como fallo pendiente. Una etiqueta más explícita sería una mejora opcional de claridad, no un requisito para aprobar la prueba; no se modificó la interfaz.
