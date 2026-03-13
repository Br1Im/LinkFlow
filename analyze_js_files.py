#!/usr/bin/env python3
"""
Анализ JavaScript файлов для понимания логики получения QR-кодов
"""

import requests
import re
import json

def analyze_js_files():
    """Анализируем JavaScript файлы"""
    print("🔍 Анализируем JavaScript файлы...")
    
    # Создаем новый платеж для получения актуальной страницы
    try:
        response = requests.post(
            "http://85.192.56.74:5001/api/create-bot-payment/bridgeapi",
            json={"amount": 100},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Ошибка создания платежа: {response.status_code}")
            return
            
        data = response.json()
        payment_url = data.get('payment_url')
        print(f"✅ Платеж создан: {payment_url}")
        
        # Получаем HTML страницы
        page_response = requests.get(payment_url, timeout=10)
        if page_response.status_code != 200:
            print(f"❌ Ошибка загрузки страницы: {page_response.status_code}")
            return
            
        html_content = page_response.text
        
        # Ищем все JavaScript файлы
        js_files = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', html_content)
        
        print(f"📄 Найдено JS файлов: {len(js_files)}")
        
        for js_file in js_files:
            if js_file.startswith('/'):
                js_url = f"https://gate.minopay.net{js_file}"
            else:
                js_url = js_file
                
            print(f"\n{'='*60}")
            print(f"🔍 Анализируем: {js_url}")
            
            try:
                js_response = requests.get(js_url, timeout=10)
                if js_response.status_code == 200:
                    js_content = js_response.text
                    print(f"📄 Размер: {len(js_content)} символов")
                    
                    # Ищем ключевые паттерны
                    patterns_to_find = {
                        "API URLs": [
                            r'["\']([^"\']*checkPaymentState[^"\']*)["\']',
                            r'["\']([^"\']*qrcode[^"\']*)["\']',
                            r'["\']([^"\']*qr\.nspk\.ru[^"\']*)["\']',
                        ],
                        "Fetch/AJAX calls": [
                            r'fetch\s*\(\s*["\']([^"\']+)["\']',
                            r'XMLHttpRequest.*open\s*\(\s*["\'][^"\']*["\'],\s*["\']([^"\']+)["\']',
                            r'\.get\s*\(\s*["\']([^"\']+)["\']',
                            r'\.post\s*\(\s*["\']([^"\']+)["\']',
                        ],
                        "URL construction": [
                            r'["\']([^"\']*\/pp\/[^"\']*)["\']',
                            r'["\']([^"\']*\/api\/[^"\']*)["\']',
                            r'["\']([^"\']*\/nova\/[^"\']*)["\']',
                        ],
                        "Parameters": [
                            r'checkPaymentState',
                            r'sign\s*[:=]',
                            r'nc\s*[:=]',
                            r'action\s*[:=]',
                        ]
                    }
                    
                    found_anything = False
                    
                    for category, patterns in patterns_to_find.items():
                        matches = []
                        for pattern in patterns:
                            pattern_matches = re.findall(pattern, js_content, re.IGNORECASE)
                            matches.extend(pattern_matches)
                        
                        if matches:
                            found_anything = True
                            print(f"\n✅ {category}:")
                            for match in set(matches):
                                print(f"   {match}")
                    
                    # Ищем функции, которые могут отвечать за получение QR
                    function_patterns = [
                        r'function\s+(\w*[Qq][Rr]\w*)\s*\(',
                        r'function\s+(\w*[Pp]ayment\w*)\s*\(',
                        r'function\s+(\w*[Cc]heck\w*)\s*\(',
                        r'(\w+)\s*:\s*function.*checkPaymentState',
                        r'(\w+)\s*:\s*function.*qrcode',
                    ]
                    
                    functions_found = []
                    for pattern in function_patterns:
                        matches = re.findall(pattern, js_content, re.IGNORECASE)
                        functions_found.extend(matches)
                    
                    if functions_found:
                        found_anything = True
                        print(f"\n✅ Функции связанные с QR/Payment:")
                        for func in set(functions_found):
                            print(f"   {func}")
                    
                    # Ищем конкретные строки кода
                    code_snippets = [
                        r'checkPaymentState.*?[;}]',
                        r'qrcode.*?[;}]',
                        r'fetch.*?checkPaymentState.*?\)',
                        r'XMLHttpRequest.*?checkPaymentState.*?\)',
                    ]
                    
                    for pattern in code_snippets:
                        matches = re.findall(pattern, js_content, re.IGNORECASE | re.DOTALL)
                        if matches:
                            found_anything = True
                            print(f"\n✅ Код с checkPaymentState/qrcode:")
                            for match in matches[:3]:  # Показываем только первые 3
                                clean_match = re.sub(r'\s+', ' ', match.strip())
                                print(f"   {clean_match[:100]}...")
                    
                    if not found_anything:
                        print("❌ Ничего интересного не найдено")
                        
                else:
                    print(f"❌ Ошибка загрузки JS: {js_response.status_code}")
                    
            except Exception as e:
                print(f"❌ Ошибка анализа {js_url}: {e}")
        
        # Дополнительно анализируем HTML на предмет встроенного JavaScript
        print(f"\n{'='*60}")
        print("🔍 Анализируем встроенный JavaScript в HTML...")
        
        # Ищем script теги с кодом
        script_blocks = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL | re.IGNORECASE)
        
        for i, script in enumerate(script_blocks):
            if len(script.strip()) > 50:  # Только значимые скрипты
                print(f"\n📄 Script block {i+1}:")
                print(f"   Размер: {len(script)} символов")
                
                # Ищем интересные паттерны в встроенном JS
                if 'checkPaymentState' in script or 'qrcode' in script or 'fetch' in script:
                    print(f"   ✅ Содержит интересные паттерны")
                    
                    # Показываем релевантные части
                    lines = script.split('\n')
                    for line_num, line in enumerate(lines):
                        if any(keyword in line.lower() for keyword in ['checkpaymentstate', 'qrcode', 'fetch', 'xmlhttprequest']):
                            print(f"   Строка {line_num+1}: {line.strip()}")
                
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")

if __name__ == "__main__":
    analyze_js_files()