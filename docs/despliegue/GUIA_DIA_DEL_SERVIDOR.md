# Guía para el día del VPS

Guía de preparación, no evidencia de un despliegue ejecutado. Requiere que el
supervisor entregue VPS, dominio, autorización de uso de los datos y secretos.
Los comandos de ejemplo son para Ubuntu y se ejecutan por SSH desde el VPS.

## 1. Preparar el VPS y la red

1. Confirma la IP pública, acceso SSH y una cuenta administrativa. Conserva el
   acceso SSH antes de activar el firewall.
2. Instala Docker Engine y el plugin Compose desde el repositorio oficial de
   Docker para la versión de Ubuntu del VPS. Comprueba la instalación:

   ```bash
   docker --version
   docker compose version
   ```

3. Configura el DNS A del dominio acordado hacia la IP del VPS. Configura AAAA
   solo si el VPS tiene IPv6 funcional.
4. En el firewall del proveedor permite SSH solo desde las IP administrativas,
   y únicamente TCP 80/443 desde Internet. En Ubuntu, después de confirmar el
   puerto SSH correcto:

   ```bash
   sudo ufw allow OpenSSH
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw deny 3000/tcp
   sudo ufw deny 8000/tcp
   sudo ufw deny 6333/tcp
   sudo ufw deny 6334/tcp
   sudo ufw enable
   sudo ufw status verbose
   ```

   No habilites UFW hasta confirmar que `OpenSSH` coincide con la configuración
   real del VPS. Compose publica Qdrant solo en loopback y no publica
   directamente API/frontend; no cambies esos enlaces a `0.0.0.0`.

## 2. Obtener el código

Clona el repositorio autorizado en el servidor, usando la rama `sala-6`:

```bash
git clone --branch sala-6 --single-branch <URL_DEL_REPOSITORIO> RAG-V2
cd RAG-V2
git status --short --branch
```

Confirma que el checkout esté limpio y que `git branch --show-current` indique
`sala-6`. El archivo `data/products.csv` debe contener los datos comerciales
aprobados antes de comunicar el servicio como producto.

## 3. Crear configuración y secretos

```bash
cp .env.production.example .env
chmod 600 .env
```

Edita `.env` en el VPS: establece el dominio real en `SITE_ADDRESS`,
`CORS_ORIGINS` y `HEALTH_URL`; genera valores aleatorios distintos para
`API_CLIENT_KEY`, `API_ADMIN_KEY` y `QDRANT_API_KEY`. No pegues secretos en
terminales compartidas, tickets, Git ni este documento. Mantén
`ALERT_WEBHOOK_URL` vacía hasta que se apruebe y configure un destino privado.
El puerto del panel de monitoreo tampoco se debe abrir al público.

Antes de arrancar, confirma el DNS y valida la interpolación de Compose sin
imprimir el resultado completo (podría contener secretos):

```bash
getent hosts "$SITE_ADDRESS"
docker compose config --quiet
```

## 4. Construir y arrancar

```bash
docker compose up -d --build
docker compose ps
curl -fsS "https://${SITE_ADDRESS}/api/health"
```

Espera a que API, frontend y Qdrant estén sanos. Caddy necesita que el DNS
resuelva al VPS y que los puertos 80/443 sean accesibles para obtener TLS. No
abras los puertos 3000, 8000, 6333 ni 6334 directamente. Consulta el
[checklist postdespliegue](./CHECKLIST_POST_DESPLIEGUE.md) antes de anunciar el
servicio.

## 5. Backup inicial y operación

Una vez que Qdrant y la API estén sanos, ejecuta el backup en un directorio
nuevo para preservar cualquier copia existente. El script crea snapshot de
Qdrant cuando puede y archiva `data/` y `qdrant_data/`:

```bash
set -a
. ./.env
set +a
bash scripts/backup.sh "backups/inicial-$(date -u +%Y%m%dT%H%M%SZ)"
```

Comprueba que se hayan creado ambos archivos y almacena una copia fuera del
VPS, con acceso restringido. Un archivo generado no demuestra que la
restauración funcione; prueba la restauración en staging antes de depender de
ella.

Configura Uptime Kuma según [MONITOREO.md](./MONITOREO.md), notificaciones
privadas, rotación de logs y un responsable de guardia. Conserva el commit
desplegado, la etiqueta de imagen y las evidencias de las pruebas.
