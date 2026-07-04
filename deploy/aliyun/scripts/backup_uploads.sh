#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="/srv/foundation-donation/backend/uploads"
BACKUP_DIR="/srv/backups/uploads"
DATE_STR="$(date +%F_%H%M%S)"

mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/uploads_${DATE_STR}.tar.gz" -C "$SOURCE_DIR" .
