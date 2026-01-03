# Спецификация endpoint для приема платежных ссылок

## Описание

Ваша площадка должна создать endpoint, который будет принимать готовые платежные ссылки СБП от нашей системы.

---

## Endpoint

### `POST /api/payment/link`

Принимает готовую платежную ссылку для отображения пользователю.

---

## Формат запроса

```json
{
  "user_id": "12345",
  "amount": 5000,
  "payment_link": "https://qr.nspk.ru/BD10000PJLOME38O9ACAII3UDF78PCFM?type=02&bank=100000000100&sum=5000000&cur=RUB&crc=FF13",
  "qr_code_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "expires_at": "2026-01-01T23:30:00Z"
}
```

### Параметры

| Параметр | Тип | Описание |
|----------|-----|----------|
| `user_id` | string | ID пользователя на вашей площадке |
| `amount` | number | Сумма платежа в рублях |
| `payment_link` | string | Готовая ссылка СБП для оплаты |
| `qr_code_base64` | string | QR-код в формате base64 (опционально) |
| `expires_at` | string | Время истечения ссылки (ISO 8601) |

---

## Ожидаемый ответ

### Успешный ответ (200 OK)

```json
{
  "success": true,
  "message": "Payment link received"
}
```

### Ответ с ошибкой (400 Bad Request)

```json
{
  "success": false,
  "error": "Invalid user_id"
}
```