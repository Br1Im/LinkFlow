#!/usr/bin/env python3
"""
Отладка HTML содержимого для понимания структуры страницы
"""

import requests
import re

def debug_payment_page():
    """Отладка содержимого страницы платежа"""
    
    # Создаем новый платеж
    print("🚀 Создаем новый платеж для отладки...")
    
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
    
    # Загружаем HTML страницы
    print(f"\n📄 Загружаем HTML страницы...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en;q=0.9",
    }
    
    try:
        html_response = requests.get(payment_url, headers=headers, timeout=15)
        
        if html_response.status_code != 200:
            print(f"❌ Ошибка загрузки HTML: {html_response.status_code}")
            return
            
        html_content = html_response.text
        print(f"✅ HTML загружен, размер: {len(html_content)} символов")
        
        # Сохраняем HTML в файл для анализа
        with open('debug_payment_page.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"💾 HTML сохранен в debug_payment_page.html")
        
        # Ищем различные паттерны
        print(f"\n🔍 Анализ HTML содержимого:")
        
        # 1. Ищем sign
        sign_patterns = [
            r'sign["\']?\s*[:=]\s*["\']([a-f0-9]+)["\']',
            r'"sign"\s*:\s*"([a-f0-9]+)"',
            r'&sign=([a-f0-9]+)',
            r'\?sign=([a-f0-9]+)',
            r'sign:\s*["\']([a-f0-9]+)["\']',
            r'sign\s*=\s*["\']([a-f0-9]+)["\']'
        ]
        
        print(f"🔑 Поиск sign:")
        for i, pattern in enumerate(sign_patterns):
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                print(f"  Pattern {i+1}: {matches}")
        
        # 2. Ищем SPM ID
        spm_patterns = [
            r'spm_[a-z0-9]+',
            r'/pp/(smp_[a-z0-9]+)/',
            r'"order_id"\s*:\s*"(spm_[a-z0-9]+)"',
            r'order_id["\']?\s*[:=]\s*["\']?(spm_[a-z0-9]+)["\']?'
        ]
        
        print(f"🆔 Поиск SPM ID:")
        for i, pattern in enumerate(spm_patterns):
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                print(f"  Pattern {i+1}: {matches}")
        
        # 3. Ищем JavaScript код
        js_patterns = [
            r'<script[^>]*>(.*?)</script>',
            r'fetch\([^)]+\)',
            r'XMLHttpRequest',
            r'checkPaymentState',
            r'qr\.nspk\.ru'
        ]
        
        print(f"📜 Поиск JavaScript:")
        for i, pattern in enumerate(js_patterns):
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if matches:
                print(f"  Pattern {i+1}: найдено {len(matches)} совпадений")
                if i < 2:  # Показываем первые несколько для script и fetch
                    for match in matches[:2]:
                        preview = match[:200] + "..." if len(match) > 200 else match
                        print(f"    {preview}")
        
        # 4. Ищем любые URL с gate.minopay.net
        url_patterns = [
            r'https://gate\.minopay\.net/[^"\s]+',
            r'/pp/[^"\s]+',
            r'checkPaymentState[^"\s]*'
        ]
        
        print(f"🔗 Поиск URL:")
        for i, pattern in enumerate(url_patterns):
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                print(f"  Pattern {i+1}: {matches}")
        
        # 5. Показываем фрагменты HTML с интересными ключевыми словами
        keywords = ['sign', 'spm_', 'checkPaymentState', 'qrcode', 'order_id']
        
        print(f"\n📋 Фрагменты HTML с ключевыми словами:")
        for keyword in keywords:
            lines = html_content.split('\n')
            for i, line in enumerate(lines):
                if keyword.lower() in line.lower():
                    print(f"  {keyword} (строка {i+1}): {line.strip()}")
                    
    except Exception as e:
        print(f"❌ Ошибка анализа HTML: {e}")

if __name__ == "__main__":
    debug_payment_page()