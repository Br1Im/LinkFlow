# 🚀 Руководство по развертыванию на хостинге

## 📋 Быстрое развертывание

### 1. Подключение к серверу
```bash
ssh root@85.192.56.74
```

### 2. Обновление кода
```bash
cd /root/LinkFlow
git pull
```

### 3. Обновление реквизитов
```bash
source webhook_env/bin/activate
python setup_new_requisites.py
```

### 4. Установка зависимостей
```bash
pip install flask-cors
```

### 5. Обновление webhook сервера
```bash
# Остановить текущий сервис
systemctl stop webhook.service

# Обновить скрипт запуска
cat > start_webhook_with_display.sh << 'EOF'
#!/bin/bash
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
sleep 2
cd /root/LinkFlow
source webhook_env/bin/activate
python webhook_server_bot_logic.py
EOF

chmod +x start_webhook_with_display.sh

# Перезапустить сервис
systemctl start webhook.service
```

### 6. Проверка работы
```bash
# Статус сервиса
systemctl status webhook.service

# Логи
journalctl -u webhook.service -f

# Тест API
curl -X POST http://85.192.56.74:5000/api/payment \
  -H "Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo" \
  -H "Content-Type: application/json" \
  -d '{"amount": 1000, "orderId": "test-new-requisites-123"}'
```

## 🔧 Обновленные данные

### Реквизиты
- **Карта:** 9860100126186921
- **Владелец:** AVAZBEK ISAQOV
- **Банк:** Kapitalbank (Humo)

### API данные
- **URL:** http://85.192.56.74:5000/api/payment
- **Token:** -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo

## 🎯 Особенности

1. **Использует логику бота** - webhook_server_bot_logic.py использует payment_service.py
2. **CORS включен** - работает с локальным фронтом
3. **Автоматическое создание QR** - через браузерную автоматизацию
4. **Сохранение заказов** - в базу данных для отслеживания

## 🧪 Тестирование

### Health Check
```bash
curl http://85.192.56.74:5000/api/health
```

### Создание платежа
```bash
curl -X POST http://85.192.56.74:5000/api/payment \
  -H "Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo" \
  -H "Content-Type: application/json" \
  -d '{"amount": 1500, "orderId": "test-deployment-123"}'
```

### Проверка статуса
```bash
curl -H "Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo" \
     http://85.192.56.74:5000/api/status/test-deployment-123
```

## 📊 Мониторинг

```bash
# Логи в реальном времени
journalctl -u webhook.service -f

# Статус всех сервисов
systemctl status webhook.service telegram-bot.service

# Проверка процессов
ps aux | grep webhook
ps aux | grep bot.py
```

## ❓ Troubleshooting

### Сервис не запускается
1. Проверить логи: `journalctl -u webhook.service -n 20`
2. Проверить файлы: `ls -la webhook_server_bot_logic.py`
3. Проверить права: `chmod +x start_webhook_with_display.sh`

### CORS ошибки
1. Убедиться что flask-cors установлен: `pip list | grep flask-cors`
2. Проверить что CORS настроен в коде
3. Тестировать через curl с заголовками Origin

### Ошибки создания платежей
1. Проверить реквизиты: `python setup_new_requisites.py`
2. Проверить браузер: `google-chrome --version`
3. Проверить Xvfb: `ps aux | grep Xvfb`

## 🎉 Готово!

После выполнения всех шагов webhook API будет работать с новыми реквизитами и использовать логику Telegram бота для создания реальных платежей.