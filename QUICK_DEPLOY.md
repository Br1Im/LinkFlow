# Быстрый деплой на хостинг

## 1. Загрузка файлов (Windows)

Запустите:
```
upload_to_hosting.bat
```

Или вручную:
```bash
scp webhook_server_production.py root@85.192.56.74:/root/
scp deploy_production_fix.sh root@85.192.56.74:/root/
```

## 2. Деплой на хостинге

```bash
ssh root@85.192.56.74
chmod +x deploy_production_fix.sh
./deploy_production_fix.sh
```

## 3. Проверка

```bash
# Смотрим логи
sudo journalctl -u webhook -f
```

В другом терминале:
```bash
# Тестируем
python test_hosting_payment.py
```

## Что исправлено

✅ Улучшенное нажатие кнопки "Оплатить" (3 способа)
✅ Детальное логирование состояния кнопки
✅ Правильная валидация суммы (1000-100000 руб)
✅ Обработка всех возможных ошибок

## Быстрая проверка

```bash
curl -X POST http://85.192.56.74:5000/api/payment \
  -H 'Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo' \
  -H 'Content-Type: application/json' \
  -d '{"amount": 1000, "orderId": "test-'$(date +%s)'"}'
```

Должен вернуть JSON с `payment_link` и `qr_base64`.
