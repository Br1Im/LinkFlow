# 🚀 Quick Start Guide

## Что изменилось в версии 2.0

### ✅ Проблема решена
Сайт multitransfer.ru использует **React + MUI controlled inputs**. Стандартные методы Selenium не работали.

### 🔧 Решение
- React-safe ввод через JS события
- Правильная последовательность действий
- Универсальные helpers для MUI

## Быстрый запуск

### 1. Тест React-safe версии (рекомендуется)

```bash
cd LinkFlow/scripts
./test_react_safe.sh
```

### 2. Docker тест

```bash
cd LinkFlow
docker-compose up --build
```

### 3. Локальный тест

```bash
cd LinkFlow
pip install -r requirements.txt
python -m tests.test_local
```

## Использование в коде

```python
from src.multitransfer_payment import MultitransferPayment

# Инициализация
payment = MultitransferPayment()
payment.login()

# Создание платежа
result = payment.create_payment(
    card_number="8600123456789012",
    owner_name="TEST USER",
    amount=1000
)

# Результат
if result['success']:
    print(f"✅ Платеж создан!")
    print(f"🔗 Ссылка: {result['payment_link']}")
    print(f"📱 QR: {result['qr_base64']}")
else:
    print(f"❌ Ошибка: {result['error']}")

# Закрытие
payment.close()
```

## Что нового

### Новые модули

1. **mui_helpers.py** — helpers для MUI
   - `set_mui_input_value()` — React-safe ввод
   - `click_mui_element()` — React-safe клик
   - `wait_for_mui_button_enabled()` — ожидание активации

2. **debug_helpers.py** — отладка
   - `dump_dom_state()` — скриншот + HTML
   - `check_react_state()` — проверка React state
   - `wait_for_react_render()` — ожидание рендеринга

### Улучшения

- ✅ Код сокращён в 2 раза
- ✅ Надёжнее работает в headless
- ✅ Детальная отладка
- ✅ Правильная работа с React

## Debug

При проблемах проверяйте `/tmp/`:
- `debug_*_*.png` — скриншоты
- `debug_*_*.html` — HTML страницы

## Документация

- [REACT_MUI_FIX.md](docs/REACT_MUI_FIX.md) — подробное решение
- [CHANGELOG.md](CHANGELOG.md) — список изменений
- [README.md](README.md) — основная документация

## Поддержка

Если что-то не работает:
1. Проверьте debug файлы в `/tmp/`
2. Запустите с `--headless=false` для визуальной отладки
3. Посмотрите [REACT_MUI_FIX.md](docs/REACT_MUI_FIX.md)
