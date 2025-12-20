#!/bin/bash

# Script de Backup antes de merge con rama roq
# Fecha: $(date +%Y%m%d-%H%M%S)

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_BRANCH="backup-before-roq-merge-${TIMESTAMP}"
DB_BACKUP="db.sqlite3.backup-roq-${TIMESTAMP}"

echo "🔄 Iniciando backup antes de merge con rama 'roq'..."
echo "Timestamp: ${TIMESTAMP}"
echo ""

# 1. Crear backup de la base de datos
echo "📦 1/5 Creando backup de base de datos..."
if [ -f "db.sqlite3" ]; then
    cp db.sqlite3 "${DB_BACKUP}"
    echo "✅ Base de datos respaldada: ${DB_BACKUP}"
else
    echo "⚠️  No se encontró db.sqlite3"
fi
echo ""

# 2. Commit de cambios actuales
echo "💾 2/5 Guardando cambios actuales en staging..."
git add -A
echo "✅ Archivos agregados al staging"
echo ""

# 3. Crear commit con los cambios actuales
echo "📝 3/5 Creando commit de backup..."
git commit -m "Backup antes de merge con roq - Dashboard implementado

- Dashboard completo y funcional
- Vista de detalle de reportes
- Lista de reportes
- Tarjeta de formularios en home
- Link de dashboard en menú de perfil
- Documentación completa

Timestamp: ${TIMESTAMP}"
echo "✅ Commit creado"
echo ""

# 4. Crear rama de backup
echo "🌿 4/5 Creando rama de backup..."
git branch "${BACKUP_BRANCH}"
echo "✅ Rama de backup creada: ${BACKUP_BRANCH}"
echo ""

# 5. Mostrar estado
echo "📊 5/5 Estado actual:"
echo "---"
git log --oneline -3
echo "---"
echo ""

echo "✅ BACKUP COMPLETADO!"
echo ""
echo "📌 Información del backup:"
echo "   - Rama de backup: ${BACKUP_BRANCH}"
echo "   - DB backup: ${DB_BACKUP}"
echo "   - Rama actual: $(git branch --show-current)"
echo ""
echo "🔄 Para hacer el merge con roq:"
echo "   git fetch origin"
echo "   git merge origin/roq"
echo ""
echo "⚠️  Si algo sale mal, puedes restaurar con:"
echo "   git reset --hard ${BACKUP_BRANCH}"
echo "   cp ${DB_BACKUP} db.sqlite3"
echo ""

