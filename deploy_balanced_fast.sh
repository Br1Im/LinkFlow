#!/bin/bash
# Развертывание сбалансированной быстрой версии на хостинге

echo "🚀 Развертывание СБАЛАНСИРОВАННОЙ БЫСТРОЙ версии webhook сервера..."

# Остановка текущих процессов
echo "⏹️ Остановка текущих процессов..."
pkill -f "python.*webhook_server" || true
pkill -f "chrome" || true
pkill -f "chromedriver" || true
sleep 2

# Переход в директорию проекта
cd /root/LinkFlow || { echo "❌ Директория /root/LinkFlow не найдена"; exit 1; }

# Обновление файлов
echo "📁 Обновление файлов..."

# Создание резервной копии текущего сервера
if [ -f "bot/webhook_server.py" ]; then
    cp bot/webhook_server.py bot/webhook_server_backup_$(date +%Y%m%d_%H%M%S).py
    echo "✅ Резервная копия создана"
fi

# Замена основного сервера на сбалансированную версию
cp bot/webhook_server_balanced_fast.py bot/webhook_server.py
echo "✅ Основной сервер заменен на сбалансированную версию"

# Проверка зависимостей
echo "📦 Проверка зависимостей..."
pip3 install -r bot/requirements.txt

# Установка Chrome и ChromeDriver если нужно
echo "🌐 Проверка Chrome..."
if ! command -v google-chrome &> /dev/null; then
    echo "📥 Установка Chrome..."
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
    apt-get update
    apt-get install -y google-chrome-stable
fi

# Установка ChromeDriver
echo "🔧 Проверка ChromeDriver..."
if ! command -v chromedriver &> /dev/null; then
    echo "📥 Установка ChromeDriver..."
    CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%.*}")
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
    unzip /tmp/chromedriver.zip -d /tmp/
    mv /tmp/chromedriver /usr/local/bin/
    chmod +x /usr/local/bin/chromedriver
    rm /tmp/chromedriver.zip
fi

# Создание systemd сервиса
echo "⚙️ Создание systemd сервиса..."
cat > /etc/systemd/system/webhook-balanced-fast.service << EOF
[Unit]
Description=Webhook Balanced Fast Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/LinkFlow/bot
Environment=DISPLAY=:99
ExecStartPre=/bin/bash -c 'Xvfb :99 -screen 0 1920x1080x24 &'
ExecStart=/usr/bin/python3 webhook_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd и запуск сервиса
echo "🔄 Перезагрузка systemd..."
systemctl daemon-reload
systemctl enable webhook-balanced-fast.service

# Запуск виртуального дисплея для headless Chrome
echo "🖥️ Запуск виртуального дисплея..."
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
sleep 2

# Запуск сервиса
echo "🚀 Запуск сбалансированного быстрого сервера..."
systemctl start webhook-balanced-fast.service

# Проверка статуса
sleep 5
echo "📊 Проверка статуса сервиса..."
systemctl status webhook-balanced-fast.service --no-pager

# Проверка работы API
echo "🔍 Проверка работы API..."
sleep 10
curl -s -H "Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo" \
     http://localhost:5000/api/health | python3 -m json.tool || echo "⚠️ API пока не отвечает"

echo ""
echo "✅ Развертывание завершено!"
echo "📡 API endpoint: http://85.192.56.74:5000/api/payment"
echo "🔥 Warmup endpoint: http://85.192.56.74:5000/api/warmup"
echo "📊 Health endpoint: http://85.192.56.74:5000/api/health"
echo "🔑 Token: -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"
echo ""
echo "📋 Полезные команды:"
echo "   systemctl status webhook-balanced-fast.service  # Статус сервиса"
echo "   systemctl restart webhook-balanced-fast.service # Перезапуск"
echo "   journalctl -u webhook-balanced-fast.service -f  # Логи в реальном времени"
echo "   systemctl stop webhook-balanced-fast.service    # Остановка"
echo ""
echo "⚖️ СБАЛАНСИРОВАННАЯ БЫСТРАЯ ВЕРСИЯ РАЗВЕРНУТА!"
echo "🎯 Ожидаемое время создания платежей: 12-17 секунд"
echo "🔥 Браузер прогревается автоматически при запуске"