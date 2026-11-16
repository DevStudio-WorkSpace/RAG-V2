#!/usr/bin/env bash
# Creates a consistent business-data archive and an official Qdrant snapshot.
# Run from any directory. Requires bash, curl, python3, and tar.
set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
QDRANT_URL="${QDRANT_URL:-http://127.0.0.1:6333}"
QDRANT_COLLECTION="${QDRANT_COLLECTION_NAME:-sublitex_fashion_v1}"
RETENTION="${BACKUP_RETENTION:-7}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
FINAL_ARCHIVE="${BACKUP_DIR}/ragv2_${TIMESTAMP}.tar.gz"

log() { printf '[backup %s] %s\n' "${TIMESTAMP}" "$*"; }
die() { log "ERROR: $*" >&2; exit 1; }

[[ "${RETENTION}" =~ ^[1-9][0-9]*$ ]] || die "BACKUP_RETENTION debe ser un entero mayor que cero."
[[ -n "${QDRANT_API_KEY:-}" ]] || die "QDRANT_API_KEY no está configurada en el entorno."
[[ -f "${PROJECT_ROOT}/data/products.csv" ]] || die "Falta data/products.csv."
[[ -f "${PROJECT_ROOT}/data/embeddings.npy" ]] || die "Falta data/embeddings.npy."
[[ -f "${PROJECT_ROOT}/data/ids.npy" ]] || die "Falta data/ids.npy."
[[ -d "${PROJECT_ROOT}/data/images_normalized" ]] || die "Falta data/images_normalized/."

mkdir -p "${BACKUP_DIR}"
WORK_DIR="$(mktemp -d "${BACKUP_DIR}/.ragv2-backup-${TIMESTAMP}.XXXXXX")"
ARCHIVE_TMP="${BACKUP_DIR}/.ragv2_${TIMESTAMP}.tar.gz.tmp"
cleanup() { rm -rf -- "${WORK_DIR}"; rm -f -- "${ARCHIVE_TMP}"; }
trap cleanup EXIT

log "Solicitando snapshot oficial de Qdrant: ${QDRANT_COLLECTION}."
SNAPSHOT_JSON="$(curl --fail --silent --show-error --max-time 120 \
  -H "api-key: ${QDRANT_API_KEY}" -X POST \
  "${QDRANT_URL}/collections/${QDRANT_COLLECTION}/snapshots")" \
  || die "Qdrant no creó el snapshot; backup cancelado."
SNAPSHOT_NAME="$(printf '%s' "${SNAPSHOT_JSON}" | python3 -c \
  'import json,sys; print(json.load(sys.stdin).get("result",{}).get("name", ""))')" \
  || die "Qdrant devolvió una respuesta de snapshot inválida."
[[ -n "${SNAPSHOT_NAME}" && "${SNAPSHOT_NAME}" != */* ]] \
  || die "El nombre del snapshot está vacío o no es seguro."

SNAPSHOT_FILE="${WORK_DIR}/${SNAPSHOT_NAME}"
curl --fail --silent --show-error --max-time 600 \
  -H "api-key: ${QDRANT_API_KEY}" \
  "${QDRANT_URL}/collections/${QDRANT_COLLECTION}/snapshots/${SNAPSHOT_NAME}" \
  -o "${SNAPSHOT_FILE}" || die "No se pudo descargar el snapshot."
[[ -s "${SNAPSHOT_FILE}" ]] || die "El snapshot descargado está vacío."

mkdir -p "${WORK_DIR}/payload/data" "${WORK_DIR}/payload/qdrant_snapshots"
cp -- "${PROJECT_ROOT}/data/products.csv" "${WORK_DIR}/payload/data/"
cp -- "${PROJECT_ROOT}/data/embeddings.npy" "${WORK_DIR}/payload/data/"
cp -- "${PROJECT_ROOT}/data/ids.npy" "${WORK_DIR}/payload/data/"
cp -a -- "${PROJECT_ROOT}/data/images_normalized" "${WORK_DIR}/payload/data/"
mv -- "${SNAPSHOT_FILE}" "${WORK_DIR}/payload/qdrant_snapshots/"

cat > "${WORK_DIR}/payload/BACKUP_MANIFEST.txt" <<EOF
created_utc=${TIMESTAMP}
qdrant_collection=${QDRANT_COLLECTION}
qdrant_url=${QDRANT_URL}
contents=data/products.csv,data/embeddings.npy,data/ids.npy,data/images_normalized,qdrant_snapshots/${SNAPSHOT_NAME}
excluded=data/images_original,data/queries_original,data/queries_procesadas,.env
EOF

log "Empaquetando catálogo, índices e imágenes normalizadas (sin fotos de consulta)."
tar -czf "${ARCHIVE_TMP}" -C "${WORK_DIR}/payload" . \
  || die "Falló la compresión del respaldo."
tar -tzf "${ARCHIVE_TMP}" >/dev/null \
  || die "El archivo comprimido no pasó la verificación."
mv -- "${ARCHIVE_TMP}" "${FINAL_ARCHIVE}"

# Delete the server-side snapshot only after the downloaded copy is verified.
if curl --fail --silent --show-error --max-time 120 \
  -H "api-key: ${QDRANT_API_KEY}" -X DELETE \
  "${QDRANT_URL}/collections/${QDRANT_COLLECTION}/snapshots/${SNAPSHOT_NAME}" >/dev/null; then
  log "Snapshot temporal eliminado de Qdrant tras verificar el archivo."
else
  log "AVISO: el respaldo está verificado, pero no se pudo borrar el snapshot temporal de Qdrant." >&2
fi

mapfile -t ARCHIVES < <(find "${BACKUP_DIR}" -maxdepth 1 -type f -name 'ragv2_*.tar.gz' -printf '%f\n' | sort -r)
if (( ${#ARCHIVES[@]} > RETENTION )); then
  for old in "${ARCHIVES[@]:RETENTION}"; do
    rm -f -- "${BACKUP_DIR}/${old}"
  done
fi

log "Backup verificado: ${FINAL_ARCHIVE} ($(du -h "${FINAL_ARCHIVE}" | cut -f1))."
