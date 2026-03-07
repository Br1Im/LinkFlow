"""
Конфигурация для тестирования multitransfer.ru
"""

# URL для тестирования
MULTITRANSFER_URL = "https://multitransfer.ru/transfer/abkhazia"

# Настройки браузера
BROWSER_CONFIG = {
    'headless': False,  # True для headless режима
    'viewport': {'width': 1920, 'height': 1080},
    'timeout': 30000,
    'args': [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor'
    ]
}

# Тестовые данные
TEST_DATA = {
    'amount': 1000,
    'currency_from': 'RUB',
    'currency_to': 'USD'
}

# Селекторы для поиска элементов
SELECTORS = {
    'amount_input': [
        'input[name*="amount"]',
        'input[id*="amount"]',
        'input[placeholder*="сумм"]',
        'input[placeholder*="Сумм"]',
        'input[type="number"]',
        '.amount input',
        '#amount'
    ],
    'currency_from': [
        'select[name*="from"]',
        'select[id*="from"]',
        '.currency-from select',
        '#currency_from'
    ],
    'currency_to': [
        'select[name*="to"]',
        'select[id*="to"]',
        '.currency-to select',
        '#currency_to'
    ],
    'submit_button': [
        'button[type="submit"]',
        'input[type="submit"]',
        'button:contains("Перевести")',
        'button:contains("Отправить")',
        '.submit-btn',
        '#submit'
    ]
}

# Настройки логирования
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'filename': 'multitransfer_test.log'
}