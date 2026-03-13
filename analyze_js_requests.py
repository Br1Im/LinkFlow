#!/usr/bin/env python3
"""
Анализ JavaScript файлов для понимания AJAX запросов
"""

import requests
import re
import time

def analyze_js_files():
    """Анализируем JavaScript файлы с сайта"""
    
    # Создаем новый платеж для получения актуального URL
    print("🚀 Создаем новый платеж...")
    
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
        
    except Exception as e:
        print(f"❌ Ошибка создания платежа: {e}")
        return
    
    # Список JavaScript файлов для анализа
    js_files = [
        "/nova/js/sbp.js?v=20260120",
        "/nova/js/api.js?v=20260120",
        "/nova/js/qr-code.js?v=20260120"
    ]
    
    base_url = "https://gate.minopay.net"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/javascript, */*",
        "Referer": payment_url
    }
    
    for js_file in js_files:
        print(f"\n📜 Анализируем {js_file}...")
        
        try:
            js_url = f"{base_url}{js_file}"
            js_response = requests.get(js_url, headers=headers, timeout=10)
            
            if js_response.status_code != 200:
                print(f"❌ Ошибка загрузки {js_file}: {js_response.status_code}")
                continue
                
            js_content = js_response.text
            print(f"✅ Загружен {js_file}, размер: {len(js_content)} символов")
            
            # Сохраняем JS файл
            filename = js_file.split('/')[-1].split('?')[0]
            with open(f"debug_{filename}", 'w', encoding='utf-8') as f:
                f.write(js_content)
            print(f"💾 Сохранен как debug_{filename}")
            
            # Ищем интересные паттерны
            patterns = [
                r'checkPaymentState',
                r'fetch\([^)]+\)',
                r'XMLHttpRequest',
                r'qr\.nspk\.ru',
                r'sign["\']?\s*[:=]',
                r'spm_[a-z0-9]+',
                r'/pp/[^"\']+',
                r'action["\']?\s*[:=]\s*["\']qrcode["\']'
            ]
            
            print(f"🔍 Поиск паттернов в {filename}:")
            for pattern in patterns:
                matches = re.findall(pattern, js_content, re.IGNORECASE)
                if matches:
                    print(f"  {pattern}: {len(matches)} совпадений")
                    for match in matches[:3]:  # Показываем первые 3
                        print(f"    {match}")
            
            # Ищем функции, которые могут делать AJAX запросы
            function_patterns = [
                r'function\s+\w*[Cc]heck\w*\([^)]*\)\s*{[^}]*}',
                r'function\s+\w*[Qq][Rr]\w*\([^)]*\)\s*{[^}]*}',
                r'function\s+\w*[Pp]ayment\w*\([^)]*\)\s*{[^}]*}',
                r'setInterval\([^)]+\)',
                r'setTimeout\([^)]+\)'
            ]
            
            print(f"🔧 Поиск функций в {filename}:")
            for pattern in function_patterns:
                matches = re.findall(pattern, js_content, re.IGNORECASE | re.DOTALL)
                if matches:
                    print(f"  {pattern.split('\\')[0]}: {len(matches)} совпадений")
                    for match in matches[:1]:  # Показываем первую
                        preview = match[:200] + "..." if len(match) > 200 else match
                        print(f"    {preview}")
                        
        except Exception as e:
            print(f"❌ Ошибка анализа {js_file}: {e}")

def try_manual_ajax_requests():
    """Пробуем различные варианты AJAX запросов вручную"""
    
    print(f"\n{'='*60}")
    print("🔧 Пробуем различные варианты AJAX запросов...")
    
    # Создаем новый платеж
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
        payment_id = payment_url.split('/')[-1]
        print(f"✅ Платеж создан: {payment_url}")
        print(f"🆔 Payment ID: {payment_id}")
        
    except Exception as e:
        print(f"❌ Ошибка создания платежа: {e}")
        return
    
    # Различные варианты AJAX URL
    ajax_variants = [
        f"https://gate.minopay.net/{payment_id}",
        f"https://gate.minopay.net/{payment_id}/",
        f"https://gate.minopay.net/{payment_id}?action=check",
        f"https://gate.minopay.net/{payment_id}?action=qrcode",
        f"https://gate.minopay.net/{payment_id}?checkPaymentState=1",
        f"https://gate.minopay.net/api/{payment_id}",
        f"https://gate.minopay.net/api/{payment_id}/status",
        f"https://gate.minopay.net/api/{payment_id}/qr",
        f"https://gate.minopay.net/pp/{payment_id}/",
        f"https://gate.minopay.net/pp/{payment_id}/?action=check",
        f"https://gate.minopay.net/pp/{payment_id}/?checkPaymentState=1",
        f"https://gate.minopay.net/check/{payment_id}",
        f"https://gate.minopay.net/status/{payment_id}",
        f"https://gate.minopay.net/qr/{payment_id}",
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, */*",
        "Accept-Language": "ru,en;q=0.9",
        "Referer": payment_url,
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive"
    }
    
    print(f"🧪 Тестируем {len(ajax_variants)} вариантов AJAX запросов...")
    
    for i, url in enumerate(ajax_variants):
        try:
            print(f"\n[{i+1}/{len(ajax_variants)}] {url}")
            
            ajax_response = requests.get(url, headers=headers, timeout=5)
            print(f"  Status: {ajax_response.status_code}")
            
            if ajax_response.status_code == 200:
                content = ajax_response.text[:300]
                print(f"  Content: {content}...")
                
                # Проверяем на JSON
                try:
                    json_data = ajax_response.json()
                    print(f"  JSON: {json_data}")
                    
                    # Ищем QR-ссылку
                    if isinstance(json_data, dict):
                        for key, value in json_data.items():
                            if isinstance(value, str) and 'qr.nspk.ru' in value:
                                print(f"  🎯 НАЙДЕНА QR-ССЫЛКА: {value}")
                                return value
                                
                except:
                    # Ищем QR в тексте
                    qr_match = re.search(r'qr\.nspk\.ru/[A-Z0-9?&=]+', ajax_response.text, re.IGNORECASE)
                    if qr_match:
                        qr_link = f"https://{qr_match.group()}"
                        print(f"  🎯 НАЙДЕНА QR-ССЫЛКА в тексте: {qr_link}")
                        return qr_link
            
            time.sleep(0.5)  # Небольшая пауза
            
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
    
    print(f"\n❌ QR-ссылка не найдена в {len(ajax_variants)} вариантах")

if __name__ == "__main__":
    print("🔍 Анализ JavaScript файлов и AJAX запросов")
    print("=" * 60)
    
    # Анализируем JS файлы
    analyze_js_files()
    
    # Пробуем AJAX запросы вручную
    try_manual_ajax_requests()
    
    print(f"\n{'='*60}")
    print("🏁 Анализ завершен!")