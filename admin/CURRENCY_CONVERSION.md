# Автоматическая конвертация валюты RUB -> UZS

## Описание

Модуль для автоматической конвертации рублей в узбекские сумы через API multitransfer.ru.

## Как это работает

1. **Заявка приходит в рублях** (например, 5000 RUB)
2. **Конвертация через API multitransfer.ru**:
   - Запрос к `https://api.multitransfer.ru/anonymous/multi/multitransfer-fee-calc/v3/commissions`
   - Получаем актуальный курс и сумму в UZS
3. **Создание платежа в UZS** через PayzTeam или другой провайдер

## API Endpoint

### POST /api/convert-currency

Конвертирует рубли в узбекские сумы.

**Request:**
```json
{
  "amount_rub": 5000
}
```

**Response:**
```json
{
  "success": true,
  "amount_rub": 5000.0,
  "amount_uzs": 758950.0,
  "exchange_rate": 151.79,
  "commission": {
    "amount": 50.0,
    "currency": "RUB"
  }
}
```

## Использование в коде

### Python (синхронный)

```python
from currency_converter import CurrencyConverter

converter = CurrencyConverter()
result = converter.convert_rub_to_uzs(5000.0)

if result:
    print(f"{result['amount_rub']} RUB = {result['amount_uzs']} UZS")
    print(f"Курс: {result['exchange_rate']}")
```

### Python (асинхронный)

```python
from currency_converter import CurrencyConverter
import asyncio

async def convert():
    converter = CurrencyConverter()
    result = await converter.convert_rub_to_uzs_async(5000.0)
    
    if result:
        print(f"{result['amount_rub']} RUB = {result['amount_uzs']} UZS")

asyncio.run(convert())
```

### HTTP API

```bash
curl -X POST http://localhost:5001/api/convert-currency \
  -H "Content-Type: application/json" \
  -d '{"amount_rub": 5000}'
```

## Интеграция с платежной системой

### Вариант 1: Конвертация перед созданием платежа

```python
# 1. Получаем заявку в рублях
amount_rub = 5000

# 2. Конвертируем в UZS
converter = CurrencyConverter()
conversion = converter.convert_rub_to_uzs(amount_rub)

if conversion:
    amount_uzs = conversion['amount_uzs']
    
    # 3. Создаем платеж в UZS
    payment_result = create_payment(
        amount=amount_uzs,
        currency='UZS'
    )
```

### Вариант 2: Автоматическая конвертация в API

Модифицируйте endpoint `/api/payment` для автоматической конвертации:

```python
@app.route('/api/payment', methods=['POST'])
def create_payment():
    data = request.get_json()
    amount_rub = data.get('amount')
    
    # Конвертируем в UZS
    converter = CurrencyConverter()
    conversion = converter.convert_rub_to_uzs(amount_rub)
    
    if not conversion:
        return jsonify({'error': 'Currency conversion failed'}), 500
    
    amount_uzs = conversion['amount_uzs']
    
    # Создаем платеж в UZS
    result = create_payment_in_uzs(amount_uzs)
    
    return jsonify({
        'success': True,
        'amount_rub': amount_rub,
        'amount_uzs': amount_uzs,
        'exchange_rate': conversion['exchange_rate'],
        'payment_result': result
    })
```

## Тестирование

Запустите тестовый скрипт:

```bash
cd admin
python test_currency_converter.py
```

Ожидаемый вывод:
```
============================================================
🔄 Тест конвертации валюты RUB -> UZS
============================================================

💰 Конвертирую 1000 RUB...
✅ Успешно:
   1000.0 RUB = 151790.0 UZS
   Курс: 151.79

💰 Конвертирую 2500 RUB...
✅ Успешно:
   2500.0 RUB = 379475.0 UZS
   Курс: 151.79

...
```

## Пример использования в боте

```python
# В handlers_public.py

from currency_converter import CurrencyConverter

async def handle_payment(message, amount_rub):
    # Конвертируем в UZS
    converter = CurrencyConverter()
    conversion = await converter.convert_rub_to_uzs_async(amount_rub)
    
    if not conversion:
        await message.answer("❌ Ошибка конвертации валюты")
        return
    
    amount_uzs = conversion['amount_uzs']
    exchange_rate = conversion['exchange_rate']
    
    # Показываем пользователю
    await message.answer(
        f"💰 Сумма к оплате:\n"
        f"   {amount_rub} RUB = {amount_uzs} UZS\n"
        f"   Курс: {exchange_rate}"
    )
    
    # Создаем платеж в UZS
    payment_result = await create_payment_uzs(amount_uzs)
```

## Структура ответа API multitransfer.ru

```json
{
  "money": {
    "acceptedMoney": {
      "amount": 5000,
      "currencyCode": "RUB"
    },
    "withdrawMoney": {
      "amount": 758950,
      "currencyCode": "UZS"
    }
  },
  "commission": {
    "amount": 50,
    "currencyCode": "RUB"
  }
}
```

## Обработка ошибок

```python
converter = CurrencyConverter()
result = converter.convert_rub_to_uzs(5000)

if result is None:
    # Обработка ошибки
    print("Ошибка конвертации:")
    print("- Проверьте интернет-соединение")
    print("- API multitransfer.ru может быть недоступен")
    print("- Проверьте формат запроса")
else:
    # Успешная конвертация
    print(f"Конвертировано: {result['amount_uzs']} UZS")
```

## Зависимости

```
httpx>=0.24.0
```

Установка:
```bash
pip install httpx
```

## Примечания

- API multitransfer.ru не требует авторизации для расчета комиссий
- Курс обновляется в реальном времени
- Рекомендуется кэшировать результаты на 1-5 минут для снижения нагрузки
- Timeout по умолчанию: 10 секунд
