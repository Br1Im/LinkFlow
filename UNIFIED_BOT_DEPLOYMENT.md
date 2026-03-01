# Unified Bot Deployment Guide

## Информация о боте

- **Имя бота**: @AxisPay_bot
- **Токен**: 8608759887:AAE56HA3BNcZd4b1_7h1NE5AWGV-Sw8EvLU
- **Поддержка**: @eva_support1
- **Сервер**: root@85.192.56.74
- **Путь на сервере**: /root/LinkFlow/bots/unified_bot

## Функционал

### Платные подписки (4 канала)
- 🪙 Крипто-канал: 1500₽ + 100₽/день (макс 30 дней)
- 💪 Фитнес-канал: 3000₽ + 100₽/день (макс 30 дней)
- 🥗 Питание: 3000₽ + 100₽/день (макс 30 дней)
- 🤖 AI-канал: 2500₽ + 100₽/день (макс 30 дней)

### Гороскоп AI
- Отдельный бот: @Luma_Astro_bot
- Кнопка в главном меню ведет на этот бот

### Пользовательское соглашение
- Полный текст (8 разделов) отображается при нажатии кнопки
- Минимальная сумма покупки: 3100₽
- Контакт поддержки: @eva_support1

## Проверка перед развертыванием

Запустите локальный тест:
```bash
python test_unified_bot_local.py
```

Должны быть все ✅ галочки.

## Развертывание на сервере

### Windows (PowerShell)
```powershell
.\deploy_unified_bot.ps1
```

### Linux/Mac (Bash)
```bash
chmod +x deploy_unified_bot.sh
./deploy_unified_bot.sh
```

### Ручное развертывание

1. Подключитесь к серверу:
```bash
ssh root@85.192.56.74
```

2. Создайте директорию (если не существует):
```bash
mkdir -p /root/LinkFlow/bots/unified_bot
```

3. Скопируйте файлы с локальной машины:
```bash
scp bots/unified_bot/*.py root@85.192.56.74:/root/LinkFlow/bots/unified_bot/
scp bots/unified_bot/.env root@85.192.56.74:/root/LinkFlow/bots/unified_bot/
```

4. Остановите старый процесс (если запущен):
```bash
ssh root@85.192.56.74 "pkill -f 'python3.*unified_bot'"
```

5. Запустите бота:
```bash
ssh root@85.192.56.74 "cd /root/LinkFlow/bots/unified_bot && nohup python3 run.py > unified_bot.log 2>&1 &"
```

## Проверка работы

### Просмотр логов
```bash
ssh root@85.192.56.74 "tail -f /root/LinkFlow/bots/unified_bot/unified_bot.log"
```

### Остановка бота
```bash
ssh root@85.192.56.74 "pkill -f 'python3.*unified_bot'"
```

### Перезапуск бота
```bash
ssh root@85.192.56.74 "pkill -f 'python3.*unified_bot' && cd /root/LinkFlow/bots/unified_bot && nohup python3 run.py > unified_bot.log 2>&1 &"
```

## Тестирование в Telegram

1. Откройте бота: https://t.me/AxisPay_bot
2. Отправьте /start
3. Проверьте:
   - ✅ Приветственное сообщение отображается
   - ✅ Кнопка "Пользовательское соглашение" показывает полный текст (8 разделов)
   - ✅ Кнопка "Платные подписки" показывает правильные цены
   - ✅ Кнопка "Баланс" показывает все продукты с ценами
   - ✅ Кнопка "Поддержка" показывает @eva_support1
   - ✅ Кнопка "Гороскоп AI" ведет на @Luma_Astro_bot

## Структура файлов

```
bots/unified_bot/
├── config.py          # Конфигурация (цены, тексты, API)
├── keyboards.py       # Клавиатуры
├── handlers.py        # Обработчики команд и кнопок
├── db.py             # База данных (SQLite)
├── run.py            # Запуск бота
└── .env              # Переменные окружения (токены, ключи)
```

## Зависимости

Убедитесь, что на сервере установлены:
- Python 3.8+
- aiogram 3.x
- aiosqlite
- requests
- python-dotenv

Установка:
```bash
pip3 install aiogram aiosqlite requests python-dotenv
```

## Troubleshooting

### Бот не отвечает
1. Проверьте, запущен ли процесс:
```bash
ssh root@85.192.56.74 "ps aux | grep unified_bot"
```

2. Проверьте логи:
```bash
ssh root@85.192.56.74 "tail -50 /root/LinkFlow/bots/unified_bot/unified_bot.log"
```

### Ошибка "Token is invalid"
Проверьте токен в файле .env на сервере:
```bash
ssh root@85.192.56.74 "cat /root/LinkFlow/bots/unified_bot/.env | grep API_TOKEN"
```

### Платежи не работают
Проверьте, что API сервер запущен:
```bash
curl http://85.192.56.74:5001/api/create-bot-payment/nutrition -X POST -H "Content-Type: application/json" -d '{"amount": 1000}'
```

## Контакты

- Поддержка: @eva_support1
- Сервер: root@85.192.56.74
- Payment API: http://85.192.56.74:5001

