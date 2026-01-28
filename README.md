# 🎯 Multitransfer API - Серверное решение

Чистый API БЕЗ браузера для автоматизации на сервере

## 📁 Файлы

- **`multitransfer_api.py`** - основной API класс (100% рабочий)
- **`example_usage.py`** - пример использования
- **`requirements.txt`** - зависимости (только requests)
- **`README.md`** - эта инструкция

## 🚀 Использование

```python
from multitransfer_api import MultitransferAPI

# Токен получаешь через решение капчи
token = "твой_fhptokenid"

api = MultitransferAPI(token)
qr_link = api.create_qr_payment(
    card_number="9860080323894719",
    recipient_name="Nodir Asadullayev",
    amount=110
)

print(qr_link)  # https://qr.nspk.ru/...
```

## 🔗 API методы

- `get_commissions(amount)` - получает commission_id (БЕЗ токена)
- `create_payment(commission_id, card, name)` - создает платеж (нужен токен)
- `get_qr_link(transaction_id)` - получает QR-ссылку (БЕЗ токена)
- `create_qr_payment(card, name, amount)` - полный процесс (нужен токен)

## 🔑 Получение токена

### Для автоматизации на сервере:

1. **anticaptcha.com** - поддерживает Yandex SmartCaptcha
2. **capmonster.cloud** - поддерживает Yandex SmartCaptcha
3. **rucaptcha.com** - поддерживает Yandex SmartCaptcha

### Параметры для сервисов:

```python
{
    "type": "YandexSmartCaptcha",
    "websiteURL": "https://multitransfer.ru/transfer/uzbekistan/sender-details",
    "websiteKey": "ysc1_DAo8nFPdNCMHkAwYxIUJFxW5IIJd3ITGArZehXxO9a0ea6f8"
}
```

Результат - это и есть `fhptokenid` для API.

### Вручную (для тестирования):

1. Открой https://multitransfer.ru/transfer/uzbekistan
2. Заполни форму и реши капчу
3. F12 → Network → найди запрос к api.multitransfer.ru
4. Скопируй `fhptokenid` из заголовков

## 💡 Важно

- **Минимальная сумма**: 110 RUB
- **Токен живет**: ~25 минут
- **Токен нужен**: только для создания платежа
- **Комиссии и QR**: работают БЕЗ токена
- **Стоимость капчи**: ~$0.003-0.01 в зависимости от сервиса

## 🎯 Для продакшена

```python
# 1. Получаешь токен через anticaptcha/capmonster
token = solve_captcha_via_service()

# 2. Создаешь платеж
api = MultitransferAPI(token)
qr_link = api.create_qr_payment(card, name, amount)

# 3. Возвращаешь QR-ссылку клиенту
return qr_link
```

Всё работает БЕЗ браузера на сервере! 🎉