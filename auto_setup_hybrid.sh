#!/bin/bash

echo "🚀 Автоматическая настройка гибридного webhook сервера..."
echo "================================================================"

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите скрипт с правами root: sudo ./auto_setup_hybrid.sh"
    exit 1
fi

# Переход в папку проекта
cd /root/LinkFlow

# Активация виртуального окружения
source webhook_env/bin/activate

echo "1️⃣ Остановка текущего сервиса..."
systemctl stop webhook.service

echo "2️⃣ Установка Xvfb для виртуального дисплея..."
apt update
apt install -y xvfb

echo "3️⃣ Создание скрипта запуска с виртуальным дисплеем..."
cat > /root/LinkFlow/start_webhook_with_display.sh << 'EOF'
#!/bin/bash
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
sleep 2
cd /root/LinkFlow
source webhook_env/bin/activate
python webhook_server_hybrid.py
EOF

chmod +x /root/LinkFlow/start_webhook_with_display.sh

echo "4️⃣ Обновление systemd сервиса..."
cat > /etc/systemd/system/webhook.service << 'EOF'
[Unit]
Description=Payment Webhook Server (Hybrid Automation)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/LinkFlow
Environment=PATH=/root/LinkFlow/webhook_env/bin:/usr/bin:/usr/local/bin
Environment=WEBHOOK_API_TOKEN=-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo
ExecStart=/root/LinkFlow/start_webhook_with_display.sh
Restart=always
RestartSec=10
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30

StandardOutput=journal
StandardError=journal
SyslogIdentifier=webhook-server

[Install]
WantedBy=multi-user.target
EOF

echo "5️⃣ Перезапуск systemd и запуск сервиса..."
systemctl daemon-reload
systemctl enable webhook.service
systemctl start webhook.service

echo "6️⃣ Ожидание запуска сервиса..."
sleep 5

echo "7️⃣ Проверка статуса сервиса..."
systemctl status webhook.service --no-pager

echo ""
echo "8️⃣ Тестирование API..."
sleep 3

# Health check
echo "🔍 Health check..."
curl -s http://localhost:5000/api/health | python3 -m json.tool

echo ""
echo "🔍 Тест создания платежа..."
curl -s -X POST http://localhost:5000/api/payment \
  -H "Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo" \
  -H "Content-Type: application/json" \
  -d '{"amount": 1000, "orderId": "test-auto-setup-123"}' | python3 -m json.tool

echo ""
echo "================================================================"
echo "✅ УСТАНОВКА ЗАВЕРШЕНА!"
echo "================================================================"
echo "🌐 API URL: http://85.192.56.74:5000/api/payment"
echo "🔑 Token: -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"
echo "📊 Статус: systemctl status webhook.service"
echo "📋 Логи: journalctl -u webhook.service -f"
echo "🧪 Тест: curl http://85.192.56.74:5000/api/health"
echo "================================================================"

# Показать последние логи
echo ""
echo "📋 Последние логи сервиса:"
journalctl -u webhook.service -n 20 --no-pager

echo ""
echo "🎯 Готово! Webhook сервер с автоматическим созданием платежей запущен!"