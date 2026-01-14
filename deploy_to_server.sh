#!/bin/bash

# Скрипт для деплоя на сервер 85.192.56.74

SERVER="root@85.192.56.74"
REMOTE_PATH="/root/LinkFlow"

echo "🚀 Начинаю деплой на сервер $SERVER"
echo "=" | tr '=' '=' | head -c 80; echo

# 1. Копируем обновленные файлы
echo "📦 Копирование файлов..."

# Копируем admin_panel.py
echo "  - bot/admin_panel.py"
scp bot/admin_panel.py $SERVER:$REMOTE_PATH/bot/

# Копируем admin.html
echo "  - bot/templates/admin.html"
scp bot/templates/admin.html $SERVER:$REMOTE_PATH/bot/templates/

# Копируем docker-compose.yml (если изменился)
echo "  - docker-compose.yml"
scp docker-compose.yml $SERVER:$REMOTE_PATH/

# Копируем Dockerfile (если изменился)
echo "  - Dockerfile"
scp Dockerfile $SERVER:$REMOTE_PATH/

echo ""
echo "✅ Файлы скопированы"
echo ""

# 2. Перезапускаем Docker на сервере
echo "🔄 Перезапуск Docker контейнера на сервере..."
ssh $SERVER << 'ENDSSH'
cd /root/LinkFlow

echo "Останавливаем контейнер..."
docker-compose down

echo "Пересобираем образ..."
docker-compose build --no-cache

echo "Запускаем контейнер..."
docker-compose up -d

echo "Ожидание запуска (20 секунд)..."
sleep 20

echo "Проверка статуса..."
docker ps | grep linkflow

echo "Последние логи:"
docker logs linkflow-payment-admin-1 --tail 30

ENDSSH

echo ""
echo "=" | tr '=' '=' | head -c 80; echo
echo "✅ Деплой завершен!"
echo "🌐 Админка доступна на: http://85.192.56.74:5001"
echo ""
echo "Для просмотра логов:"
echo "  ssh $SERVER 'docker logs -f linkflow-payment-admin-1'"
