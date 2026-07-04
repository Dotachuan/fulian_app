#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="/srv/backups/mysql"
DATE_STR="$(date +%F_%H%M%S)"
mkdir -p "$BACKUP_DIR"

mysqldump -u foundation_user -p foundation_donation > "$BACKUP_DIR/foundation_donation_${DATE_STR}.sql"
