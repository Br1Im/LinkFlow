#!/bin/bash

echo "=== Проверка логов API сервера (порт 5001) ==="
echo ""

# Проверяем запущен ли API сервер
echo "1. Проверка процесса API сервера:"
ps aux | grep "api_server.py" | grep -v grep
echo ""

# Проверяем логи systemd если сервис запущен через systemd
echo "2. Последние 50 строк логов API сервера:"
if systemctl list-units --type=service | grep -q "linkflow-api"; then
    sudo journalctl -u linkflow-api -n 50 --no-pager
else
    echo "Сервис linkflow-api не найден в systemd"
fi
echo ""

# Проверяем логи admin панели (порт 5000)
echo "3. Последние 50 строк логов Admin панели:"
if systemctl list-units --type=service | grep -q "linkflow-admin"; then
    sudo journalctl -u linkflow-admin -n 50 --no-pager
else
    echo "Сервис linkflow-admin не найден в systemd"
fi
echo ""

# Проверяем доступность API
echo "4. Тест доступности API:"
curl -s http://localhost:5001/health | python3 -m json.tool || echo "API недоступен"
echo ""

# Проверяем nginx логи
echo "5. Последние 20 строк nginx error.log:"
sudo tail -n 20 /var/log/nginx/error.log
echo ""

echo "6. Последние 20 строк nginx access.log:"
sudo tail -n 20 /var/log/nginx/access.log
