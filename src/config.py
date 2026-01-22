# -*- coding: utf-8 -*-
"""
Конфигурация для LinkFlow
"""

# URL
MULTITRANSFER_URL = "https://multitransfer.ru/"

# Таймауты (секунды)
PAGE_LOAD_TIMEOUT = 30
ELEMENT_WAIT_TIMEOUT = 20

# Страна по умолчанию
DEFAULT_COUNTRY = "Узбекистан"

# Банк по умолчанию
DEFAULT_BANK = "Uzcard/Humo"

# Пути для скриншотов
SCREENSHOT_PATH = "/app/screenshots"
SCREENSHOT_PATH_LOCAL = "./screenshots"

# Пример данных отправителя (для тестов)
EXAMPLE_SENDER_DATA = {
    "passport_series": "1820",
    "passport_number": "657875",
    "passport_issue_date": "22.07.2020",
    "birth_country": "Россия",
    "birth_place": "камышин",
    "first_name": "Дмитрий",
    "last_name": "Непокрытый",
    "birth_date": "03.07.2000",
    "phone": "+79880260334",
    "registration_country": "Россия",
    "registration_place": "камышин"
}

# Режимы платёжки с разными лимитами
PAYMENT_MODES = {
    "standard": {
        "name": "Стандартный",
        "min_amount": 110,
        "max_amount": 120000,
        "description": "Обычный режим (110-120000 RUB)"
    },
    "fast": {
        "name": "Быстрый",
        "min_amount": 500,
        "max_amount": 50000,
        "description": "Быстрые переводы (500-50000 RUB)"
    },
    "test": {
        "name": "Тестовый",
        "min_amount": 110,
        "max_amount": 1000,
        "description": "Для тестирования (110-1000 RUB)"
    }
}

# Лимиты сумм по умолчанию (стандартный режим)
MIN_AMOUNT = PAYMENT_MODES["standard"]["min_amount"]
MAX_AMOUNT = PAYMENT_MODES["standard"]["max_amount"]

# Пример данных получателя (для тестов)
EXAMPLE_RECIPIENT_DATA = {
    "card_number": "9860080323894719",
    "owner_name": "Nodir Asadullayev",
    "amount": 500  # Минимум 110 RUB, максимум 120000 RUB
}
