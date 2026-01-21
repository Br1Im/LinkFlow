# -*- coding: utf-8 -*-
"""
Конфигурация для MultiTransfer Payment System
"""

# URL
MULTITRANSFER_URL = "https://multitransfer.ru/"

# Таймауты (секунды)
PAGE_LOAD_TIMEOUT = 30
ELEMENT_WAIT_TIMEOUT = 20
BANK_LIST_WAIT_TIMEOUT = 60

# Тестовые данные
TEST_CARD_NUMBER = "9860080323894719"
TEST_OWNER_NAME = "Nodir Asadullayev"
TEST_AMOUNT = 1000

# Страна по умолчанию
DEFAULT_COUNTRY = "Узбекистан"

# Банк по умолчанию
DEFAULT_BANK = "Uzcard/Humo"

# Пути для скриншотов
SCREENSHOT_PATH = "/app/screenshots"
SCREENSHOT_PATH_LOCAL = "./screenshots"
