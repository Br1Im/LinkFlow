# Playwright метод

✅ Реализовано!

Playwright - современная альтернатива Selenium с лучшей производительностью.

## Преимущества
- ⚡ Быстрее чем Selenium (~30-60 сек вместо 2 минут)
- 🎯 Более надёжный (автоматические ожидания)
- 🚀 Лучше работает с современными веб-приложениями
- 📸 Встроенные скриншоты и видео

## Установка

```bash
pip install playwright
playwright install chromium
```

## Использование

### Вариант 1: Через Docker (рекомендуется)

```bash
docker-compose -f docker-compose.playwright.yml up --build
```

### Вариант 2: Локально

```python
from src.methods.playwright import MultitransferPayment
from src.sender_data import SENDER_DATA

payment = MultitransferPayment(sender_data=SENDER_DATA, headless=True, skip_bank_selection=True)
payment.login()

result = payment.create_payment(
    card_number="9860080323894719",
    owner_name="Nodir Asadullayev",
    amount=500
)

payment.close()
print(result)
```

### Вариант 3: Через админ-панель

Установи переменную окружения:
```bash
export PAYMENT_METHOD=playwright
docker-compose up
```

## Производительность

- Selenium: ~120 секунд (2 минуты)
- Playwright: ~30-60 секунд (ожидается)

## Особенности

- Использует Chromium вместо Chrome
- Автоматические ожидания элементов
- Лучше обрабатывает React компоненты
- Меньше потребление ресурсов
