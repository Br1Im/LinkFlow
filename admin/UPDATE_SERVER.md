# Инструкция по обновлению на сервере 85.192.56.74

## Проблема
Сервер использует старый PayzTeam API вместо нового H2H API.

## Решение

### 1. Подключитесь к серверу
```bash
ssh root@85.192.56.74
```

### 2. Перейдите в директорию проекта
```bash
cd /path/to/LinkFlow  # Замените на реальный путь
```

### 3. Проверьте текущую конфигурацию
```bash
cat admin/payment_service/requisite_config.py | grep ACTIVE_REQUISITE_SERVICE
```

### 4. Обновите файл requisite_config.py

Откройте файл:
```bash
nano admin/payment_service/requisite_config.py
```

Убедитесь, что установлено:
```python
ACTIVE_REQUISITE_SERVICE = 'h2h'
```

И проверьте H2H_CONFIG:
```python
H2H_CONFIG = {
    'base_url': 'https://api.liberty.top',  # ВАЖНО: api.liberty.top
    'access_token': 'dtpf8uupsbhumevz4pz2jebrqzqmv62o',
    'merchant_id': 'd5c17c6c-dc40-428a-80e5-2ca01af99f68',
    'currency': 'rub',
    'payment_detail_type': 'card'
}
```

Сохраните (Ctrl+O, Enter, Ctrl+X)

### 5. Перезапустите сервис
```bash
# Если используется systemd
sudo systemctl restart linkflow

# Или если используется supervisor
sudo supervisorctl restart linkflow

# Или просто перезапустите процесс
pkill -f api_server.py
python3 admin/api_server.py &
```

### 6. Проверьте что работает
```bash
curl -X POST http://85.192.56.74:5000/api/create-payment \
  -H "Content-Type: application/json" \
  -d '{"amount": 1000}' \
  --max-time 60
```

Должны получить реквизиты от H2H API, а не ошибку "PayzTeam API не вернул реквизиты".

## Быстрая проверка конфигурации

Запустите на сервере:
```bash
cd /path/to/LinkFlow
python3 admin/check_config.py
```

Должно показать:
```
✅ Используется H2H API
   Base URL: https://api.liberty.top
```

## Если проблема остается

1. Проверьте что файл обновлен:
```bash
cat admin/payment_service/requisite_config.py
```

2. Проверьте логи:
```bash
tail -f /var/log/linkflow.log  # Или где у вас логи
```

3. Тестовый запрос напрямую:
```bash
cd /path/to/LinkFlow
python3 admin/test_integration_final.py
```
