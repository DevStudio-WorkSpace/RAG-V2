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
- [ ] Recuperación tras archivo inválido: cargar una imagen válida y completar una búsqueda sin recargar la página.
- [x] Imagen inferior a 32 px: captura del usuario muestra rechazo de `tiny-16.png` con mensaje “La imagen es demasiado pequeña (16x16); se requiere un mínimo de 32px por lado para una búsqueda fiable.” Botones Buscar/Cambiar disponibles. [Evidencia](../evidencias/frontend-imagen-pequena-2026-11-06.png). Fixture: `evaluation/fixtures/tiny-16.png`.
- [x] Recuperación tras imagen pequeña: usuario confirma el 2026-11-06 que pulsó Cambiar, adjuntó una foto válida y completó la búsqueda. La captura muestra nueva imagen de consulta, cinco resultados anunciados, botones habilitados y ausencia del error anterior; visibles SBX-03-0006 y SBX-03-0008. Se registra su confirmación y observación, sin copiar esta captura que también incluye pestañas ajenas a la prueba.
- [x] Imagen externa: usuario adjunta foto de persona con camiseta, observa carga y luego resultados. La interfaz anuncia 5 resultados; la captura permite ver SBX-03-0006 primero (0.7491) y SBX-03-0008 segundo (0.7464). No se conoce id_correcto ni se ven las cinco tarjetas, por lo que no se certifican exactitud ni calidad completa. Evidencias de [carga](../evidencias/frontend-foto-externa-carga-2026-11-06.png) y [respuesta](../evidencias/frontend-foto-externa-resultado-2026-11-06.png).
- [x] Fallo de conexión y recuperación: parada breve controlada de API en staging, mensaje de error visible y controles habilitados; API restaurada y reintento correcto con Top 1 SBX-01-0001. Verificado en navegador el 2026-11-06.
- [ ] Adaptación a pantalla estrecha sin controles importantes cortados.
- [ ] Prueba en celular real con acceso de red preparado.
- [ ] Respuesta sin resultados, con un caso controlado.
- [ ] Tiempo agotado, con un caso controlado.

Cada casilla requiere resultado observado y evidencia. Las pruebas automáticas anteriores de errores de API no sustituyen la comprobación visual del mensaje en el navegador. No se identifican navegador/versiones o dispositivo móvil que la evidencia no demuestre.

## Siguiente paso de frontend

Revisar la adaptación a pantallas estrechas antes de pasar a un celular real.
Comprobar, por ejemplo, anchos de 360, 390 y 768 píxeles: que no haya desbordamiento
horizontal, que muestras, selector, botones y mensajes puedan usarse y que los
resultados sigan legibles. Probar carga, error y resultado, no solo la pantalla inicial.
Registrar capturas y corregir únicamente los problemas observados; simular un ancho
no sustituye la prueba en teléfono real. Estas comprobaciones aún no se realizaron.

## Observaciones de interpretación

- Calidad de ranking pendiente: consulta de muestra SBX-01-0006. La captura final muestra 3 resultados anunciados, con SBX-02-0149 primero (0.7838) y la coincidencia SBX-01-0006 segunda (0.5731). La tercera tarjeta no es visible en la captura. La coincidencia correcta aparece en Top 5 pero no en Top 1; investigar en la evaluación del motor/preprocesamiento. No se atribuye a la interfaz ni se declara validada la calidad por aprobar el ciclo de carga.

- Corregido el riesgo de respuestas superpuestas bloqueando nuevas entradas hasta finalizar. También se limpian los resultados anteriores al iniciar y se libera el bloqueo con `finally`. Se verificaron búsquedas de SBX-01-0001 y SBX-01-0002, reactivación de controles y recuperación tras fallo. [Controles durante la petición](../evidencias/frontend-bloqueado-2026-11-06.png) y [resultado tras reintentar](../evidencias/frontend-bloqueo-resultado-2026-11-06.png). Build Next.js/TypeScript correcto; lint 0 errores y 4 advertencias preexistentes. El texto “Listo para buscar” conserva su significado de imagen disponible.

- El usuario aclara que “Listo para buscar” pertenece al estado de la imagen cargada, no al progreso de la petición. Bajo esa interpretación es válido mantenerlo: la imagen continúa disponible durante y después de la búsqueda. Se retira su clasificación anterior como fallo pendiente. Una etiqueta más explícita sería una mejora opcional de claridad, no un requisito para aprobar la prueba; no se modificó la interfaz.
