#!/bin/bash
# Быстрое развертывание исправленного webhook сервера

echo "🚀 БЫСТРОЕ ИСПРАВЛЕНИЕ CURL ПРОБЛЕМЫ"
echo "=================================="

# Остановка сервиса
echo "⏹️ Остановка webhook сервиса..."
sudo systemctl stop webhook

# Копирование исправленного файла
echo "📁 Копирование исправленного сервера..."
cp webhook_server_curl_fixed.py /home/

# Обновление systemd сервиса
echo "🔧 Обновление systemd сервиса..."
sudo tee /etc/systemd/system/webhook.service > /dev/null << 'EOF'
[Unit]
Description=LinkFlow Webhook Server (CURL FIXED)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home
ExecStart=/usr/bin/python3 /home/webhook_server_curl_fixed.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/home:/home/bot
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка и запуск
echo "🔄 Перезагрузка systemd..."
sudo systemctl daemon-reload

echo "▶️ Запуск исправленного сервиса..."
sudo systemctl start webhook
sudo systemctl enable webhook

# Ожидание запуска
echo "⏳ Ожидание запуска сервиса..."
sleep 5

# Проверка статуса
echo "📊 Проверка статуса..."
sudo systemctl status webhook --no-pager -l

echo ""
echo "✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
echo "🧪 Тест curl:"
echo "curl -X POST \"http://85.192.56.74:5000/api/payment\" \\"
echo "  -H \"Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"amount\": 100, \"orderId\": \"curl-fix-test-123\"}'"