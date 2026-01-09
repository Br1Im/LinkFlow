#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для добавления реквизитов и аккаунта в базу данных
"""

import sys
import os
sys.path.append('/home/bot')

from database import Database

db = Database()

# Добавляем реквизиты
db.add_requisite('9860100126186921', 'AVAZBEK ISAQOV')
print('✅ Реквизиты добавлены: 9860100126186921 AVAZBEK ISAQOV')

# Добавляем аккаунт
db.add_account('+79880260334', 'xowxut-wemhej-3zAsno')
print('✅ Аккаунт добавлен: +79880260334')

print('🚀 Данные готовы для работы webhook сервера!')