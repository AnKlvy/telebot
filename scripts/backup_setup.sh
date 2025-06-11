#!/bin/bash

# Простая настройка автобэкапов PostgreSQL
echo "🔧 Настройка автобэкапов PostgreSQL..."

# Создаем директорию для бэкапов
mkdir -p ~/backups/telebot
echo "📁 Создана директория: ~/backups/telebot"

# Получаем текущую директорию проекта
PROJECT_DIR=$(pwd)
echo "📍 Проект находится в: $PROJECT_DIR"

# Создаем простой скрипт бэкапа
cat > ~/backups/backup_telebot.sh << EOF
#!/bin/bash

# Простой скрипт бэкапа телеграм-бота
cd $PROJECT_DIR  # Путь к проекту

DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="\$HOME/backups/telebot/backup_\$DATE.sql"

# Создаем бэкап
docker-compose exec -T postgres pg_dump -U telebot_user telebot > \$BACKUP_FILE

# Сжимаем
gzip \$BACKUP_FILE

# Удаляем старые (старше 7 дней)
find \$HOME/backups/telebot -name "backup_*.sql.gz" -mtime +7 -delete

echo "✅ Бэкап создан: \$BACKUP_FILE.gz"
EOF

# Делаем исполняемым
chmod +x ~/backups/backup_telebot.sh
echo "📝 Создан скрипт: ~/backups/backup_telebot.sh"

# Добавляем в cron (каждый день в 3:00)
(crontab -l 2>/dev/null; echo "0 3 * * * ~/backups/backup_telebot.sh") | crontab -
echo "⏰ Добавлена cron-задача: ежедневно в 3:00"

echo ""
echo "✅ Готово! Автобэкапы настроены."
echo ""
echo "🧪 Тестирование:"
echo "   ~/backups/backup_telebot.sh  # Запустить вручную"
echo "   ls -la ~/backups/telebot/    # Посмотреть бэкапы"
echo "   crontab -l                   # Проверить cron"
