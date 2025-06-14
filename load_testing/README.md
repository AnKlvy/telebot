# Нагрузочное тестирование телеграм бота

Набор инструментов для НАСТОЯЩЕГО нагрузочного тестирования производительности бота.

## Структура

- `simple_test.py` - ⚡ Быстрый параллельный тест webhook (БЕЗ пауз!)
- `webhook_load_test.py` - 🌐 Продвинутое тестирование webhook с разными режимами
- `advanced_load_test.py` - 🚀 Продвинутый тест с мониторингом ресурсов
- `full_load_test.py` - 🎯 Комплексное тестирование всех компонентов
- `telegram_user_simulation.py` - 👥 Имитация реальных пользователей через Telegram API
- `database_stress_test.py` - 🗄️ Тестирование производительности базы данных
- `redis_performance_test.py` - 🔴 Тестирование Redis под нагрузкой
- `requirements.txt` - Зависимости для тестирования

## Установка

```bash
cd load_testing
pip install -r requirements.txt
```

## Использование

### 1. Тестирование webhook
```bash
python webhook_load_test.py --url https://edubot.schoolpro.kz/webhook --users 100 --duration 60
```

### 2. Имитация пользователей
```bash
python telegram_user_simulation.py --bot-token YOUR_BOT_TOKEN --users 50 --actions 10
```

### 3. Тестирование базы данных
```bash
python database_stress_test.py --concurrent 20 --operations 1000
```

### 4. Комплексное тестирование
```bash
python full_load_test.py --scenario basic --duration 300
```

## Мониторинг

Все тесты создают подробные отчеты в папке `reports/` с метриками:
- Время отклика
- Пропускная способность
- Ошибки
- Использование ресурсов
