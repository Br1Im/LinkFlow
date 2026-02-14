# Интеграция H2H API для получения реквизитов

## Описание

Новый сервис для получения реквизитов через H2H API. Старый сервис (PayzTeam) закомментирован, но сохранен для возможного использования в будущем.

## Быстрый старт

### 1. Настройка конфигурации

Откройте файл `admin/payment_service/requisite_config.py` и укажите реальные значения:

```python
# Конфигурация H2H API
H2H_CONFIG = {
    'base_url': 'https://your-api-url.com',  # Замените на реальный URL
    'access_token': 'your_access_token',      # Токен из админки
    'merchant_id': 'your_merchant_uuid',      # UUID мерчанта
    'currency': 'rub',
    'payment_detail_type': 'card'
}
```

### 2. Тестирование

Запустите тестовый скрипт для проверки интеграции:

```bash
cd admin
python test_h2h_api.py
```

Скрипт выполнит 10 запросов с суммами от 1000 до 5000 рублей.

## Переключение между сервисами

В файле `requisite_config.py` измените значение:

```python
# Для использования H2H API (новый сервис)
ACTIVE_REQUISITE_SERVICE = 'h2h'

# Для использования PayzTeam API (старый сервис)
ACTIVE_REQUISITE_SERVICE = 'payzteam'
```

## Структура файлов

```
admin/payment_service/
├── h2h_api.py              # Клиент H2H API
├── payzteam_api.py         # Клиент PayzTeam API (старый)
├── requisite_config.py     # Конфигурация сервисов
└── ...

admin/
├── test_h2h_api.py         # Тест H2H API (10 запросов)
└── H2H_INTEGRATION.md      # Эта документация
```

## API H2H - Основные методы

### Создание заказа

```python
from h2h_api import H2HAPI

api = H2HAPI(
    base_url="https://api.example.com",
    access_token="your_token"
)

result = api.create_order(
    external_id="ORDER_123",
    amount=1000,
    merchant_id="merchant_uuid",
    currency="rub",
    payment_detail_type="card"
)

if result.get("success"):
    data = result["data"]
    payment_detail = data["payment_detail"]
    
    print(f"Карта: {payment_detail['detail']}")
    print(f"Владелец: {payment_detail['initials']}")
```

### Получение информации о заказе

```python
order_info = api.get_order(order_id="order_uuid")
```

### Отмена заказа

```python
cancel_result = api.cancel_order(order_id="order_uuid")
```

## Использование в payment_service

Функция `get_payzteam_requisite()` автоматически использует активный сервис из конфигурации:

```python
from payzteam_api import get_payzteam_requisite

# Получить реквизиты (автоматически использует H2H или PayzTeam)
requisite = get_payzteam_requisite(amount=5000)

if requisite:
    print(f"Карта: {requisite['card_number']}")
    print(f"Владелец: {requisite['card_owner']}")
```

## Формат ответа

### H2H API

```json
{
  "card_number": "1000200030004000",
  "card_owner": "Иван Иванов",
  "order_id": "uuid",
  "amount": 1000,
  "payment_gateway": "sberbank_rub",
  "expires_at": 1731375451
}
```

### PayzTeam API (старый)

```json
{
  "card_number": "5614682414447872",
  "card_owner": "Ziedullo Goziev",
  "bank": "Trast Bank",
  "deal_id": 100
}
```

## Параметры запроса

### Обязательные

- `external_id` - Уникальный ID заказа на вашей стороне
- `amount` - Сумма заказа (целое число)
- `merchant_id` - UUID мерчанта

### Опциональные

- `currency` - Код валюты (rub, kzt и т.д.)
- `pay_gateway` - Код платежного метода
- `payment_detail_type` - Тип реквизита (card, phone, account_number, qr_code)
- `client_id` - ID клиента (для контрагентов)
- `callback_url` - URL для callback уведомлений
- `payer_bank` - Банк плательщика (для deeplinks)

## Статусы заказа

### Основные статусы

- `success` - Операция успешно завершена
- `pending` - Операция в ожидании
- `fail` - Операция завершилась неудачно

### Подстатусы

- `accepted` - Закрыт вручную
- `successfully_paid` - Закрыт автоматически
- `waiting_for_payment` - Ждет платежа
- `expired` - Отменен по истечению времени
- `cancelled` - Отменен вручную

## Обработка ошибок

```python
result = api.create_order(...)

if not result.get("success"):
    error = result.get("error", "Unknown error")
    print(f"Ошибка: {error}")
    
    # HTTP 422 - Ошибка валидации
    if "errors" in result:
        for field, messages in result["errors"].items():
            print(f"{field}: {messages}")
    
    # HTTP 400 - Ошибка бизнес-логики
    if "message" in result:
        print(f"Сообщение: {result['message']}")
```

## Таймауты

По умолчанию система ждет 30 секунд. Можно изменить через заголовок:

```python
result = api.create_order(
    ...,
    max_wait_ms=10000  # 10 секунд
)
```

## Callback уведомления

При изменении статуса заказа на указанный `callback_url` будет отправлен POST-запрос с данными заказа.

## Примечания

- Старый сервис (PayzTeam) сохранен и может быть активирован в любой момент
- Конфигурация централизована в `requisite_config.py`
- Все запросы логируются для отладки
- Поддержка deeplinks для iOS/Android (если указан `payer_bank`)

## Поддержка

При возникновении проблем проверьте:

1. Правильность токена доступа (`Access-Token`)
2. Корректность `merchant_id`
3. Доступность API (`base_url`)
4. Логи в консоли для детальной информации об ошибках
