#!/bin/bash
# Adze Studio — Daily GCS backup (rolling 7-day retention)
# Backs up: artists/ (configs, content, assets, DBs), .env, logs/, nginx configs
# Skips: output/ (regenerable via compile.py), __pycache__, .snapshots
#
# Install: crontab -e → 0 3 * * * /home/gabriel/adze/backup-gcs.sh >> /home/gabriel/adze/logs/backup-gcs.log 2>&1

set -euo pipefail

ADZE_DIR="/home/gabriel/adze"
BUCKET="gs://adze-backups/adze"
DATE=$(date +%Y-%m-%d)
ARCHIVE="/tmp/adze-backup-${DATE}.tar.gz"
LOG_PREFIX="[$(date '+%Y-%m-%d %H:%M:%S')]"

echo "${LOG_PREFIX} Starting Adze backup..."

# Create archive (exclude regenerable output, snapshots, pycache)
cd "${ADZE_DIR}"
tar czf "${ARCHIVE}" \
    --exclude='__pycache__' \
    --exclude='.snapshots' \
    --exclude='output' \
    --exclude='*.pyc' \
    artists/ \
    logs/ \
    .env \
    nginx/ \
    _claude_sessions.json \
    2>/dev/null || true

SIZE=$(du -sh "${ARCHIVE}" | cut -f1)
echo "${LOG_PREFIX} Archive created: ${ARCHIVE} (${SIZE})"

# Upload to GCS
gsutil -q cp "${ARCHIVE}" "${BUCKET}/daily/${DATE}.tar.gz"
echo "${LOG_PREFIX} Uploaded to ${BUCKET}/daily/${DATE}.tar.gz"

# Clean up local archive
rm -f "${ARCHIVE}"

# Rolling retention: delete backups older than 7 days
CUTOFF=$(date -d '7 days ago' +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d)
gsutil ls "${BUCKET}/daily/" 2>/dev/null | while read -r file; do
    FILE_DATE=$(basename "$file" .tar.gz)
    if [[ "${FILE_DATE}" < "${CUTOFF}" ]]; then
        gsutil -q rm "$file"
        echo "${LOG_PREFIX} Deleted old backup: ${file}"
    fi
done

echo "${LOG_PREFIX} Backup complete."
