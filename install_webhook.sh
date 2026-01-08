#!/bin/bash

# Скрипт автоматической установки webhook сервера

echo "🚀 Установка Webhook API сервера..."

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите скрипт с правами root: sudo ./install_webhook.sh"
    exit 1
fi

# Обновление системы
echo "📦 Обновление системы..."
apt update && apt upgrade -y

# Установка Python и pip
echo "🐍 Установка Python..."
apt install -y python3 python3-pip python3-venv

# Установка зависимостей
echo "📚 Установка зависимостей..."
pip3 install -r requirements.txt

# Создание пользователя для сервиса
echo "👤 Создание пользователя webhook..."
useradd -r -s /bin/false webhook || true

# Создание директорий
echo "📁 Создание директорий..."
mkdir -p /var/log/webhook
chown webhook:webhook /var/log/webhook

# Копирование файлов сервиса
echo "📋 Настройка systemd сервиса..."
cp webhook.service /etc/systemd/system/

# Обновление путей в сервисе
CURRENT_DIR=$(pwd)
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$CURRENT_DIR|g" /etc/systemd/system/webhook.service

# Генерация токена если не задан
if [ -z "$WEBHOOK_API_TOKEN" ]; then
    WEBHOOK_API_TOKEN=$(openssl rand -base64 32)
    echo "🔑 Сгенерирован токен: $WEBHOOK_API_TOKEN"
    echo "WEBHOOK_API_TOKEN=$WEBHOOK_API_TOKEN" >> .env
fi

# Обновление токена в сервисе
sed -i "s|Environment=WEBHOOK_API_TOKEN=.*|Environment=WEBHOOK_API_TOKEN=$WEBHOOK_API_TOKEN|g" /etc/systemd/system/webhook.service

# Перезагрузка systemd
systemctl daemon-reload

# Включение и запуск сервиса
echo "🔄 Запуск сервиса..."
systemctl enable webhook.service
systemctl start webhook.service

# Проверка статуса
sleep 2
if systemctl is-active --quiet webhook.service; then
    echo "✅ Сервис успешно запущен!"
    echo "📊 Статус: $(systemctl is-active webhook.service)"
    echo "🌐 URL: http://$(hostname -I | awk '{print $1}'):5000/api/payment"
    echo "🔑 Token: $WEBHOOK_API_TOKEN"
else
    echo "❌ Ошибка запуска сервиса"
    echo "📋 Логи:"
    journalctl -u webhook.service --no-pager -n 20
    exit 1
fi

# Настройка firewall
echo "🔥 Настройка firewall..."
ufw allow 5000/tcp || true

# Тестирование
echo "🧪 Тестирование API..."
sleep 3
python3 test_webhook.py

echo ""
echo "="*60
echo "✅ УСТАНОВКА ЗАВЕРШЕНА"
echo "="*60
echo "🌐 API URL: http://$(hostname -I | awk '{print $1}'):5000/api/payment"
echo "🔑 Token: $WEBHOOK_API_TOKEN"
echo "📊 Статус: systemctl status webhook.service"
echo "📋 Логи: journalctl -u webhook.service -f"
echo "🧪 Тест: python3 test_webhook.py"
echo "="*60