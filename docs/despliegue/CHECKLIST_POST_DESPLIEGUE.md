# Checklist de verificación postdespliegue

Ejecuta desde la raíz del repositorio en el VPS. Sustituye los placeholders
por datos y una imagen de prueba autorizados. No registres las claves en
capturas ni en logs. Estos pasos preparan la verificación final; no prueban
por sí solos un despliegue.

## Preparación

```bash
set -a
. ./.env
set +a
export QUERY_IMAGE="<RUTA_A_IMAGEN_REAL_AUTORIZADA>"
export EXPECTED_PRODUCT_ID="<ID_ESPERADO>"
```

## Requisitos de la sección 3.5

### Compose y salud

```bash
docker compose config --quiet
docker compose ps
curl -fsS "https://${SITE_ADDRESS}/backend/health" |
  python3 -c 'import json,sys; d=json.load(sys.stdin); assert d.get("desfase_detectado") is False, d; print("API saludable:", d.get("desfase_detectado"))'
```

### Búsqueda de imagen y Top 5 esperado

```bash
curl --fail-with-body --silent --show-error \
  -H "X-API-Key: ${API_CLIENT_KEY}" \
  -F "file=@${QUERY_IMAGE}" -F "modelo=clip" -F "modo=auto" \
  "https://${SITE_ADDRESS}/backend/search/image" \
  -o /tmp/sublitex-search.json
python3 -c 'import json,os; d=json.load(open("/tmp/sublitex-search.json", encoding="utf-8")); r=d if isinstance(d,list) else d.get("resultados", []); assert 0 < len(r) <= 5 and r[0].get("id") == os.environ["EXPECTED_PRODUCT_ID"], r; print("Top 1:", r[0]["id"], "resultados:", len(r))'
```

### Archivo inválido e imagen menor de 32 px

```bash
printf 'no es una imagen' > /tmp/sublitex-invalid.jpg
status=$(curl --silent --show-error -o /tmp/sublitex-invalid-response.txt -w '%{http_code}' \
  -H "X-API-Key: ${API_CLIENT_KEY}" \
  -F "file=@/tmp/sublitex-invalid.jpg;type=image/jpeg" \
  "https://${SITE_ADDRESS}/backend/search/image")
test "$status" = 400
```

```bash
status=$(curl --silent --show-error -o /tmp/sublitex-tiny-response.txt -w '%{http_code}' \
  -H "X-API-Key: ${API_CLIENT_KEY}" \
  -F "file=@evaluation/fixtures/tiny-16.png;type=image/png" \
  "https://${SITE_ADDRESS}/backend/search/image")
test "$status" = 400
```

### Foto externa e interfaz

En un navegador del celular/PC externo, abre `https://${SITE_ADDRESS}` y prueba
una foto real autorizada. Confirma que el estado de carga termina, aparecen
resultados, las imágenes cargan y una ficha abre el destino esperado. Verifica
también el rechazo visible de archivo inválido, recuperación tras el error,
pantalla estrecha y uso de `/api/search`/`/api/health`. Guarda dispositivo,
navegador, fecha, resultado y capturas sin datos personales.

### Latencia CLIP/Qdrant

Usa una imagen autorizada, concurrencia baja al inicio y registra éxitos,
errores, p50 y p95:

```bash
python3 scripts/load_test_qdrant.py \
  --url "https://${SITE_ADDRESS}/backend/search/image" \
  --image "${QUERY_IMAGE}" --requests 10 --concurrency 1 --warmup 1 --timeout 180
```

### Repetición con dominio, HTTPS y acceso externo

```bash
curl -fsSI "https://${SITE_ADDRESS}/"
curl -fsS "https://${SITE_ADDRESS}/api/health"
curl -fsS "https://${SITE_ADDRESS}/backend/health"
```

Ejecuta además los pasos de búsqueda, rechazo de archivo y foto externa desde
un equipo fuera de la red administrativa. No expongas directamente la API si
se sirve a través del proxy.

## Checks de la sección 8

### 1. Catálogo con datos comerciales aprobados

```bash
python3 scripts/validar_catalogo.py
```

Debe terminar con código 0 y cero URLs de ejemplo/vacías, nombres iguales al
ID, imágenes inexistentes e IDs duplicados. Si los datos aún no fueron
entregados, debe fallar y este punto permanece pendiente.

### 2. VPS/Docker y dominio

```bash
docker info >/dev/null
docker compose version
getent hosts "$SITE_ADDRESS"
```

Registra la IP del VPS asignada y confirma en el panel del proveedor que el
dominio apunta a ella. No se puede certificar infraestructura solo desde el
checkout local.

### 3. Reverse proxy con HTTPS y rutas internas

```bash
curl -fsSI "https://${SITE_ADDRESS}/"
curl -fsS "https://${SITE_ADDRESS}/api/health"
curl -fsS "https://${SITE_ADDRESS}/backend/health"
docker compose exec -T proxy caddy validate --config /etc/caddy/Caddyfile
```

El navegador debe mostrar un certificado válido. En el VPS comprueba los
puertos publicados y que no haya listeners públicos en puertos internos:

```bash
sudo ss -lntp
docker compose ps
```

Qdrant puede enlazarse a `127.0.0.1:6333/6334` para administración local; no
debe estar publicado en interfaces públicas. API y frontend deben quedar
detrás del proxy.

### 4. Build del frontend

```bash
docker compose build --no-cache frontend
```

El build debe terminar correctamente. Revisa el log del build por errores y
confirma TypeScript mediante la salida del proceso; no uses secretos como
argumentos de build.

### 5. Seguridad de puertos y CORS

```bash
docker compose config --quiet
sudo ufw status verbose
sudo ss -lntp
```

Confirma que el firewall público solo permita SSH administrativo, 80 y 443; la
configuración Compose debe mantener Qdrant en loopback y API sin publicación
directa. Revisa `CORS_ORIGINS` en `.env` localmente sin copiar su contenido a
la evidencia: debe contener únicamente el origen HTTPS acordado, nunca `*`.

### 6. Búsqueda externa con destino comercial real

Repite desde celular/PC externo la búsqueda de imagen descrita arriba. Confirma
Top 5, que el Top 1 esperado coincide con la prueba aprobada y que abrir la
ficha lleva a un destino comercial real autorizado. Registra la evidencia
manual; un HTTP 200 solo no acredita relevancia ni destino comercial.
