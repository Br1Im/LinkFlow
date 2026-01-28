# 🎯 Multitransfer API - Полное API решение

Чистый API для создания QR-платежей через multitransfer.ru

## 📁 Структура

- **`multitransfer_api.py`** - базовый API класс (100% рабочий)
- **`auto_captcha_api.py`** - интеграция с solver'ом капчи
- **`get_fresh_token.py`** - получение токена вручную для теста
- **`captcha_solver_lib/`** - Docker solver для Yandex SmartCaptcha
- **`requirements.txt`** - зависимости (только requests)

## ✅ Что работает

### 1. API для создания платежей (100% рабочий)

```python
from multitransfer_api import MultitransferAPI

# Нужен свежий токен (получить вручную или через сервис)
token = "твой_fhptokenid"

api = MultitransferAPI(token)
qr_link = api.create_qr_payment(
    card_number="9860080323894719",
    recipient_name="Nodir Asadullayev",
    amount=110
)

print(qr_link)  # https://qr.nspk.ru/...
```

### 2. Методы API

- `get_commissions(amount)` - получает commission_id (БЕЗ токена)
- `create_payment(commission_id, card, name)` - создает платеж (нужен токен)
- `get_qr_link(transaction_id)` - получает QR-ссылку (БЕЗ токена)
- `create_qr_payment(card, name, amount)` - полный процесс (нужен токен)

## ⚠️ Проблема с автоматическим решением капчи

**yandex-captcha-puzzle-solver НЕ МОЖЕТ решить эту капчу:**
- Делает 200+ попыток за 5 минут
- Капча слишком сложная для автоматического решения
- Timeout даже с maxTimeout=300000 (5 минут)

## 🔑 Получение токена

### Вариант 1: Вручную (для тестирования)

```bash
python3 get_fresh_token.py
```

Следуй инструкциям:
1. Открой https://multitransfer.ru/transfer/uzbekistan
2. F12 → Network
3. Заполни форму и реши капчу
4. Найди запрос к `transfers/create`
5. Скопируй `fhptokenid` из Headers

### Вариант 2: Через платные сервисы (для продакшена)

Эти сервисы поддерживают Yandex SmartCaptcha:

1. **anticaptcha.com** (~$0.003-0.01 за капчу)
2. **capmonster.cloud** (~$0.003-0.01 за капчу)
3. **rucaptcha.com** (~$0.003-0.01 за капчу)

Параметры для сервисов:
```python
{
    "type": "YandexSmartCaptcha",
    "websiteURL": "https://multitransfer.ru/transfer/uzbekistan/sender-details",
    "websiteKey": "ysc1_DAo8nFPdNCMHkAwYxIUJFxW5IIJd3ITGArZehXxO9a0ea6f8"
}
```

Результат - это и есть `fhptokenid` для API.

### Вариант 3: Интеграция с anticaptcha

```python
from anticaptchaofficial.yandexsmartcaptchaproxyless import *
from multitransfer_api import MultitransferAPI

# Решаем капчу через anticaptcha
solver = yandexSmartCaptchaProxyless()
solver.set_key("твой_api_key")
solver.set_website_url("https://multitransfer.ru/transfer/uzbekistan/sender-details")
solver.set_website_key("ysc1_DAo8nFPdNCMHkAwYxIUJFxW5IIJd3ITGArZehXxO9a0ea6f8")

token = solver.solve_and_return_solution()

# Используем токен для создания платежа
api = MultitransferAPI(token)
qr_link = api.create_qr_payment("9860080323894719", "Nodir Asadullayev", 110)
```

## 💡 Важно

- **Минимальная сумма**: 110 RUB
- **Токен живет**: ~25 минут
- **API работает**: 100% протестирован
- **Автоматический solver**: НЕ работает (капча слишком сложная)
- **Решение для продакшена**: использовать платные сервисы

## 🎯 Рекомендация для продакшена

```python
from anticaptchaofficial.yandexsmartcaptchaproxyless import *
from multitransfer_api import MultitransferAPI

def create_payment(card: str, name: str, amount: float):
    """Создание платежа с решением капчи через anticaptcha"""
    
    # 1. Решаем капчу
    solver = yandexSmartCaptchaProxyless()
    solver.set_key("твой_api_key")
    solver.set_website_url("https://multitransfer.ru/transfer/uzbekistan/sender-details")
    solver.set_website_key("ysc1_DAo8nFPdNCMHkAwYxIUJFxW5IIJd3ITGArZehXxO9a0ea6f8")
    
    token = solver.solve_and_return_solution()
    
    if not token:
        return None
    
    # 2. Создаем платеж
    api = MultitransferAPI(token)
    qr_link = api.create_qr_payment(card, name, amount)
    
    return qr_link
```

## 📊 Итог

✅ **API работает** - протестирован и готов к использованию  
❌ **Бесплатный solver** - не может решить эту капчу  
💰 **Платные сервисы** - единственное рабочее решение для автоматизации  
💵 **Стоимость** - ~$0.003-0.01 за одну капчу  

**API готов к продакшену с интеграцией anticaptcha/capmonster!** 🎉
