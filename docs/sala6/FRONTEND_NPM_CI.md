# Frontend: instalación reproducible y conexión con API

Fecha: 2026-11-05. Base actualizada a `dfb3005d`. Tareas §3.4 y verificación local del flujo de §3.5.

## Cambios

Se incorporaron `frontend/package-lock.json` y el Dockerfile de la rama del compañero `origin/chore/npm-ci`, commit `0f41d2fa`. El `package.json` de esa rama coincide con el actual. Se exige el lockfile al copiar y se ejecuta `npm ci` en lugar de `npm install`; la versión del lockfile es 3 y sus dependencias normales/de desarrollo coinciden con el manifiesto.

No se cambiaron la interfaz ni las versiones declaradas para resolver avisos de dependencias. El aporte se incluye en la entrega de frontend de Sala 6, con los límites y las evidencias registrados abajo.

## Verificación realizada

| Comprobación | Resultado |
| --- | --- |
| `npm ci` dentro del build Docker | Correcto; 372 paquetes instalados |
| Build Next.js y TypeScript | Correctos |
| `npm run lint`, sobre los archivos actuales en contenedor temporal | 0 errores, 4 advertencias por variables sin usar |
| Verificador de integración | 17/17 correcto, con código backend actual |
| Imagen real desde Windows a `/api/search` de la VM | HTTP 200; backend Qdrant; Top 1 `SBX-01-0001` |
| Archivos JavaScript enviados al navegador | Usan `/api/search`; sin acceso directo a localhost/127.0.0.1:8000 ni clave de cliente incluida |
| URL de API dentro del servidor Next.js | `http://api:8000`, nombre interno Docker |

Evidencia: [frontend-2026-11-05.json](../evidencias/frontend-2026-11-05.json).

El recorrido comprobado fue Windows → túnel SSH en puerto 8080 → Caddy → Next.js `/api/search` → FastAPI → Qdrant. `localhost:8080` es la entrada al túnel, no una API que deba instalarse en el equipo del usuario. Las claves permanecen del lado del servidor.

## Cómo repetir

Desde la raíz del proyecto en un equipo con Docker y configuración de datos/secretos preparada:

```bash
docker compose -p ragv2staging -f docker-compose.yml -f docker-compose.staging.yml build frontend
docker compose -p ragv2staging -f docker-compose.yml -f docker-compose.staging.yml up -d --no-build --wait
docker compose -p ragv2staging -f docker-compose.yml -f docker-compose.staging.yml exec -T api python scripts/verificar_staging.py
```

Estos comandos asumen que la imagen backend ya contiene el código vigente. Si se modifica, debe prepararse su imagen antes de usar `--no-build`.

## Límites y pendientes separados

- La imagen del frontend se construyó con su Dockerfile normal y `npm ci` efectivamente ejecutado. El backend se probó con sus dependencias previamente verificadas y código API/core/scripts actualizado. Su nueva dependencia explícita httpx ya estaba instalada en versión 0.28.1, dentro del rango requerido. La reconstrucción completa del backend desde una base nueva se canceló para evitar agotar el disco de la VM; no se declara verificado ese build limpio.
- npm reportó 9 vulnerabilidades (8 moderadas y 1 crítica). Revisarlas es una tarea separada antes de publicar; no se ejecutó `npm audit fix --force`.
- Falta repetir el acceso con dominio/HTTPS y dispositivo externo del despliegue final. La prueba actual fue desde Windows a una VM independiente por túnel, mediante curl y revisión del bundle; no se ejecutó automatización de navegador.
- Los tiempos son muestras individuales, no percentiles de rendimiento. La VM tiene recursos limitados.
