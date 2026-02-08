# Интеграция с PayzTeam Exchange API (P2P)

## Описание

Интеграция с PayzTeam для создания P2P платежей (карта на карту).

## Конфигурация

### Мерчант
- **ID мерчанта**: 747
- **Email**: stasfrolif@gmail.com

### API ключи
Ключи находятся в личном кабинете PayzTeam:
1. Войдите в ЛК: https://payzteam.com
2. Перейдите в раздел **"Мой магазин"** → **"Ключи"**
3. Скопируйте:
   - **API ключ** (для заголовка X-Api-Key)
   - **Секретный ключ** (для подписи запросов)

### Установка ключей

Установите переменные окружения:

```bash
# Windows (PowerShell)
$env:PAYZTEAM_API_KEY="ваш_api_ключ"
$env:PAYZTEAM_SECRET_KEY="ваш_секретный_ключ"

# Linux/Mac
export PAYZTEAM_API_KEY="ваш_api_ключ"
export PAYZTEAM_SECRET_KEY="ваш_секретный_ключ"
```

Или замените значения в коде:
- `admin/payment_service/payzteam_api.py`
- `admin/payment_service/steps/step2_form.py`

## API Endpoints

### 1. Создание P2P платежа
**POST** `https://payzteam.com/exchange/create_deal_v2/{merchant_id}`

**Заголовки:**
```json
{
  "Content-Type": "application/json",
  "X-Api-Key": "ваш_api_ключ"
}
```

**Тело запроса:**
```json
{
  "client": "test@test.ru",
  "amount": "1000.00",
  "fiat_currency": "rub",
  "uuid": "UNIQUE_ID_123",
  "language": "ru",
  "payment_method": "c2c",
  "bank": "sber",
  "is_intrabank_transfer": false,
  "ip": "127.0.0.1",
  "sign": "sha1_подпись"
}
```

**Подпись (sign):**
```
sha1(client + uuid + amount + fiat_currency + payment_method + SecretKey)
```

**Ответ (успех):**
```json
{
  "id": 100,
  "status": 0,
  "success": true,
  "paymentInfo": {
    "card_number": "1234567890123456",
    "card_holder": "IVAN IVANOV",
    "amount": "1000.00",
    ...
  }
}
```

**Статусы платежа:**
- `0` - новая оплата
- `2` - время оплаты вышло
- `3` - ожидает обработки
- `4` - оплата успешно прошла
- `5` - отправка callback партнеру

### 2. Проверка статуса платежа
**POST** `https://payzteam.com/exchange/get`

**Тело запроса:**
```json
{
  "id": 100
}
```

### 3. Отмена платежа
**POST** `https://payzteam.com/exchange/cancel`

**Content-Type:** `application/x-www-form-urlencoded`

**Тело запроса:**
```
id=100
```

**Ответ:**
```json
{
  "success": true
}
```

## Параметры платежа

### payment_method (метод оплаты)
- `c2c` - С карты на карту
- `sbp` - СБП
- `qrcode` - Оплата по QR-коду
- `transgran_c2c` - Трансграничный с карты на карту
- `transgran_sbp` - Трансграничный СБП
- `abh_c2c` - Трансгран карта (v2)
- `abh_sbp` - Трансгран SBP (v2)
- `mob_com` - Мобильная коммерция
- `nspk` - Оплата по QR-коду

### bank (банк)
- `sber` - Сбербанк
- `tinkoff` - Тинькофф
- `vtb` - ВТБ
- `alfa` - Альфа-Банк

### fiat_currency (валюта)
- `rub` - Российский рубль
- `azn` - Азербайджанский манат
- `kzt` - Казахстанский тенге
- `try` - Турецкая лира

## Использование

### Тестирование API

```bash
# Установите ключи в файле
python admin/test_payzteam_exchange.py
```

### Использование в коде

```python
from payment_service.payzteam_api import PayzTeamAPI

# Инициализация
api = PayzTeamAPI(
    merchant_id="747",
    api_key="ваш_api_ключ",
    secret_key="ваш_секретный_ключ"
)

# Создание платежа
result = api.create_deal(
    amount=1000.00,
    uuid="UNIQUE_ORDER_123",
    client_email="client@example.com",
    payment_method="c2c",
    bank="sber"
)

if result.get("success"):
    deal_id = result["id"]
    payment_info = result["paymentInfo"]
    
    # Проверка статуса
    status = api.get_payment_status(deal_id)
    
    # Отмена платежа
    cancel = api.cancel_payment(deal_id)
```

## Интеграция в payment_service

Интеграция добавлена в `admin/payment_service/steps/step2_form.py`:

1. После успешного заполнения формы создается P2P платеж в PayzTeam
2. Получаются реквизиты для оплаты
3. Для тестовых платежей автоматически выполняется отмена

## Структура файлов

```
admin/
├── payment_service/
│   ├── payzteam_api.py          # Класс для работы с API
│   └── steps/
│       └── step2_form.py         # Интеграция в процесс оплаты
├── test_payzteam_exchange.py    # Тестовый скрипт
└── PAYZTEAM_INTEGRATION.md       # Эта документация
```

## Примечания

1. **API ключ** указывается в заголовке `X-Api-Key` (не Bearer!)
2. **Секретный ключ** используется только для генерации подписи (SHA1)
3. Подпись формируется по формуле: `sha1(client+uuid+amount+fiat_currency+payment_method+SecretKey)`
4. Для тестирования используйте метод `cancel_payment()` для отмены созданных платежей

## Документация

- Стандартное API: https://payzteam.com/api-for-developers
- H2H API: https://payzteam.com/payment-api
