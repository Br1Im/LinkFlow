#!/usr/bin/env python3
"""
Скрипт для перехвата сетевых запросов браузера
Использует requests-html для имитации браузера с JavaScript
"""

import requests
import json
import time
import re
from urllib.parse import urlparse, parse_qs

def create_new_payment():
    """Создать новый платеж"""
    print("🚀 Создаем новый платеж...")
    
    try:
        response = requests.post(
            "http://85.192.56.74:5001/api/create-bot-payment/bridgeapi",
            json={"amount": 100},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            payment_url = data.get('payment_url')
            print(f"✅ Платеж создан: {payment_url}")
            return payment_url
        else:
            print(f"❌ Ошибка: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка создания платежа: {e}")
        return None

def monitor_network_requests(payment_url):
    """Мониторим сетевые запросы используя анализ JavaScript"""
    print(f"\n🌐 Мониторим сетевые запросы для: {payment_url}")
    
    payment_id = payment_url.split('/')[-1]
    print(f"🆔 Payment ID: {payment_id}")
    
    # Создаем сессию
    session = requests.Session()
    
    # Заголовки браузера
    browser_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        # Шаг 1: Загружаем страницу
        print("📄 Загружаем страницу...")
        response = session.get(payment_url, headers=browser_headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Ошибка загрузки: {response.status_code}")
            return None
        
        html_content = response.text
        print(f"✅ Страница загружена: {len(html_content)} символов")
        
        # Шаг 2: Анализируем HTML для поиска данных
        print("\n🔍 Анализируем HTML для поиска sign и других данных...")
        
        # Ищем встроенные данные в JavaScript
        script_patterns = [
            r'const\s+formJsonConfig\s*=\s*`([^`]+)`',
            r'var\s+formJsonConfig\s*=\s*["\']([^"\']+)["\']',
            r'formJsonConfig\s*=\s*["\']([^"\']+)["\']',
            r'sign["\']?\s*[:=]\s*["\']([a-f0-9]+)["\']',
            r'data\.sign\s*=\s*["\']([a-f0-9]+)["\']',
        ]
        
        found_data = {}
        for pattern in script_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if matches:
                print(f"✅ Найден паттерн: {matches}")
                if 'sign' in pattern.lower():
                    found_data['sign'] = matches[0]
                elif 'formJsonConfig' in pattern:
                    try:
                        config_data = json.loads(matches[0])
                        found_data['config'] = config_data
                        print(f"📋 Config data: {json.dumps(config_data, indent=2)}")
                    except:
                        print(f"📋 Raw config: {matches[0][:200]}...")
        
        # Шаг 3: Имитируем ожидание загрузки JavaScript
        print(f"\n⏳ Ждем 3 секунды (имитация загрузки JS)...")
        time.sleep(3)
        
        # Шаг 4: Пробуем запросы которые должен делать JavaScript
        ajax_headers = {
            "User-Agent": browser_headers["User-Agent"],
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru,en;q=0.9",
            "Referer": payment_url,
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        
        # Основываясь на анализе JS, пробуем запросы
        potential_requests = []
        
        # Если нашли sign, используем его
        if 'sign' in found_data:
            sign = found_data['sign']
            print(f"🔑 Используем найденный sign: {sign}")
            potential_requests.extend([
                f"https://gate.minopay.net/{payment_id}?checkPaymentState=1&sign={sign}",
                f"https://gate.minopay.net/pp/{payment_id}/?checkPaymentState=1&sign={sign}",
            ])
        
        # Добавляем запросы без sign (возможно sign добавляется динамически)
        potential_requests.extend([
            f"https://gate.minopay.net/{payment_id}?checkPaymentState=1",
            f"https://gate.minopay.net/{payment_id}/status",
            f"https://gate.minopay.net/{payment_id}/qr",
            f"https://gate.minopay.net/api/{payment_id}/status",
            f"https://gate.minopay.net/nova/api/{payment_id}/status",
        ])
        
        print(f"\n🔍 Пробуем {len(potential_requests)} потенциальных AJAX запросов...")
        
        for i, url in enumerate(potential_requests):
            try:
                # Добавляем случайный nc параметр как в реальном JS
                import random
                if 'checkPaymentState=1' in url:
                    separator = '&' if '?' in url else '?'
                    url_with_nc = f"{url}{separator}nc={random.random()}"
                else:
                    url_with_nc = url
                
                print(f"\n🔗 [{i+1}/{len(potential_requests)}] {url_with_nc}")
                
                ajax_response = session.get(url_with_nc, headers=ajax_headers, timeout=5)
                
                print(f"📊 Status: {ajax_response.status_code}")
                print(f"📋 Content-Type: {ajax_response.headers.get('content-type', 'unknown')}")
                
                if ajax_response.status_code == 200:
                    response_text = ajax_response.text
                    print(f"📋 Response (первые 150 символов): {response_text[:150]}...")
                    
                    # Проверяем, является ли ответ JSON
                    if 'application/json' in ajax_response.headers.get('content-type', ''):
                        try:
                            data = ajax_response.json()
                            print(f"📋 JSON Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                            
                            # Ищем QR-ссылку
                            if isinstance(data, dict):
                                if data.get('action') == 'qrcode' and 'url' in data:
                                    qr_url = data['url']
                                    if 'qr.nspk.ru' in qr_url:
                                        print(f"🎯 НАЙДЕНА QR-ССЫЛКА: {qr_url}")
                                        return qr_url
                                
                                # Проверяем все поля на наличие QR-ссылки
                                for key, value in data.items():
                                    if 'qr.nspk.ru' in str(value):
                                        print(f"🎯 НАЙДЕНА QR-ССЫЛКА в поле '{key}': {value}")
                                        return value
                        
                        except json.JSONDecodeError:
                            pass
                    
                    # Ищем QR-ссылку в тексте
                    qr_match = re.search(r'qr\.nspk\.ru/[A-Z0-9?&=]+', response_text, re.IGNORECASE)
                    if qr_match:
                        qr_link = f"https://{qr_match.group()}"
                        print(f"🎯 НАЙДЕНА QR-ССЫЛКА в тексте: {qr_link}")
                        return qr_link
                
                elif ajax_response.status_code == 404:
                    print("❌ 404 - Not Found")
                else:
                    print(f"❌ HTTP {ajax_response.status_code}")
                    
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        # Шаг 5: Пробуем дополнительные запросы с задержкой
        print(f"\n⏳ Ждем еще 5 секунд и пробуем снова...")
        time.sleep(5)
        
        # Повторяем некоторые ключевые запросы
        key_requests = [req for req in potential_requests if 'checkPaymentState=1' in req]
        
        for url in key_requests[:3]:  # Только первые 3
            try:
                import random
                url_with_nc = f"{url}&nc={random.random()}"
                
                print(f"\n🔄 Повторный запрос: {url_with_nc}")
                
                ajax_response = session.get(url_with_nc, headers=ajax_headers, timeout=5)
                
                if ajax_response.status_code == 200:
                    try:
                        data = ajax_response.json()
                        if data.get('action') == 'qrcode' and 'url' in data:
                            qr_url = data['url']
                            print(f"🎯 НАЙДЕНА QR-ССЫЛКА (повторный запрос): {qr_url}")
                            return qr_url
                    except:
                        pass
                        
            except Exception as e:
                print(f"❌ Ошибка повторного запроса: {e}")
        
        return None
        
    except Exception as e:
        print(f"❌ Общая ошибка мониторинга: {e}")
        return None

def main():
    """Основная функция"""
    print("=" * 60)
    print("🌐 Перехват сетевых запросов браузера")
    print("=" * 60)
    
    # Создаем новый платеж
    payment_url = create_new_payment()
    if not payment_url:
        return
    
    # Мониторим сетевые запросы
    qr_link = monitor_network_requests(payment_url)
    
    if qr_link:
        print(f"\n🎉 УСПЕХ! Найдена QR-ссылка: {qr_link}")
        
        # Проверяем, что ссылка рабочая
        try:
            test_response = requests.head(qr_link, timeout=5)
            if test_response.status_code == 200:
                print(f"✅ QR-ссылка доступна")
            else:
                print(f"⚠️ QR-ссылка вернула статус: {test_response.status_code}")
        except:
            print(f"⚠️ Не удалось проверить доступность QR-ссылки")
            
    else:
        print(f"\n❌ QR-ссылка не найдена")
        print(f"💡 Попробуйте открыть {payment_url} в браузере и посмотреть Network tab")

if __name__ == "__main__":
    main()