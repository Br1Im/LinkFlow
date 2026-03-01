# Обновление кода на сервере 85.192.56.74

## Проблема
Endpoint `/api/create-bot-payment/<bot_name>` падает с ошибкой:
```
'NoneType' object has no attribute 'call_soon_threadsafe'
```

## Причина
Использовался `run_async()` для вызова `mp_client.create_payment()`, но `event_loop` был `None`.

## Решение
Заменили `run_async()` на `asyncio.run()` в файле `admin/api_server.py`.

## Как обновить сервер

### Вариант 1: Через Git (если используется)
```bash
ssh root@85.192.56.74
cd /path/to/LinkFlow
git pull
sudo systemctl restart linkflow-api
```

### Вариант 2: Копирование файла
```bash
# С локальной машины
scp admin/api_server.py root@85.192.56.74:/path/to/LinkFlow/admin/

# На сервере
ssh root@85.192.56.74
sudo systemctl restart linkflow-api
```

### Вариант 3: Ручное редактирование
```bash
ssh root@85.192.56.74
nano /path/to/LinkFlow/admin/api_server.py
```

Найти строку (около 1008):
```python
response = run_async(mp_client.create_payment(
```

Заменить на:
```python
# Создаем платеж (используем asyncio.run вместо run_async)
import asyncio
response = asyncio.run(mp_client.create_payment(
```

Сохранить и перезапустить сервис:
```bash
sudo systemctl restart linkflow-api
```

## Проверка
После обновления проверить:
```bash
curl --location '85.192.56.74:5001/api/create-bot-payment/crypto' \
--header 'Content-Type: application/json' \
--data '{"amount": 1544}'
```

Должен вернуть успешный ответ с `"success": true`.

## Изменённые файлы
- `admin/api_server.py` - исправлен endpoint `/api/create-bot-payment/<bot_name>`

## Дополнительные изменения (для реквизитов)
Также были внесены изменения для использования ТОЛЬКО H2H/PayzTeam API (без fallback на БД):
- `admin/api_server.py` - изменена логика получения реквизитов
- `admin/payment_service/payment_service.py` - убран fallback на БД

Если нужны эти изменения, обновите оба файла.
