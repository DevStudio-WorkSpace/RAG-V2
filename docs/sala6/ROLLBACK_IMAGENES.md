# Rollback de imágenes de API y frontend

Esta guía documenta cómo volver a imágenes Docker locales anteriores. El rollback de imágenes no revierte cambios de datos ni de esquema de Qdrant. No usar `docker compose down` ni `down -v` durante este procedimiento.

## Requisitos

- Ejecutar primero en staging y confirmar Qdrant sano.
- Usar tags únicos guardados localmente para API y frontend.
- Preservar las demás variables al cambiar `APP_IMAGE_TAG` en el `.env` privado.
- Aplicar solo API/frontend con `--no-deps`; así Compose no reconcilia Qdrant ni el proxy.

## Guardar la versión actual

Con los contenedores sanos, desde la raíz del proyecto:

```bash
PREVIOUS_TAG=estable-AAAA-MM-DD

docker image tag "$(docker inspect --format='{{.Image}}' sublitex_api)" "sublitex_api:${PREVIOUS_TAG}"
docker image tag "$(docker inspect --format='{{.Image}}' sublitex_frontend)" "sublitex_frontend:${PREVIOUS_TAG}"
docker image inspect "sublitex_api:${PREVIOUS_TAG}" "sublitex_frontend:${PREVIOUS_TAG}" --format '{{.RepoTags}} {{.Id}}'
```

Si no se encuentran ambas imágenes, detenerse y confirmar los nombres/IDs de los contenedores antes de reconstruir o desplegar.

## Volver a un tag anterior

1. Confirmar que ambos tags existen y que esa versión es compatible con los datos actuales.
2. Cambiar solo `APP_IMAGE_TAG` en el `.env` privado al tag anterior.
3. Aplicar y revisar:

```bash
docker compose config -q
docker compose up -d --no-build --pull never --no-deps api frontend
docker compose ps
docker compose logs --tail=50 api frontend
```

4. Verificar `GET /api/health` con HTTP 200 y `desfase_detectado=false`; abrir la interfaz y ejecutar una búsqueda conocida.
5. Registrar fecha, tag/IDs de imagen, resultado de salud y búsqueda. No guardar ni compartir `.env` o claves.

Si la versión nueva modificó datos de forma incompatible, detener la API y usar solo un procedimiento de restauración de backup/snapshot previamente validado para ese entorno.

## Simulacro ejecutado en VirtualBox (2026-11-09)

Se alternó entre tags `rollback-base` y `rollback-candidate` usando las imágenes locales ya disponibles. `docker compose config -q` pasó; API y frontend quedaron healthy; `/api/health` respondió 200 con 577 productos y 577 embeddings, sin desfase; una búsqueda exacta de `SBX-01-0001` devolvió ese mismo Top 1 en ambos tags. En la secuencia final con `--no-deps`, Qdrant conservó ID, hora de inicio y bind mount. Los servicios quedaron en `rollback-candidate` healthy.

En una primera aplicación sin `--no-deps`, Compose recreó Qdrant; el almacenamiento persistió y el servicio se recuperó, pero se repitió la prueba con `--no-deps` para evitar esa reconciliación. Este simulacro valida rollback de imágenes y preservación del contenedor/datos de staging; no valida restauración de backups, producción ni compatibilidad ante cambios de esquema.

Evidencia detallada y sanitizada: [rollback-2026-11-09.txt](../evidencias/rollback-2026-11-09.txt).
