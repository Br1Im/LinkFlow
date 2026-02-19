#!/bin/bash

echo "========================================="
echo "Установка crypto_vip_robot на сервер"
echo "========================================="
echo ""

# Остановка старого бота
echo "1. Остановка старого бота..."
pm2 stop crypto-bot 2>/dev/null || echo "Бот не был запущен"
pm2 delete crypto-bot 2>/dev/null || echo "Бот не был в PM2"

# Резервная копия
echo ""
echo "2. Создание резервной копии..."
cd /root
if [ -d "Cryptoliqbez" ]; then
    BACKUP_NAME="Cryptoliqbez_backup_$(date +%Y%m%d_%H%M%S)"
    mv Cryptoliqbez "$BACKUP_NAME"
    echo "Резервная копия создана: $BACKUP_NAME"
else
    echo "Старой версии не найдено"
fi

# Распаковка новых файлов
echo ""
echo "3. Распаковка новых файлов..."
mkdir -p Cryptoliqbez
cd Cryptoliqbez
unzip -o ../crypto_bot.zip

# Установка зависимостей
echo ""
echo "4. Установка зависимостей..."
pip3.11 install -r requirements.txt

# Очистка кэша
echo ""
echo "5. Очистка кэша Python..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete

# Проверка файлов
echo ""
echo "6. Проверка файлов..."
ls -la

# Запуск бота
echo ""
echo "7. Запуск бота..."
pm2 start --name crypto-bot --interpreter python3.11 run.py
pm2 save

# Показ логов
echo ""
echo "========================================="
echo "Установка завершена!"
echo "========================================="
echo ""
echo "Проверка логов (Ctrl+C для выхода):"
sleep 2
pm2 logs crypto-bot --lines 30
