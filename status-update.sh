#!/bin/bash
# Writes system status to logs/status.json (read by admin dashboard API)
# Run via cron every 5 minutes: */5 * * * * /home/gabriel/adze/status-update.sh

STATUS_FILE="/home/gabriel/adze/logs/status.json"

# Docker
DOCKER_STATUS=$(docker inspect --format '{{.State.Status}}' adze-flask 2>/dev/null || echo "unknown")
DOCKER_STARTED=$(docker inspect --format '{{.State.StartedAt}}' adze-flask 2>/dev/null | head -c 19 | tr 'T' ' ')
DOCKER_RESTARTS=$(docker inspect --format '{{.RestartCount}}' adze-flask 2>/dev/null || echo "0")
DOCKER_STATS=$(docker stats --no-stream --format '{{.CPUPerc}}|{{.MemUsage}}' adze-flask 2>/dev/null || echo "?|?")
DOCKER_CPU=$(echo "$DOCKER_STATS" | cut -d'|' -f1 | tr -d ' ')
DOCKER_MEM=$(echo "$DOCKER_STATS" | cut -d'|' -f2 | tr -d ' ')

# Disk
DISK_INFO=$(df -h /home/gabriel/adze 2>/dev/null | tail -1)
DISK_TOTAL=$(echo "$DISK_INFO" | awk '{print $2}')
DISK_USED=$(echo "$DISK_INFO" | awk '{print $3}')
DISK_AVAIL=$(echo "$DISK_INFO" | awk '{print $4}')
DISK_PCT=$(echo "$DISK_INFO" | awk '{print $5}')

# GCS Backup
BACKUP_INFO=$(gsutil ls -l gs://adze-backups/adze/daily/ 2>/dev/null | grep -v TOTAL | tail -1)
if [ -n "$BACKUP_INFO" ]; then
    BACKUP_SIZE=$(echo "$BACKUP_INFO" | awk '{print $1}')
    BACKUP_DATE=$(echo "$BACKUP_INFO" | awk '{print $2}' | head -c 10)
    BACKUP_COUNT=$(gsutil ls gs://adze-backups/adze/daily/ 2>/dev/null | wc -l)
else
    BACKUP_SIZE="0"
    BACKUP_DATE="none"
    BACKUP_COUNT="0"
fi

cat > "$STATUS_FILE" << ENDJSON
{
    "docker": {
        "status": "${DOCKER_STATUS}",
        "started": "${DOCKER_STARTED}",
        "restarts": ${DOCKER_RESTARTS:-0},
        "cpu": "${DOCKER_CPU}",
        "memory": "${DOCKER_MEM}"
    },
    "disk": {
        "total": "${DISK_TOTAL}",
        "used": "${DISK_USED}",
        "available": "${DISK_AVAIL}",
        "percent": "${DISK_PCT}"
    },
    "backup": {
        "last_date": "${BACKUP_DATE}",
        "last_size": ${BACKUP_SIZE:-0},
        "count": ${BACKUP_COUNT:-0}
    },
    "updated": "$(date -Iseconds)"
}
ENDJSON
