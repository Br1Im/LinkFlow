# 🎯 Чистый API для multitransfer.ru

Только 3 файла - минимум кода для работы с API.

## 📁 Файлы

- **`multitransfer_api.py`** - основной API класс
- **`example.py`** - пример использования  
- **`README.md`** - эта инструкция

## 🚀 Быстрый старт

### 1. Получи токен

1. Открой https://multitransfer.ru/transfer/uzbekistan
2. F12 → Network
3. Заполни форму (сумма 110+, карта любая)
4. Реши капчу (нажми на квадратик ☑️)
5. Найди запрос к `api.multitransfer.ru`
6. Скопируй `fhptokenid` из заголовков

### 2. Используй API

```python
from multitransfer_api import MultitransferAPI

api = MultitransferAPI("твой_токен")
qr_link = api.create_qr_payment("9860080323894719", "Nodir Asadullayev", 110)
print(qr_link)  # https://qr.nspk.ru/...
```

### 3. Запусти пример

```bash
python3 example.py
```

## 🔗 API методы

- `get_commissions(amount)` - получает commission_id
- `create_payment(commission_id, card, name)` - создает платеж  
- `get_qr_link(transaction_id)` - получает QR-ссылку
- `create_qr_payment(card, name, amount)` - полный процесс

## 💡 Важно

- **Минимальная сумма**: 110 RUB
- **Токен живет**: ~25 минут
- **Результат**: `https://qr.nspk.ru/...`

Всё! 🎉