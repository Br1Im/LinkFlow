# API Endpoint: Create Bot Payment

## Описание
Универсальный endpoint для создания платежей через MulenPay для всех ботов. Каждый бот использует свои уникальные credentials (shopId, secret_key, private_key2).

## URL
```
POST /api/create-bot-payment/<bot_name>
```

## Поддерживаемые боты
- `nutrition` - Nutrition Bot (shopId: 280)
- `crypto` - Crypto Bot (shopId: 322)
- `ai` - AI Bot (shopId: 321)
- `fitvip` - FitVIP Bot (shopId: 320)

## Request

### Headers
```
Content-Type: application/json
```

### Body
```json
{
  "amount": 3000
}
```

### Параметры
- `amount` (required, integer): Сумма платежа в рублях (от 100 до 120000)

## Response

### Success (200)
```json
{
  "success": true,
  "qr_link": "https://qr.nspk.ru/...",
  "widget_url": "https://mulenpay.ru/payment/widget/UUID",
  "payment_id": "890311",
  "amount": 3000,
  "bot_name": "crypto"
}
```

### Error (400) - Invalid bot name
```json
{
  "success": false,
  "error": "Invalid bot name. Must be one of: nutrition, crypto, ai, fitvip"
}
```

### Error (400) - Missing amount
```json
{
  "success": false,
  "error": "amount is required"
}
```

### Error (400) - Invalid amount
```json
{
  "success": false,
  "error": "Amount must be between 100 and 120000 RUB"
}
```

### Error (500) - Payment creation failed
```json
{
  "success": false,
  "error": "Failed to create payment",
  "bot_name": "crypto"
}
```

## Примеры использования

### cURL
```bash
# Nutrition bot
curl -X POST http://85.192.56.74:5001/api/create-bot-payment/nutrition \
  -H "Content-Type: application/json" \
  -d '{"amount": 3500}'

# Crypto bot
curl -X POST http://85.192.56.74:5001/api/create-bot-payment/crypto \
  -H "Content-Type: application/json" \
  -d '{"amount": 3000}'

# AI bot
curl -X POST http://85.192.56.74:5001/api/create-bot-payment/ai \
  -H "Content-Type: application/json" \
  -d '{"amount": 4000}'

# FitVIP bot
curl -X POST http://85.192.56.74:5001/api/create-bot-payment/fitvip \
  -H "Content-Type: application/json" \
  -d '{"amount": 4500}'
```

### Python
```python
import requests

# Создать платеж для crypto bot
response = requests.post(
    'http://85.192.56.74:5001/api/create-bot-payment/crypto',
    json={'amount': 3000}
)

result = response.json()
if result['success']:
    print(f"QR Link: {result['qr_link']}")
    print(f"Widget URL: {result['widget_url']}")
    print(f"Payment ID: {result['payment_id']}")
else:
    print(f"Error: {result['error']}")
```

### JavaScript (fetch)
```javascript
// Создать платеж для ai bot
fetch('http://85.192.56.74:5001/api/create-bot-payment/ai', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ amount: 4000 })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('QR Link:', data.qr_link);
    console.log('Widget URL:', data.widget_url);
    console.log('Payment ID:', data.payment_id);
  } else {
    console.error('Error:', data.error);
  }
});
```

## Технические детали

### Bot Credentials
Каждый бот использует свои уникальные credentials для MulenPay API:

| Bot Name  | Shop ID | Secret Key (первые 16 символов) | Private Key2 (первые 16 символов) |
|-----------|---------|----------------------------------|-------------------------------------|
| nutrition | 280     | b48d74485fcf7b4a...              | nVT5DyeFCJGMe04T...                 |
| crypto    | 322     | 09a9972a4245b553...              | aFZRjeQm4YQcZpN1...                 |
| ai        | 321     | ff689d0f8856f0dd...              | NcvxkxQ1pdiV5Boo...                 |
| fitvip    | 320     | 3f1d3205d7b32543...              | Z1xK2O43vfGaFVLl...                 |

### Процесс создания платежа
1. Валидация bot_name (должен быть один из: nutrition, crypto, ai, fitvip)
2. Валидация amount (от 100 до 120000 RUB)
3. Получение credentials для выбранного бота
4. Создание платежа через MulenPay API с использованием credentials бота
5. Получение widget_url и payment_id
6. Запрос к `/sbp` endpoint для получения прямой QR-ссылки
7. Возврат результата с qr_link, widget_url, payment_id

### Отличия от /api/create-qr-payment
- `/api/create-qr-payment` - работает только с nutrition bot (shopId=280)
- `/api/create-bot-payment/<bot_name>` - универсальный endpoint для всех 4 ботов
- Оба endpoint возвращают одинаковый формат ответа

## Тестирование
Для тестирования всех ботов используйте скрипт:
```bash
ssh root@85.192.56.74 '/tmp/test_bot_payment_api.sh'
```

## Статус
✅ Реализовано и протестировано (21.02.2026)
✅ Все 4 бота успешно создают платежи
✅ QR-ссылки генерируются корректно
