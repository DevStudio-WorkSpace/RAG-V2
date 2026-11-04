# Monitoreo del despliegue

## Señales y umbrales iniciales

Los umbrales son valores iniciales para una demo privada; ajústalos con una
línea base real antes de usarlos como SLO de producción.

| Señal | Qué observar | Umbral inicial sugerido |
| --- | --- | --- |
| API `/health` | `GET /health` debe responder HTTP 200 y devolver `desfase_detectado: false`. | Comprobar cada minuto; alertar al primer fallo. |
| Búsqueda de imágenes | Latencia p95 de `POST /search/image`, separando `clip` y `fusion` si se usan ambos. | Investigar si el p95 supera 10 s durante 5 minutos; fijar el SLO tras medir la carga real. |
| Errores HTTP | Proporción y cantidad de respuestas 5xx de API/proxy. | Alertar si supera 1 % durante 5 minutos o hay más de 5 errores en 5 minutos. |
| API: RAM y CPU | Uso del contenedor API y límites efectivos del host. Como referencia, se han observado unos 2,6 GB de RAM bajo carga; Compose declara un límite de 4 GB. | Avisar sobre 3,2 GB de RAM (80 % del límite) o 80 % de CPU durante 5 minutos. |
| Disco | Espacio ocupado y libre donde residen `data/` y `qdrant_data/`. | Avisar al 80 % de uso y escalar al 90 %. |
| Qdrant | Que el servicio responda en su endpoint de readiness y que la colección esté disponible. | Alertar si readiness falla durante dos comprobaciones consecutivas. |

Uptime Kuma es una opción liviana para disponibilidad HTTP y notificaciones. No
calcula por sí solo el p95 de búsquedas ni las métricas de CPU, RAM o disco:
esas señales requieren métricas del proxy/servidor o una herramienta de
observabilidad adicional. El healthcheck que ya tiene Compose solo comprueba
el código HTTP de `/health`; no comprueba el campo `desfase_detectado` ni
Qdrant.

## Ejecutar Uptime Kuma

El servicio adicional está definido en `docker-compose.monitoring.yml` y usa
`louislam/uptime-kuma:2.5.9`, versión estable fijada para que los despliegues no
varíen al descargar una etiqueta flotante como `latest`. Los datos se guardan
en el volumen nombrado `uptime_kuma_data`.

Desde la raíz del proyecto en el servidor:

```bash
docker compose -f docker-compose.monitoring.yml up -d
```

El puerto 3001 se enlaza únicamente a `127.0.0.1`; no abras ese puerto en el
firewall ni lo publiques en Internet. Para acceder desde tu equipo, crea un
túnel SSH:

```bash
ssh -L 3001:127.0.0.1:3001 usuario@servidor
```

Después abre `http://127.0.0.1:3001` localmente. Si se integra en un proxy,
mantén el acceso autenticado y restringido a la red interna; nunca publiques
directamente el puerto de Kuma.

Para monitorizar los servicios por sus nombres internos, conecta Kuma a las
redes Compose existentes. Identifica los nombres con `docker network ls` y
conecta el contenedor a `<proyecto>_frontend_net` (API) y, para vigilar
Qdrant, a `<proyecto>_backend`:

```bash
docker network connect <proyecto>_frontend_net sublitex_uptime_kuma
docker network connect <proyecto>_backend sublitex_uptime_kuma
```

En Kuma configura una comprobación HTTP de `http://api:8000/health` cada minuto
y valida tanto el estado 200 como que el JSON contenga
`"desfase_detectado":false` (monitor JSON/consulta JSON). Para Qdrant usa
`http://qdrant:6333/readyz` desde la red interna. No guardes una clave de
administrador de la API en Kuma para estas comprobaciones públicas de readiness.
Uptime Kuma no mide el p95 de `POST /search/image`; obtén ese percentil de las
métricas del proxy o de una herramienta de métricas.

## Alertas y comprobación periódica por script

Uptime Kuma permite configurar notificaciones desde **Settings →
Notifications**. Elige un proveedor (por ejemplo, Discord o Telegram), pega su
webhook/token directamente en la configuración privada de Kuma y envía una
notificación de prueba. No guardes credenciales en este documento ni en Git.

Como alternativa, `scripts/health_alert.py` consulta el endpoint de salud y
envía una notificación solo al cambiar entre OK y falla. Configura las
variables indicadas en `.env.example` en el entorno del usuario que ejecutará
el proceso. Puede programarse con cron cada 1–5 minutos:

```cron
*/2 * * * * cd /ruta/al/proyecto && /usr/bin/python3 scripts/health_alert.py
```

O mediante un `systemd timer` que active un servicio oneshot con la misma
frecuencia. Mantén las variables y el archivo de estado accesibles solo para
ese usuario; nunca imprimas ni registres la URL del webhook.

## Estado de verificación

El archivo Compose de monitoreo se debe validar con Docker Compose y probar en
el VPS antes de marcar Monitoreo como completado. Si Docker no está disponible
en el entorno de desarrollo, una validación de sintaxis YAML no sustituye esa
prueba operativa.
