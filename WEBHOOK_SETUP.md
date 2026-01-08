# Настройка Webhook API для интеграции с платежной системой

## 📋 Что это?

Webhook сервер принимает POST запросы от платежной системы и создает QR-коды для оплаты через СБП.

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка конфигурации

Отредактируйте файл `webhook_config.py`:

```python
# Ваши реквизиты
CARD_NUMBER = "9860100125857258"  # Замените на ваш номер карты
CARD_OWNER = "IZZET SAMEKEEV"     # Замените на владельца карты

# URL вашего сервера
SERVER_URL = "http://85.192.56.74:5000"  # Замените на ваш IP/домен
```

### 3. Установка токена безопасности

```bash
export WEBHOOK_API_TOKEN="your-super-secure-token-here"
```

Или создайте файл `.env`:
```
WEBHOOK_API_TOKEN=your-super-secure-token-here
```

### 4. Запуск сервера

```bash
python webhook_server.py
```

## 🔧 Настройка как системный сервис

### 1. Копирование файла сервиса

```bash
sudo cp webhook.service /etc/systemd/system/
```

### 2. Редактирование сервиса

```bash
sudo nano /etc/systemd/system/webhook.service
```

Измените пути и токен:
```ini
WorkingDirectory=/path/to/your/bot
Environment=WEBHOOK_API_TOKEN=your-actual-token
```

### 3. Запуск сервиса

```bash
sudo systemctl daemon-reload
sudo systemctl enable webhook.service
sudo systemctl start webhook.service
```

### 4. Проверка статуса

```bash
sudo systemctl status webhook.service
sudo journalctl -u webhook.service -f
```

## 📡 API Endpoints

### Создание платежа

**POST** `/api/payment`

**Headers:**
```
Authorization: Bearer your-token
Content-Type: application/json
```

**Body:**
```json
{
    "amount": 100,
    "orderId": "order-id-hash"
}
```

**Response:**
```json
{
    "success": true,
    "orderId": "order-id-hash",
    "qrcId": "BR10006J6N78356E9GC8D5BANTAT1HIV",
    "qr": "https://qr.nspk.ru/..."
}
```

### Проверка статуса

**GET** `/api/status/{orderId}`

**Headers:**
```
Authorization: Bearer your-token
```

**Response:**
```json
{
    "success": true,
    "orderId": "order-id-hash",
    "status": "pending",
    "amount": 100,
    "createdAt": "2024-01-01T12:00:00"
}
```

### Health Check

**GET** `/api/health`

**Response:**
```json
{
    "success": true,
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00"
}
```

## 🧪 Тестирование

```bash
python test_webhook.py
```

## 🔒 Безопасность

1. **Используйте сильный токен** - минимум 32 символа
2. **HTTPS** - настройте SSL сертификат для продакшна
3. **Firewall** - ограничьте доступ к порту 5000
4. **Логирование** - мониторьте подозрительную активность

## 🌐 Настройка для продакшна

### Nginx как reverse proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### SSL сертификат

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 Мониторинг

### Логи сервиса

```bash
sudo journalctl -u webhook.service -f
```

### Логи приложения

```bash
tail -f webhook.log
```

## 🔧 Параметры для интеграции

**Ваши данные для настройки в платежной системе:**

- **URL:** `http://85.192.56.74:5000/api/payment`
- **Token:** `your-secure-token-here` (замените на ваш)
- **Method:** POST
- **Content-Type:** application/json

## ❓ Troubleshooting

### Сервер не запускается

1. Проверьте порт: `sudo netstat -tlnp | grep 5000`
2. Проверьте логи: `sudo journalctl -u webhook.service`
3. Проверьте права: `ls -la webhook_server.py`

### Ошибки авторизации

1. Проверьте токен в заголовке
2. Убедитесь что токен совпадает в конфиге
3. Проверьте формат: `Bearer your-token`

### Ошибки создания платежей

1. Проверьте реквизиты в `webhook_config.py`
2. Проверьте доступность elecsnet.ru
3. Проверьте логи fast_payment_api

## 📞 Поддержка

При возникновении проблем проверьте:
1. Логи сервиса
2. Статус сервиса
3. Доступность портов
4. Правильность конфигурации