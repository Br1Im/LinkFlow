# Деплой исправлений на хостинг

## Что исправлено

1. **Улучшенное нажатие кнопки "Оплатить"**:
   - Добавлено детальное логирование состояния кнопки
   - Три способа нажатия (JavaScript, обычный click, submit формы)
   - Проверка активации кнопки перед нажатием

2. **Правильная валидация суммы**:
   - Минимум 1000 рублей (требование elecsnet.ru)
   - Максимум 100000 рублей

## Шаги деплоя

### 1. Загрузка файлов на хостинг

```bash
# На локальной машине
scp webhook_server_production.py root@85.192.56.74:/root/
scp deploy_production_fix.sh root@85.192.56.74:/root/
```

### 2. Запуск деплоя на хостинге

```bash
# Подключаемся к хостингу
ssh root@85.192.56.74

# Делаем скрипт исполняемым
chmod +x deploy_production_fix.sh

# Запускаем деплой
./deploy_production_fix.sh
```

### 3. Проверка работы

```bash
# Смотрим логи в реальном времени
sudo journalctl -u webhook -f

# В другом терминале делаем тестовый запрос
curl -X POST http://localhost:5000/api/payment \
  -H 'Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo' \
  -H 'Content-Type: application/json' \
  -d '{"amount": 1000, "orderId": "test-'$(date +%s)'"}'
```

### 4. Проверка с внешнего IP

```bash
# С локальной машины
curl -X POST http://85.192.56.74:5000/api/payment \
  -H 'Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo' \
  -H 'Content-Type: application/json' \
  -d '{"amount": 1000, "orderId": "test-'$(date +%s)'"}'
```

## Что смотреть в логах

После деплоя в логах должно появиться:

```
[X.Xs] Проверяю состояние кнопки...
  - disabled: None
  - class: button
  - displayed: True
  - enabled: True
[X.Xs] Кнопка активна после 0 попыток
[X.Xs] Пробую нажать кнопку...
[X.Xs] ✓ JavaScript click выполнен
[X.Xs] Ожидаю результат...
```

## Откат изменений

Если что-то пошло не так:

```bash
# На хостинге
sudo systemctl stop webhook

# Восстанавливаем бэкап (найдите последний)
ls -la webhook_server_production.py.backup.*
cp webhook_server_production.py.backup.YYYYMMDD_HHMMSS webhook_server_production.py

# Запускаем
sudo systemctl start webhook
sudo systemctl status webhook
```

## Мониторинг

```bash
# Статус сервиса
sudo systemctl status webhook

# Логи за последний час
sudo journalctl -u webhook --since "1 hour ago"

# Логи с ошибками
sudo journalctl -u webhook -p err

# Логи в реальном времени
sudo journalctl -u webhook -f
```

## Тестирование

После деплоя протестируйте:

1. ✅ Создание платежа с суммой 1000 руб
2. ✅ Создание платежа с суммой 5000 руб
3. ❌ Попытка создать платеж с суммой 100 руб (должна вернуть ошибку)
4. ❌ Попытка создать платеж с суммой 150000 руб (должна вернуть ошибку)
5. ✅ Проверка, что QR код генерируется
6. ✅ Проверка, что ссылка на оплату работает

## Полезные команды

```bash
# Перезапуск сервиса
sudo systemctl restart webhook

# Просмотр конфигурации
sudo systemctl cat webhook

# Редактирование конфигурации
sudo systemctl edit webhook --full

# Проверка портов
sudo netstat -tulpn | grep 5000

# Проверка процессов
ps aux | grep webhook
```
