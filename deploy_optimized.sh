#!/bin/bash

echo "🚀 РАЗВЕРТЫВАНИЕ ОПТИМИЗИРОВАННОЙ СИСТЕМЫ ПЛАТЕЖЕЙ"
echo "=================================================="
echo "Цель: Ускорение до 8-12 секунд + поддержка частых запросов"
echo "=================================================="

# Подключаемся к серверу
SERVER="root@85.192.56.74"
SSH_KEY="$HOME/.ssh/linkflow_server_key"

# Функция для SSH с ключом
ssh_with_key() {
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$@"
}

# Функция для SCP с ключом  
scp_with_key() {
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "$@"
}

echo "📦 1. Копирование оптимизированных файлов на сервер..."

# Копируем оптимизированные файлы
scp_with_key bot/payment_service_ultra.py $SERVER:/app/bot/
scp_with_key bot/admin_panel_optimized.py $SERVER:/app/bot/
scp_with_key bot/optimized_browser_pool.py $SERVER:/app/bot/

echo "✅ Файлы скопированы"

echo "🔄 2. Остановка текущего контейнера..."
ssh_with_key $SERVER "docker stop linkflow-payment-prod || true"

echo "⏳ 3. Пауза 5 секунд для корректного завершения..."
sleep 5

echo "🏗️ 4. Создание бэкапа текущей версии..."
ssh_with_key $SERVER "
    if [ -f /app/bot/admin_panel.py ]; then
        cp /app/bot/admin_panel.py /app/bot/admin_panel_backup_$(date +%Y%m%d_%H%M%S).py
        echo '✅ Бэкап создан'
    fi
"

echo "🔧 5. Замена файлов на оптимизированные версии..."
ssh_with_key $SERVER "
    # Заменяем admin_panel на оптимизированную версию
    cp /app/bot/admin_panel_optimized.py /app/bot/admin_panel.py
    echo '✅ admin_panel.py заменен на оптимизированную версию'
    
    # Проверяем что файлы на месте
    ls -la /app/bot/payment_service_ultra.py
    ls -la /app/bot/admin_panel.py
    ls -la /app/bot/optimized_browser_pool.py
"

echo "🚀 6. Запуск оптимизированного контейнера..."
ssh_with_key $SERVER "
    cd /app
    docker-compose up -d
"

echo "⏳ 7. Ожидание запуска (15 секунд)..."
sleep 15

echo "🔍 8. Проверка статуса контейнера..."
ssh_with_key $SERVER "
    docker ps | grep linkflow-payment-prod
    echo ''
    echo '📊 Последние логи:'
    docker logs --tail 10 linkflow-payment-prod
"

echo "✅ 9. Проверка API..."
echo "🌐 Тестирую health endpoint..."

# Тестируем health endpoint
curl -s -H "Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo" \
     http://85.192.56.74:5001/api/health | python -m json.tool

echo ""
echo "🌐 Тестирую stats endpoint..."

# Тестируем stats endpoint  
curl -s -H "Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo" \
     http://85.192.56.74:5001/api/stats | python -m json.tool

echo ""
echo "=================================================="
echo "🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "=================================================="
echo "📊 Изменения:"
echo "   • Ускорены все таймауты в 2 раза"
echo "   • Убрана система очередей"
echo "   • Добавлена параллельная обработка"
echo "   • Уменьшен API таймаут до 15 секунд"
echo "   • Добавлена статистика в реальном времени"
echo ""
echo "🎯 Ожидаемые результаты:"
echo "   • Время ответа: 8-12 секунд (было 20-22)"
echo "   • Поддержка частых запросов (1-3s интервал)"
echo "   • Параллельная обработка до 5 запросов"
echo ""
echo "📋 Следующий шаг: Запустить тест частых запросов"
echo "   python test_high_frequency.py"