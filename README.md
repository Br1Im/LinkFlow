# 💳 MultiTransfer Payment System

Автоматизированная система создания платежей через multitransfer.ru для карт Узбекистана.

## 📁 Структура проекта

```
LinkFlow/
├── src/                          # Исходный код
│   ├── __init__.py
│   ├── multitransfer_payment.py  # Модуль для multitransfer.ru (React-safe)
│   ├── payment_manager.py        # Менеджер платежей
│   ├── mui_helpers.py            # Helpers для MUI controlled inputs
│   └── debug_helpers.py          # Debug утилиты для React/MUI
├── tests/                        # Тесты
│   ├── __init__.py
│   ├── test_multitransfer.py     # Тест для Docker
│   └── test_local.py             # Локальный тест
├── scripts/                      # Скрипты запуска
│   ├── run_test.sh               # Запуск теста в Docker
│   ├── run_interactive.sh        # Интерактивный режим
│   └── test_react_safe.sh        # Тест React-safe версии
├── docs/                         # Документация
│   ├── README.md                 # Основная документация
│   ├── DOCKER_README.md          # Docker документация
│   └── REACT_MUI_FIX.md          # React + MUI решение
├── screenshots/                  # Скриншоты (создается автоматически)
├── Dockerfile                    # Docker образ
├── docker-compose.yml            # Docker Compose конфигурация
└── requirements.txt              # Python зависимости
```

## 🚀 Быстрый старт

### Вариант 1: Docker (рекомендуется)

```bash
cd scripts
./run_test.sh
```

### Вариант 2: React-safe тест

```bash
cd scripts
./test_react_safe.sh
```

### Вариант 3: Локально

```bash
pip install -r requirements.txt
python -m tests.test_local
```

## 📖 Документация

- [Основная документация](docs/README.md)
- [Docker документация](docs/DOCKER_README.md)

## 🔧 Требования

- Python 3.11+
- Docker & Docker Compose (для Docker варианта)
- Chrome браузер (для локального варианта)

## 📝 Использование

### Как модуль

```python
from src.multitransfer_payment import MultitransferPayment

payment = MultitransferPayment()
payment.login()

result = payment.create_payment(
    card_number="9860080323894719",
    owner_name="Nodir Asadullayev",
    amount=1000
)

print(result['payment_link'])
payment.close()
```

### Через менеджер

```python
from src.payment_manager import PaymentManager

manager = PaymentManager()
manager.initialize()

result = manager.create_payment(
    card_number="9860080323894719",
    owner_name="Nodir Asadullayev",
    amount=1000
)

manager.close()
```

## 🎯 Особенности

- ✅ **React-safe** — правильная работа с MUI controlled inputs
- ✅ Автоматический выбор страны (Узбекистан)
- ✅ Ввод суммы и выбор банка
- ✅ Поддержка Uzcard/Humo
- ✅ Получение QR-кода и ссылки
- ✅ Docker контейнер для изоляции
- ✅ Детальное логирование
- ✅ Скриншоты для отладки
- ✅ Debug helpers для React/MUI

## 🔥 React + MUI Fix

Сайт multitransfer.ru использует React + Material-UI. Стандартные методы Selenium не работают.

**Решение:**
- JS-события для ввода (input/change/blur)
- Ожидание активации кнопки "Продолжить"
- Правильная последовательность кликов

Подробнее: [docs/REACT_MUI_FIX.md](docs/REACT_MUI_FIX.md)

## 📊 Производительность

- Время создания платежа: ~40-60 секунд
- Headless режим в Docker
- Автоматическое управление браузером

## 🤝 Разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск локального теста
python -m tests.test_local

# Запуск Docker теста
cd scripts && ./run_test.sh

# Интерактивный режим
cd scripts && ./run_interactive.sh
```

## 📄 Лицензия

MIT
