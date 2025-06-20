# SSL для Telegram Bot на Beget VPS

## 🎯 Один скрипт для всего

Забудьте про кучу команд! Теперь всё SSL управление в одном месте:

```bash
./scripts/ssl_manager.sh
```

## 🚀 Что умеет SSL менеджер

1. **Показать статус** - полная диагностика системы, домена, SSL
2. **Включить HTTPS** - автоматически создаст сертификаты если нужно  
3. **Включить HTTP** - для тестирования без SSL
4. **Создать SSL сертификаты** - через acme.sh с автообновлением
5. **Выход** - просто выйти

## 📋 Что проверяет статус

- **Система**: ОС, внешний IP, порты 80/443
- **Домен**: DNS настройки, указывает ли на сервер
- **SSL**: наличие сертификатов, срок действия
- **Docker**: статус контейнеров
- **Рекомендации**: что нужно исправить

## ⚙️ Автоматические функции

- **Права доступа**: автоматически делает скрипты исполняемыми
- **Резервные копии**: сохраняет конфигурации перед изменениями
- **Проверки**: валидирует домен, сертификаты, DNS
- **Обновление переменных**: автоматически обновляет /etc/edu_telebot/env

## 🔧 Для разработчиков

Все функции теперь встроены в SSL менеджер. Отдельные скрипты больше не нужны!

## 💡 Рекомендации для Beget

1. **Начните с HTTP** - протестируйте бота без SSL
2. **Настройте домен** - купите домен и настройте DNS
3. **Включите HTTPS** - через SSL менеджер одной командой
4. **Проверяйте статус** - регулярно запускайте диагностику

## 🚨 Частые проблемы

**Домен не указывает на сервер:**
- Проверьте DNS записи домена
- Подождите распространения DNS (до 24 часов)

**Порт 80 занят:**
- SSL менеджер автоматически остановит nginx
- Если не помогает: `sudo docker-compose down`

**Сертификаты не создаются:**
- Убедитесь что домен реальный (не localhost)
- Проверьте что домен указывает на ваш сервер
- Попробуйте через несколько минут

## 🎉 Готово!

Теперь SSL настройка - это просто:
```bash
./scripts/ssl_manager.sh
```

Выбираете нужный пункт и всё работает!
