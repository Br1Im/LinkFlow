# 🎯 Multitransfer API

Чистый API для создания QR-платежей через multitransfer.ru

## 📁 Файлы

- **`multitransfer_api.py`** - основной API класс
- **`requirements.txt`** - зависимости (только requests)
- **`README.md`** - эта инструкция

## 🚀 Использование

```python
from multitransfer_api import MultitransferAPI

# Получи токен из браузера (F12 → Network → fhptokenid)
token = "твой_токен_из_браузера"

# Создай API клиент
api = MultitransferAPI(token)

# Создай QR-платеж
qr_link = api.create_qr_payment(
    card_number="9860080323894719",
    recipient_name="Nodir Asadullayev",
    amount=110
)

print(qr_link)  # https://qr.nspk.ru/...
```

## 🔗 API методы

- `get_commissions(amount)` - получает commission_id
- `create_payment(commission_id, card, name)` - создает платеж  
- `get_qr_link(transaction_id)` - получает QR-ссылку
- `create_qr_payment(card, name, amount)` - полный процесс

## 💡 Получение токена

1. Открой https://multitransfer.ru/transfer/uzbekistan
2. F12 → Network
3. Заполни форму и реши капчу
4. Найди запрос к api.multitransfer.ru
5. Скопируй `fhptokenid` из заголовков

**Токен нужен для каждого нового платежа!**