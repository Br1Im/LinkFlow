#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Патч для добавления синхронизации в webhook сервер
"""

import re

# Читаем исходный файл
with open('/home/webhook_server_bot_logic_fixed.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Добавляем импорт threading
if 'import threading' not in content:
    content = content.replace('import logging', 'import logging\nimport threading')

# Добавляем глобальную блокировку после импортов
if 'request_lock = threading.Lock()' not in content:
    # Находим место после создания app
    app_pattern = r'(app = Flask\(__name__\).*?\n)'
    replacement = r'\1\n# Глобальная блокировка для синхронизации запросов\nrequest_lock = threading.Lock()\nlast_request_time = 0\n'
    content = re.sub(app_pattern, replacement, content, flags=re.DOTALL)

# Добавляем синхронизацию в create_payment
if 'with request_lock:' not in content:
    # Находим начало функции create_payment
    pattern = r'(@app\.route\(\'/api/payment\'.*?\ndef create_payment\(\):.*?\n)(.*?)(if request\.method == \'OPTIONS\':)'
    
    replacement = r'''\1    global last_request_time
    
    # СИНХРОНИЗАЦИЯ - обрабатываем запросы по очереди
    with request_lock:
        \3'''
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Добавляем отступы для всего содержимого функции
    lines = content.split('\n')
    in_function = False
    new_lines = []
    
    for line in lines:
        if 'def create_payment():' in line:
            in_function = True
            new_lines.append(line)
        elif in_function and line.startswith('def ') and 'create_payment' not in line:
            in_function = False
            new_lines.append(line)
        elif in_function and line.strip() and not line.startswith('    global') and not line.startswith('    # СИНХРОНИЗАЦИЯ') and not line.startswith('    with request_lock:'):
            new_lines.append('        ' + line)
        else:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)

# Добавляем паузу между запросами
pause_code = '''
            # Пауза между запросами для стабильности
            current_time = time.time()
            time_since_last = current_time - last_request_time
            if time_since_last < 2.0:  # Минимум 2 секунды между запросами
                sleep_time = 2.0 - time_since_last
                logger.info(f"⏳ Пауза {sleep_time:.1f}s для стабильности браузера...")
                time.sleep(sleep_time)
'''

if 'Пауза между запросами для стабильности' not in content:
    # Добавляем паузу перед созданием платежа
    pattern = r'(logger\.info\(f"Creating payment via BOT LOGIC:.*?\n)'
    replacement = r'\1' + pause_code + r'\1'
    content = re.sub(pattern, replacement, content)

# Обновляем last_request_time
if 'last_request_time = time.time()' not in content:
    pattern = r'(result = create_payment_fast\(amount, send_callback=None\))'
    replacement = r'\1\n            last_request_time = time.time()'
    content = re.sub(pattern, replacement, content)

# Сохраняем исправленный файл
with open('/home/webhook_server_bot_logic_fixed.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Патч применен успешно!")