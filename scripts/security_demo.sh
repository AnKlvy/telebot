#!/bin/bash

echo "🔍 Демонстрация разницы в безопасности хранения переменных окружения"
echo "=================================================================="

echo ""
echo "❌ НЕБЕЗОПАСНО: .env файл в корне проекта"
echo "------------------------------------------------"

# Создаем пример небезопасного .env
cat > /tmp/unsafe_env << EOF
BOT_TOKEN=1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
POSTGRES_PASSWORD=super_secret_password
EOF

chmod 644 /tmp/unsafe_env  # Обычные права для файлов проекта

echo "Файл: /tmp/unsafe_env"
echo "Права доступа:"
ls -la /tmp/unsafe_env

echo ""
echo "Кто может прочитать файл:"
echo "- Владелец: ✅ Да"
echo "- Группа: ✅ Да" 
echo "- Все остальные: ✅ Да"
echo "- Веб-сервер: ✅ Да"
echo "- Другие процессы: ✅ Да"

echo ""
echo "Содержимое видно всем:"
cat /tmp/unsafe_env

echo ""
echo "=================================================================="
echo ""
echo "✅ БЕЗОПАСНО: Переменные в защищенной директории"
echo "------------------------------------------------"

# Создаем пример безопасного хранения
sudo mkdir -p /tmp/secure_config
sudo chmod 700 /tmp/secure_config

sudo tee /tmp/secure_config/env > /dev/null << EOF
BOT_TOKEN=1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
POSTGRES_PASSWORD=super_secret_password
EOF

sudo chmod 600 /tmp/secure_config/env
sudo chown root:root /tmp/secure_config/env

echo "Файл: /tmp/secure_config/env"
echo "Права доступа:"
sudo ls -la /tmp/secure_config/env

echo ""
echo "Кто может прочитать файл:"
echo "- root: ✅ Да"
echo "- Группа: ❌ Нет"
echo "- Все остальные: ❌ Нет"
echo "- Веб-сервер: ❌ Нет"
echo "- Другие процессы: ❌ Нет"

echo ""
echo "Попытка чтения обычным пользователем:"
if cat /tmp/secure_config/env 2>/dev/null; then
    echo "❌ Файл прочитан!"
else
    echo "✅ Доступ запрещен (Permission denied)"
fi

echo ""
echo "=================================================================="
echo ""
echo "🎯 ВЫВОДЫ:"
echo "----------"
echo "1. .env в корне проекта = доступен всем процессам"
echo "2. Файл в /etc/ с правами 600 = доступен только root"
echo "3. Docker может читать файл через volume mount"
echo "4. Секреты изолированы от исходного кода"
echo "5. Не попадают в Git репозиторий"
echo "6. Не попадают в бэкапы кода"

# Очистка
rm -f /tmp/unsafe_env
sudo rm -rf /tmp/secure_config

echo ""
echo "🔒 Рекомендация: Всегда используйте защищенные директории для секретов!"
