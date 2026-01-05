# -*- coding: utf-8 -*-
"""
Конфигурация бота
"""

import os

# Telegram
BOT_TOKEN = '8556732862:AAGIT_7dqSHeKJbSljE1FRf62Fy6u0t0t2A'

# Администраторы
SUPER_ADMIN_ID = 7036953540
ADDITIONAL_ADMIN_ID = 7468167524

# Лимиты платежей
MIN_AMOUNT = 1000
MAX_AMOUNT = 100000

# Таймауты (секунды)
BROWSER_TIMEOUT = 30
PAGE_LOAD_TIMEOUT = 20
ELEMENT_WAIT_TIMEOUT = 15

# Периодичность проверки аккаунтов (минуты)
ACCOUNT_CHECK_INTERVAL = 30

# Пути
PROFILE_BASE_PATH = os.path.abspath("profiles")
QR_TEMP_PATH = os.path.abspath("temp_qr")

# Создаем папки если их нет
os.makedirs(PROFILE_BASE_PATH, exist_ok=True)
os.makedirs(QR_TEMP_PATH, exist_ok=True)

# URL
ELECSNET_URL = 'https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment='
ELECSNET_BASE_URL = 'https://1.elecsnet.ru/NotebookFront/'
