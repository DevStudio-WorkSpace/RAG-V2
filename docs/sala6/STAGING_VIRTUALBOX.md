# Copia de pruebas en VirtualBox

## Qué significa para otros equipos

VirtualBox aloja el entorno Linux de pruebas y SSH permite administrarlo y abrir un túnel. Ninguno participa en el cálculo de similitud. No son dependencias del buscador: un compañero con Docker puede ejecutar el mismo stack directamente en su equipo Linux o en otro entorno compatible, sin SSH ni VirtualBox.

Para reproducir el comportamiento deben coincidir código, catálogo, IDs, índices, pesos del modelo, imagen consultada, modelo seleccionado, modo de búsqueda y preprocesamiento. Las variables de entorno deben ser equivalentes; las claves pueden ser distintas. Usar CLIP y los modos original/auto para repetir las pruebas verificadas. CLIP es el modelo canónico y predeterminado de la interfaz y la API.

Se espera el mismo comportamiento funcional bajo esas condiciones, pero no se garantiza igualdad exacta de scores, orden de empates o tiempos entre equipos. Las dependencias aún no están completamente fijadas (falta lockfile del frontend y hay rangos en requirements), por lo que un nuevo build puede resolver versiones diferentes. Ejecutar los mismos contenedores ya construidos reduce esa variación. La ejecución nativa sin Docker también requiere validar versiones y dependencias: no fue probada en esta sesión.

Si Docker está en el equipo del compañero, puede usar el complemento staging y abrir directamente `http://localhost:8080`; no necesita túnel. Debe preparar su propio .env, los datos y permisos indicados abajo. Si usa solo docker-compose.yml, cambian puertos, límites, precarga y persistencia de caché; las pruebas registradas corresponden al complemento de staging. El script usa nombres internos de servicios Docker y está pensado para ejecutarse dentro del contenedor API.

**Mención para el equipo:** se validó una copia de Sala 6 en Ubuntu/Docker, administrada por SSH dentro de VirtualBox. Pasaron 17/17 pruebas básicas con CLIP y una consulta exacta recuperó el ID correcto por los flujos original, auto y Qdrant. Esto acredita esa configuración; cada equipo debe repetir el verificador y no extrapolarlo a Fusión, producción o calidad sobre todo el banco.

## Resultado verificado — 2026-11-04

Build de API y frontend completado; stack iniciado; 17/17 comprobaciones de integración correctas. Catálogo de 577 productos e IDs alineados; cuatro matrices con dimensiones esperadas, valores finitos y vectores no nulos. API saludable, interfaz e imágenes accesibles, autorización y errores comprobados. Sin archivo devuelve 400 en los tres endpoints de búsqueda.

La consulta exacta SBX-01-0001 recuperó ese ID en Top 1 por el flujo original, auto y Qdrant. Se indexaron 577 puntos en la colección de prueba. Curl con una imagen real de data/consultas respondió 200. Evidencia: [staging-2026-11-04.json](../evidencias/staging-2026-11-04.json).

Mediciones individuales: original 1,066 s; auto 19,93 s en el verificador final y 7,75 s en otra llamada curl. Son muestras aisladas, no p50/p95. Fusión no se probó. La instalación npm reportó 17 vulnerabilidades (16 moderadas, 1 crítica); falta analizar el informe completo y resolver las aplicables antes de producción. Quedan unos 7 GB libres en la VM tras construir: vigilar el espacio antes de nuevas imágenes o respaldos.

## Medición inicial p50/p95 — 2026-11-11

En la copia staging con imágenes `rollback-candidate` y Qdrant 1.20 se usó el medidor existente desde el contenedor API: 10 solicitudes medidas a `/search/image`, CLIP (`modelo=clip`, `modo=auto`), concurrencia 1, una solicitud de calentamiento y timeout de 90 s; consulta `data/consultas/SBX-01-0001_exacta.jpg`. El script recibió 8 respuestas HTTP 200 y registró 2 `ReadTimeout` del cliente (solicitudes 3 y 10). Sobre las 8 respuestas recibidas informó p50 5898.3 ms, p95 9766.8 ms y throughput 0.03 solicitudes/s. Evidencia: [latencia-staging-2026-11-11.txt](../evidencias/latencia-staging-2026-11-11.txt).

Es una medición real y reproducible de una carga secuencial corta, no una caracterización multiusuario ni un SLO: la muestra de éxitos es pequeña y los timeouts forman parte del resultado operativo. API y Qdrant quedaron saludables; el API conservó un reinicio previo de una corrida simultánea, sin OOM. Repetir con más muestras y concurrencia gradual antes de definir objetivos de latencia.

Se corrigieron dos problemas descubiertos al ejecutar: caché Hugging Face sin permisos para appuser (Dockerfile crea ahora su directorio antes del chown; también se verificó un volumen nuevo escribible) y peticiones sin archivo que devolvían 422. Las correcciones están en Windows y en la copia de pruebas, sin commit.

## Ubicación y acceso

- VM: Ubuntu-Docker; usuario SSH: vboxuser.
- SSH desde Windows: `ssh -p 2222 vboxuser@127.0.0.1`.
- Proyecto aislado: `/home/vboxuser/Desktop/TRABAJOS/RAG-V2-staging`.
- Copia inicial: commit `7e6b42c218e01065fe11d03138f5b69822067a92` más los cambios locales sin commit al transferir. No es un checkout Git.
- Manifiesto de transferencia: `/home/vboxuser/Desktop/TRABAJOS/virtualbox-staging-manifest.json`.
- Se excluyeron secretos, dependencias locales, historial Git y consultas subidas por usuarios. Se copiaron catálogo, índices, imágenes normalizadas y consultas de prueba.
- `.env` se generó dentro de la VM con tres claves aleatorias distintas y permisos 600; no copiarlo a Git ni a imágenes.

## Arranque

Desde la carpeta del proyecto en la VM:

```bash
docker compose -p ragv2staging -f docker-compose.yml -f docker-compose.staging.yml config -q
docker compose -p ragv2staging -f docker-compose.yml -f docker-compose.staging.yml up -d --build
docker compose -p ragv2staging -f docker-compose.yml -f docker-compose.staging.yml ps
```

El complemento de staging reduce límites para 2 CPU, mantiene caché de modelos en un volumen y publica HTTP exclusivamente en `127.0.0.1:8080` dentro de la VM. Usa Compose con soporte de `!override` (en la VM se verificó Compose v5.5.1). Los nombres de contenedores siguen siendo los del Compose principal: no iniciar otra copia de ese stack simultáneamente en el mismo Docker.

`PRELOAD_EXTRA_MODELS=false` evita precalentar OpenCLIP y SigLIP. No desactiva su selección manual: en esta VM de 3,3 GiB probar explícitamente CLIP. Para Fusión aumentar memoria y medir consumo. La configuración original mantiene su comportamiento de precarga por defecto.

La API necesita escribir en `data/queries_original` y `data/queries_procesadas`: en la copia de staging sus directorios deben pertenecer al UID/GID 10001 del contenedor. No cambiar permisos del catálogo original de Windows.

## Abrir desde Windows

Mantener abierto este túnel en PowerShell:

```powershell
ssh -p 2222 -L 8080:127.0.0.1:8080 vboxuser@127.0.0.1
```

Abrir `http://localhost:8080`. El túnel requiere que la VM siga encendida y el stack esté iniciado. Se mantiene HTTP solo para esta prueba local; no demuestra HTTPS de producción.

## Verificación

```bash
docker compose -p ragv2staging -f docker-compose.yml -f docker-compose.staging.yml exec -T api python scripts/verificar_staging.py
```

El verificador comprueba datos/IDs, salud, interfaz, autorización, manejo de errores, búsquedas original/auto con CLIP e imágenes servidas por frontend. Genera consultas locales de prueba, sin modificar catálogo o índices. Una búsqueda exacta no reemplaza la evaluación de 50 consultas ni la prueba con imágenes externas. La ejecución inicial no incluyó rollback/restauración; el rollback por tags se probó el 2026-11-09, ver [evidencia](../evidencias/rollback-2026-11-09.txt). La restauración de backup sigue pendiente.

Para guardar evidencias, redirigir la salida a un archivo dentro de `evidence/` en la VM. Los logs de la preparación inicial están allí: `build-original.log` y `start-and-tests.log`. No publicar logs o configuraciones que contengan secretos.

## Detener

```bash
docker compose -p ragv2staging -f docker-compose.yml -f docker-compose.staging.yml stop
```

La copia no se sincroniza automáticamente: los cambios posteriores de Windows deben transferirse y reconstruirse. No usar `down -v` para mantenimiento normal, ya que borra volúmenes nombrados.
