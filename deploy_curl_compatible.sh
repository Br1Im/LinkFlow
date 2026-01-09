#!/bin/bash
# Развертывание CURL-совместимого webhook сервера

echo "🚀 Развертывание CURL-совместимого webhook сервера..."

# Остановка старого сервиса
echo "⏹️ Остановка старого сервиса..."
sudo systemctl stop webhook

# Копирование нового файла
echo "📁 Копирование нового сервера..."
cp webhook_server_curl_compatible.py /home/webhook_server_curl_compatible.py

# Обновление systemd сервиса
echo "🔧 Обновление systemd сервиса..."
sudo tee /etc/systemd/system/webhook.service > /dev/null << 'EOF'
[Unit]
Description=LinkFlow Webhook Server (CURL Compatible)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home
ExecStart=/usr/bin/python3 /home/webhook_server_curl_compatible.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/home
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd
echo "🔄 Перезагрузка systemd..."
sudo systemctl daemon-reload

# Запуск нового сервиса
echo "▶️ Запуск нового сервиса..."
sudo systemctl start webhook
sudo systemctl enable webhook

# Проверка статуса
echo "📊 Проверка статуса..."
sudo systemctl status webhook --no-pager

echo "✅ Развертывание завершено!"
echo "📡 API endpoint: http://85.192.56.74:5000/api/payment"
echo "🔑 Token: -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"
echo "🧪 Тест: curl -X POST \"http://85.192.56.74:5000/api/payment\" -H \"Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo\" -H \"Content-Type: application/json\" -d '{\"amount\": 100, \"orderId\": \"test-123\"}'"