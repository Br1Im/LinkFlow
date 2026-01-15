#!/bin/bash

# Скрипт для деплоя ОПТИМИЗИРОВАННОЙ версии на сервер 85.192.56.74

SERVER="root@85.192.56.74"
REMOTE_PATH="/root/LinkFlow"

echo "⚡ ДЕПЛОЙ ОПТИМИЗИРОВАННОЙ ВЕРСИИ (цель < 10 сек)"
echo "=" | tr '=' '=' | head -c 80; echo

# 1. Копируем обновленные файлы
echo "📦 Копирование оптимизированных файлов..."

# Копируем payment_service.py (ГЛАВНЫЕ ОПТИМИЗАЦИИ)
echo "  - bot/payment_service.py (ОПТИМИЗИРОВАН)"
scp bot/payment_service.py $SERVER:$REMOTE_PATH/bot/

# Копируем browser_manager.py (ОПТИМИЗИРОВАН)
echo "  - bot/browser_manager.py (ОПТИМИЗИРОВАН)"
scp bot/browser_manager.py $SERVER:$REMOTE_PATH/bot/

# Копируем admin_panel.py
echo "  - bot/admin_panel.py"
scp bot/admin_panel.py $SERVER:$REMOTE_PATH/bot/

echo ""
echo "✅ Файлы скопированы"
echo ""

# 2. Перезапускаем Docker на сервере
echo "🔄 Перезапуск Docker контейнера..."
ssh $SERVER << 'ENDSSH'
cd /root/LinkFlow

echo "Останавливаем контейнер..."
docker-compose down

echo "Пересобираем образ с оптимизациями..."
docker-compose build --no-cache

echo "Запускаем контейнер..."
docker-compose up -d

echo "Ожидание запуска (20 секунд)..."
sleep 20

echo "Проверка статуса..."
docker ps | grep linkflow

echo "Последние логи:"
docker logs linkflow-payment-admin-1 --tail 50

ENDSSH

echo ""
echo "=" | tr '=' '=' | head -c 80; echo
echo "✅ ОПТИМИЗИРОВАННАЯ ВЕРСИЯ ЗАДЕПЛОЕНА!"
echo "⚡ Ожидаемая скорость: < 10 секунд на платеж"
echo "🌐 API: http://85.192.56.74:5001/api/payment"
echo ""
echo "Для тестирования:"
echo "  curl -X POST http://85.192.56.74:5001/api/payment \\"
echo "    -H 'Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"amount\": 1000, \"orderId\": \"test-speed-$(date +%s)\"}'"
echo ""
echo "Для просмотра логов:"
echo "  ssh $SERVER 'docker logs -f linkflow-payment-admin-1'"
