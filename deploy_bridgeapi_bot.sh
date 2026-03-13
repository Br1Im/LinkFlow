#!/bin/bash

# Скрипт развертывания BridgeAPI_Bot со всеми новыми функциями

echo "🚀 РАЗВЕРТЫВАНИЕ BRIDGEAPI_BOT"
echo "================================"

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python3."
    exit 1
fi

# Переходим в директорию бота
BOT_DIR="bots/BridgeAPI_Bot"

if [ ! -d "$BOT_DIR" ]; then
    echo "❌ Директория $BOT_DIR не найдена"
    exit 1
fi

cd "$BOT_DIR"

echo "📁 Рабочая директория: $(pwd)"

# Останавливаем существующий процесс
echo "🛑 Остановка существующего бота..."
pkill -f "python.*run.py" || echo "⚠️ Процесс не найден"

# Создаем бэкап базы данных
if [ -f "bridgeapi_bot.db" ]; then
    echo "📦 Создание бэкапа базы данных..."
    cp bridgeapi_bot.db "bridgeapi_bot.db.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Бэкап создан"
fi

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo "✅ Зависимости установлены"
else
    echo "⚠️ requirements.txt не найден, устанавливаем основные пакеты..."
    pip3 install aiogram aiosqlite python-dotenv requests aiohttp
fi

# Проверяем конфигурацию
echo "⚙️ Проверка конфигурации..."
if [ ! -f ".env" ]; then
    echo "❌ .env файл не найден!"
    echo "Создайте .env файл с настройками:"
    echo "API_TOKEN=your_bot_token"
    echo "SBP_SHOP_ID=802685"
    echo "SBP_SECRET_KEY=your_secret_key"
    echo "PROXYAPI_KEY=sk-YEMVoEtElex2mgBoEYe4K79pOBoONUtr"
    echo "ADMIN_IDS=your_telegram_id"
    exit 1
fi

# Проверяем основные файлы
REQUIRED_FILES=("run.py" "handlers.py" "config.py" "db.py" "keyboards.py" "sbp_payment.py")
NEW_FILES=("ai_service.py" "ai_handlers.py" "admin_handlers.py")

echo "📋 Проверка файлов..."
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - отсутствует"
    fi
done

echo "📋 Новые файлы (AI и админка):"
for file in "${NEW_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - отсутствует"
    fi
done

# Инициализируем базу данных
echo "🗄️ Инициализация базы данных..."
python3 -c "
import sys
sys.path.append('.')
import asyncio
from db import init_db
asyncio.run(init_db())
print('✅ База данных инициализирована')
" || echo "⚠️ Ошибка инициализации БД"

# Запускаем бота
echo "🚀 Запуск бота..."
nohup python3 run.py > bot.log 2>&1 &
BOT_PID=$!

sleep 3

# Проверяем запуск
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Бот запущен (PID: $BOT_PID)"
    echo "📋 Логи: $(pwd)/bot.log"
    
    # Показываем первые строки лога
    echo "📄 Первые строки лога:"
    head -10 bot.log 2>/dev/null || echo "Лог пока пуст"
    
else
    echo "❌ Ошибка запуска бота"
    echo "📋 Проверьте логи:"
    cat bot.log 2>/dev/null || echo "Лог файл не найден"
    exit 1
fi

echo ""
echo "🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "=========================="
echo ""
echo "✅ Функции бота:"
echo "• 💳 Платежная система СБП"
echo "• 🤖 10 AI-инструментов"
echo "• 👑 Админ-панель (/admin)"
echo "• 🎬 Генерация видео"
echo "• 📊 Статистика"
echo ""
echo "🔧 Что делать дальше:"
echo "1. Убедитесь что ADMIN_IDS в .env содержит ваш Telegram ID"
echo "2. Протестируйте бота: отправьте /start"
echo "3. Проверьте админку: отправьте /admin"
echo "4. Протестируйте AI-функции"
echo ""
echo "📋 Управление ботом:"
echo "• Логи: tail -f $(pwd)/bot.log"
echo "• Остановка: pkill -f 'python.*run.py'"
echo "• Перезапуск: ./deploy_bridgeapi_bot.sh"
echo ""
echo "🆔 PID бота: $BOT_PID"