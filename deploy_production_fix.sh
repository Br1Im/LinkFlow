#!/bin/bash

echo "🚀 Деплой улучшенной версии на хостинг"
echo "========================================"

# Проверяем, что мы на хостинге
if [ ! -f "/etc/systemd/system/webhook.service" ]; then
    echo "❌ Этот скрипт нужно запускать на хостинге!"
    exit 1
fi

# Останавливаем сервис
echo "⏸️  Останавливаю webhook сервис..."
sudo systemctl stop webhook

# Делаем бэкап текущей версии
echo "💾 Создаю бэкап..."
cp webhook_server_production.py webhook_server_production.py.backup.$(date +%Y%m%d_%H%M%S)

# Копируем новую версию (предполагается, что файл уже загружен)
echo "📦 Обновляю файлы..."

# Проверяем синтаксис Python
echo "🔍 Проверяю синтаксис..."
python3 -m py_compile webhook_server_production.py
if [ $? -ne 0 ]; then
    echo "❌ Ошибка синтаксиса в webhook_server_production.py!"
    echo "♻️  Восстанавливаю бэкап..."
    cp webhook_server_production.py.backup.* webhook_server_production.py
    sudo systemctl start webhook
    exit 1
fi

# Запускаем сервис
echo "▶️  Запускаю webhook сервис..."
sudo systemctl start webhook

# Ждем немного
sleep 3

# Проверяем статус
echo "📊 Проверяю статус..."
sudo systemctl status webhook --no-pager -l

# Показываем последние логи
echo ""
echo "📋 Последние логи:"
sudo journalctl -u webhook -n 20 --no-pager

echo ""
echo "✅ Деплой завершен!"
echo ""
echo "Для просмотра логов в реальном времени:"
echo "  sudo journalctl -u webhook -f"
echo ""
echo "Для проверки работы:"
echo "  curl -X POST http://localhost:5000/api/payment \\"
echo "    -H 'Authorization: Bearer YOUR_TOKEN' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"amount\": 1000, \"orderId\": \"test-$(date +%s)\"}'"
