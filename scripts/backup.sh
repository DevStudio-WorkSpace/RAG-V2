#!/usr/bin/env bash
# backup.sh — Backup de data/ y qdrant_data/ con snapshot Qdrant opcional
#
# Uso:
#   bash scripts/backup.sh                  # backup completo al directorio por defecto
#   bash scripts/backup.sh /ruta/destino    # directorio de destino personalizado
#   QDRANT_URL=http://... bash scripts/backup.sh   # Qdrant en otra URL
#
# Qué hace:
#   1. Crea un snapshot de la colección Qdrant activa (si Qdrant está disponible).
#   2. Comprime data/ en un .tar.gz con fecha+hora.
#   3. Comprime qdrant_data/ (almacenamiento de Qdrant, incluye snapshots) en otro .tar.gz.
#   4. Rota: mantiene los últimos RETENER backups, borra los más antiguos.
#
# Requisitos: bash ≥4, curl, tar (disponibles en cualquier instalación Linux estándar).
# Para cron: 0 2 * * * /bin/bash /ruta/proyecto/scripts/backup.sh >> /var/log/sublitex_backup.log 2>&1

set -euo pipefail

# ── Configuración ────────────────────────────────────────────────────────────
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${1:-${PROJECT_ROOT}/backups}"
QDRANT_URL="${QDRANT_URL:-http://127.0.0.1:6333}"
QDRANT_API_KEY="${QDRANT_API_KEY:-}"
QDRANT_COLLECTION="${QDRANT_COLLECTION_NAME:-sublitex_fashion_v1}"
RETENER=7          # número de backups comprimidos a conservar por carpeta
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_PREFIX="[backup ${TIMESTAMP}]"

# ── Helpers ──────────────────────────────────────────────────────────────────
log()  { echo "${LOG_PREFIX} $*"; }
warn() { echo "${LOG_PREFIX} AVISO: $*" >&2; }
die()  { echo "${LOG_PREFIX} ERROR: $*" >&2; exit 1; }

rotar() {
    local dir="$1" prefijo="$2"
    # Elimina los archivos más antiguos si hay más de RETENER
    local count
    count=$(find "${dir}" -maxdepth 1 -name "${prefijo}*.tar.gz" | wc -l)
    if (( count > RETENER )); then
        find "${dir}" -maxdepth 1 -name "${prefijo}*.tar.gz" \
            | sort | head -n $(( count - RETENER )) \
            | xargs rm -f
        log "Rotación: se eliminaron $(( count - RETENER )) backup(s) antiguo(s) de '${prefijo}'."
    fi
}

# ── Verificaciones previas ───────────────────────────────────────────────────
[[ -d "${PROJECT_ROOT}/data" ]]        || die "No se encontró data/ en ${PROJECT_ROOT}"
[[ -d "${PROJECT_ROOT}/qdrant_data" ]] || warn "qdrant_data/ no existe; se omitirá ese backup."

mkdir -p "${BACKUP_DIR}"
log "Directorio de backups: ${BACKUP_DIR}"
log "Raíz del proyecto:     ${PROJECT_ROOT}"

# ── 1. Snapshot de Qdrant ────────────────────────────────────────────────────
SNAPSHOT_OK=false
CURL_ARGS=(-s -S --max-time 60)
[[ -n "${QDRANT_API_KEY}" ]] && CURL_ARGS+=(-H "api-key: ${QDRANT_API_KEY}")

log "Solicitando snapshot de colección '${QDRANT_COLLECTION}' en ${QDRANT_URL} …"
SNAP_RESPONSE=$(curl "${CURL_ARGS[@]}" \
    -X POST \
    "${QDRANT_URL}/collections/${QDRANT_COLLECTION}/snapshots" \
    -o - 2>&1) || true

if echo "${SNAP_RESPONSE}" | grep -q '"status":"ok"'; then
    SNAP_NAME=$(echo "${SNAP_RESPONSE}" | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)
    log "Snapshot creado: ${SNAP_NAME}"
    SNAPSHOT_OK=true
else
    warn "No se pudo crear snapshot Qdrant (Qdrant podría estar apagado). Se continúa sin snapshot."
    warn "Respuesta: ${SNAP_RESPONSE:0:200}"
fi

# ── 2. Backup de data/ ───────────────────────────────────────────────────────
DATA_DEST="${BACKUP_DIR}/data_${TIMESTAMP}.tar.gz"
log "Comprimiendo data/ → ${DATA_DEST} …"
tar -czf "${DATA_DEST}" \
    --exclude="data/images_original" \
    -C "${PROJECT_ROOT}" data
DATA_SIZE=$(du -sh "${DATA_DEST}" | cut -f1)
log "Backup data/ completado: ${DATA_SIZE}"
rotar "${BACKUP_DIR}" "data_"

# ── 3. Backup de qdrant_data/ ────────────────────────────────────────────────
if [[ -d "${PROJECT_ROOT}/qdrant_data" ]]; then
    QDRANT_DEST="${BACKUP_DIR}/qdrant_data_${TIMESTAMP}.tar.gz"
    log "Comprimiendo qdrant_data/ → ${QDRANT_DEST} …"
    tar -czf "${QDRANT_DEST}" \
        -C "${PROJECT_ROOT}" qdrant_data
    QDRANT_SIZE=$(du -sh "${QDRANT_DEST}" | cut -f1)
    log "Backup qdrant_data/ completado: ${QDRANT_SIZE}"
    rotar "${BACKUP_DIR}" "qdrant_data_"
else
    warn "qdrant_data/ no existe; backup omitido."
fi

# ── 4. Resumen ───────────────────────────────────────────────────────────────
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "Backup finalizado."
log "  Snapshot Qdrant : $( ${SNAPSHOT_OK} && echo 'OK' || echo 'omitido (Qdrant inaccesible)')"
log "  data/           : ${DATA_DEST} (${DATA_SIZE})"
if [[ -d "${PROJECT_ROOT}/qdrant_data" ]]; then
    log "  qdrant_data/    : ${QDRANT_DEST} (${QDRANT_SIZE})"
fi
log "  Retención       : últimos ${RETENER} backups por carpeta"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

