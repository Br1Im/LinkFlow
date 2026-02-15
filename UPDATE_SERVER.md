# Инструкция по обновлению сервера 85.192.56.74

## Шаг 1: Подключиться к серверу
```bash
ssh root@85.192.56.74
```

## Шаг 2: Перейти в директорию проекта
```bash
cd /root/LinkFlow
# или
cd ~/LinkFlow
```

## Шаг 3: Обновить код из Git
```bash
git pull origin main
```

## Шаг 4: Перезапустить сервисы

### Если используется systemd:
```bash
# Перезапуск API сервера (порт 5001)
sudo systemctl restart linkflow-api

# Перезапуск Admin панели (порт 5000)
sudo systemctl restart linkflow-admin

# Проверка статуса
sudo systemctl status linkflow-api
sudo systemctl status linkflow-admin
```

### Если запущено вручную через screen/tmux:
```bash
# Найти процессы
ps aux | grep "api_server.py"
ps aux | grep "admin_panel_db.py"

# Убить старые процессы
pkill -f api_server.py
pkill -f admin_panel_db.py

# Запустить заново
cd /root/LinkFlow/admin

# API сервер (порт 5001)
nohup python3 api_server.py > api_server.log 2>&1 &

# Admin панель (порт 5000)
nohup python3 admin_panel_db.py > admin_panel.log 2>&1 &
```

## Шаг 5: Проверить что всё работает

### Проверка API:
```bash
curl http://localhost:5001/health
```

### Проверка Admin панели:
```bash
curl http://localhost:5000/
```

### Тестовый запрос на создание платежа:
```bash
curl -X POST http://85.192.56.74/api/create-payment \
  -H "Content-Type: application/json" \
  -d '{"amount": 1100}'
```

## Шаг 6: Проверить логи (если есть проблемы)

### Логи через systemd:
```bash
sudo journalctl -u linkflow-api -n 50 --no-pager
sudo journalctl -u linkflow-admin -n 50 --no-pager
```

### Логи из файлов:
```bash
tail -f /root/LinkFlow/admin/api_server.log
tail -f /root/LinkFlow/admin/admin_panel.log
```

## Что изменилось в этом обновлении:

1. ✅ Добавлен эндпоинт `/api/create-payment` (алиас для `/api/payment`)
2. ✅ Исправлена конвертация дат из ISO формата в dd.mm.yyyy
3. ✅ При ошибке API возвращает `card_number` и `card_owner` для отладки
4. ✅ Админка теперь передаёт параметр `requisite_api` в API сервер
5. ✅ Добавлено debug-логирование в admin_panel_db.py

## Проверка работы админки:

1. Открой http://85.192.56.74 в браузере
2. Попробуй создать платёж через форму
3. В консоли сервера (где запущен admin_panel_db.py) должны появиться строки:
   ```
   🔍 DEBUG: Отправка запроса на http://localhost:5001/api/payment для заказа ORD-...
   🔍 DEBUG: Payload: {'amount': 1100, 'orderId': 'ORD-...', 'requisite_api': 'auto'}
   🔍 DEBUG: Ответ от API - Status: 201, Time: 21.50s
   ```

## Если что-то не работает:

Запусти скрипт проверки:
```bash
cd /root/LinkFlow/admin
python3 check_api_simple.py
```
