#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

if [[ "$(git branch --show-current)" != "sala-6" ]]; then
    echo "ERROR: deploy.sh solo despliega la rama sala-6." >&2
    exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "ERROR: hay cambios versionados sin guardar; no se desplegará." >&2
    exit 1
fi

if [[ ! -f .env ]]; then
    echo "ERROR: falta .env de producción." >&2
    exit 1
fi

git pull --ff-only origin sala-6
export APP_IMAGE_TAG="$(git rev-parse --verify HEAD)"

docker compose config --quiet
docker compose build api frontend
docker compose up -d

for attempt in $(seq 1 120); do
    if docker compose exec -T api python -c \
        'import json,sys,urllib.request; d=json.load(urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=10)); sys.exit(0 if d.get("desfase_detectado") is False else 1)' \
        >/dev/null 2>&1; then
        echo "Despliegue sano: /health responde sin desfase."
        docker compose ps
        exit 0
    fi
    sleep 5
done

echo "ERROR: la API no quedó sana dentro del tiempo de espera." >&2
docker compose ps >&2
docker compose logs --tail=80 api >&2
exit 1
