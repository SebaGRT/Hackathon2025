#!/bin/bash

# Backup script for calendar enhancement
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backup_calendar_${TIMESTAMP}"

echo "Creating backup: ${BACKUP_DIR}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Backup files
cp seguridad/templates/seguridad/dashboard.html "${BACKUP_DIR}/dashboard.html.bak"
cp seguridad/views.py "${BACKUP_DIR}/views.py.bak"
cp db.sqlite3 "${BACKUP_DIR}/db.sqlite3.bak"

echo "✅ Backup created in: ${BACKUP_DIR}"
echo ""
echo "Files backed up:"
echo "  - dashboard.html"
echo "  - views.py"
echo "  - db.sqlite3"
echo ""
echo "To restore, run:"
echo "  cp ${BACKUP_DIR}/dashboard.html.bak seguridad/templates/seguridad/dashboard.html"
echo "  cp ${BACKUP_DIR}/views.py.bak seguridad/views.py"
echo "  cp ${BACKUP_DIR}/db.sqlite3.bak db.sqlite3"

