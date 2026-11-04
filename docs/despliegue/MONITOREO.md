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

Como alternativa, `scripts/health_alert.py` (solo biblioteca estándar, sin
dependencias extra) consulta los endpoints y envía una notificación **solo al
cambiar entre OK y fallo**, incluido el aviso de recuperación. El último estado
se guarda en `ALERT_STATE_FILE` (por defecto `.alert_state.json`, excluido de
Git) para no repetir avisos en cada ejecución.

Variables del bloque «Alertas» de `.env.example`:

| Variable | Función |
| --- | --- |
| `ALERT_WEBHOOK_URL` | Webhook de destino. Vacía: el aviso se escribe en stdout. |
| `ALERT_WEBHOOK_FORMAT` | `generic` (JSON `{"text": ...}`), `discord`, `slack` o `telegram`. |
| `ALERT_TELEGRAM_BOT_TOKEN`, `ALERT_TELEGRAM_CHAT_ID` | Solo para `telegram`. |
| `HEALTH_URL`, `HEALTH_TIMEOUT` | Endpoint vigilado y espera máxima por petición. |
| `ALERT_MIN_PRODUCTS`, `ALERT_MIN_EMBEDDINGS` | Mínimos aceptados en `/health` (0 = no comprobar). |
| `ALERT_MAX_HEALTH_MS` | Latencia máxima de `/health` (0 = no comprobar). |
| `ALERT_QDRANT_READYZ_URL` | Readiness de Qdrant (vacío = no comprobar). |
| `ALERT_SEARCH_URL`, `ALERT_SEARCH_IMAGE` | Búsqueda sintética real (vacío = no comprobar). |
| `ALERT_SEARCH_MODELO`, `ALERT_API_KEY` | Modelo y clave de cliente para la búsqueda sintética. |
| `ALERT_SEARCH_TIMEOUT` | Espera máxima de la búsqueda sintética en segundos (por defecto 120). |
| `ALERT_MAX_SEARCH_MS` | Latencia máxima de la búsqueda (0 = no comprobar). |
| `ALERT_STATE_FILE` | Archivo de estado (por defecto `.alert_state.json`). |

Códigos de salida: `0` todas las comprobaciones OK, `1` alguna falla, `2` error
de configuración, `3` no se pudo entregar la notificación (el estado no se
actualiza y el aviso se reintenta en la siguiente ejecución).

```bash
python3 scripts/health_alert.py --verbose        # comprueba y muestra detalle
python3 scripts/health_alert.py --dry-run        # muestra el aviso sin enviarlo
python3 scripts/health_alert.py --force-notify   # prueba de notificación
```

Programación con cron (cada 2 minutos, con salida a un log local):

```cron
*/2 * * * * cd /ruta/al/proyecto && /usr/bin/python3 scripts/health_alert.py >> /var/log/sublitex_alertas.log 2>&1
```

O con un `systemd timer` cada 2 minutos; el script lee `.env` por sí mismo:

```ini
# /etc/systemd/system/sublitex-alertas.service
[Unit]
Description=Alertas del buscador visual Sublitex

[Service]
Type=oneshot
WorkingDirectory=/ruta/al/proyecto
ExecStart=/usr/bin/python3 scripts/health_alert.py
```

```ini
# /etc/systemd/system/sublitex-alertas.timer
[Unit]
Description=Ejecuta las alertas de Sublitex cada 2 minutos

[Timer]
OnBootSec=2min
OnUnitActiveSec=2min
Unit=sublitex-alertas.service

[Install]
WantedBy=timers.target
```

Mantén las variables y el archivo de estado accesibles solo para ese usuario;
nunca imprimas ni registres la URL del webhook ni el token del bot. El script
redacta esos valores antes de escribir cualquier mensaje.

## Estado de verificación

- 2026-11-04 — `scripts/health_alert.py` probado sin Docker con una API y un
  webhook simulados en local: 52/52 comprobaciones correctas. Cubre silencio en
  el primer arranque OK, alerta por HTTP 500, `desfase_detectado` distinto de
  `false`, mínimos de catálogo, latencia alta, Qdrant sin readiness, búsqueda
  con HTTP 401, aviso único sin duplicados, aviso de recuperación, reintento
  cuando el webhook falla, `--dry-run`, `--force-notify`, carga por `--env-file`,
  errores de configuración y ausencia de secretos en la salida.
- El envío a un canal real (Discord, Slack o Telegram) requiere el webhook o el
  token del equipo: se comprueba una vez con `--force-notify`.
- El archivo Compose de monitoreo se debe validar con Docker Compose y probar en
  el VPS antes de marcar Monitoreo como completado. Si Docker no está disponible
  en el entorno de desarrollo, una validación de sintaxis YAML no sustituye esa
  prueba operativa.
