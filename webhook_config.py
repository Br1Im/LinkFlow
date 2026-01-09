# -*- coding: utf-8 -*-
"""
Конфигурация webhook сервера
"""

import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Настройки сервера
SERVER_HOST = '0.0.0.0'  # Доступен извне
SERVER_PORT = 5000       # Порт

# Безопасность - ЗАМЕНИТЕ НА ВАШ ТОКЕН
API_TOKEN = os.getenv('WEBHOOK_API_TOKEN', 'my-super-secret-token-2024')

# Реквизиты для платежей (обновлены)
CARD_NUMBER = "9860100126186921"
CARD_OWNER = "AVAZBEK ISAQOV"

# URL вашего сервера (замените на ваш домен/IP)
SERVER_URL = "http://85.192.56.74:5000"

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FILE = "webhook.log"

print(f"🔧 Конфигурация webhook сервера:")
print(f"   🌐 URL: {SERVER_URL}/api/payment")
print(f"   🔑 Token: {API_TOKEN}")
print(f"   💳 Card: {CARD_NUMBER}")
print(f"   👤 Owner: {CARD_OWNER}")