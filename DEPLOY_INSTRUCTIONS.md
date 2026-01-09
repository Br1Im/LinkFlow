# ИНСТРУКЦИИ ПО РАЗВЕРТЫВАНИЮ CURL-СОВМЕСТИМОГО СЕРВЕРА

## Проблема
- fetch из браузера работает (браузер уже прогрет)
- curl не работает (каждый запрос запускает новый браузер, который падает)

## Решение
Развернуть новый сервер `webhook_server_curl_compatible.py` который НЕ использует браузер

## Команды для выполнения на сервере:

```bash
# 1. Подключиться к серверу
ssh root@85.192.56.74

# 2. Остановить старый сервис
sudo systemctl stop webhook

# 3. Скопировать новый файл (выполнить на локальной машине)
scp webhook_server_curl_compatible.py root@85.192.56.74:/home/
scp bot/webhook_config.py root@85.192.56.74:/home/bot/
scp bot/database.py root@85.192.56.74:/home/bot/

# 4. Обновить systemd сервис (на сервере)
sudo tee /etc/systemd/system/webhook.service > /dev/null << 'EOF'
[Unit]
Description=LinkFlow Webhook Server (CURL Compatible)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home
ExecStart=/usr/bin/python3 /home/webhook_server_curl_compatible.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/home
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 5. Перезагрузить systemd и запустить
sudo systemctl daemon-reload
sudo systemctl start webhook
sudo systemctl enable webhook

# 6. Проверить статус
sudo systemctl status webhook

# 7. Проверить логи
sudo journalctl -u webhook -f

# 8. Тест curl
curl -X POST "http://85.192.56.74:5000/api/payment" \
  -H "Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "orderId": "test-curl-123"}'
```

## Что изменится:
- ✅ curl запросы будут работать
- ✅ fetch из браузера продолжит работать  
- ✅ Быстрые ответы (без браузера)
- ✅ Реальные NSPK ссылки
- ✅ Стабильная работа на хостинге