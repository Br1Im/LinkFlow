#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для сохранения скриншота из ответа сервера
"""

import requests
import json
import time
import uuid

# Настройки
SERVER_URL = "http://85.192.56.74:5000"
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

def save_screenshot():
    """Делает запрос и сохраняет скриншот"""
    
    print("🔍 ПОЛУЧЕНИЕ СКРИНШОТА ОШИБКИ")
    print("=" * 50)
    
    # Данные для запроса
    order_id = f"screenshot-test-{int(time.time())}-{uuid.uuid4().hex[:6]}"
    amount = 1000  # Минимальная сумма для elecsnet.ru
    
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'amount': amount,
        'orderId': order_id
    }
    
    print(f"📋 Отправка запроса...")
    
    try:
        response = requests.post(
            f"{SERVER_URL}/api/payment",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 500:
            result = response.json()
            
            if 'screenshot' in result:
                screenshot_data = result['screenshot']
                
                # Сохраняем в HTML файл
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Скриншот ошибки elecsnet.ru</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: #f0f0f0;
            font-family: Arial, sans-serif;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-bottom: 20px;
        }}
        img {{
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: zoom-in;
        }}
        img.zoomed {{
            cursor: zoom-out;
            max-width: none;
            width: auto;
        }}
        .info {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .error {{
            background: #ffebee;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Скриншот ошибки при создании платежа</h1>
        <div class="info">
            <strong>Информация:</strong><br>
            Это скриншот страницы elecsnet.ru в момент ошибки при попытке создать платеж через curl запрос.<br>
            <strong>Время:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}<br>
            <strong>Order ID:</strong> {order_id}
        </div>
        <img id="screenshot" src="{screenshot_data}" alt="Скриншот ошибки" onclick="toggleZoom(this)">
        <div class="error">
            <strong>Текст ошибки:</strong><br>
            {result.get('error', 'Unknown error')}
        </div>
    </div>
    
    <script>
        function toggleZoom(img) {{
            img.classList.toggle('zoomed');
        }}
    </script>
</body>
</html>"""
                
                with open('screenshot_error.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print("✅ Скриншот сохранен в файл: screenshot_error.html")
                print("📂 Открой этот файл в браузере, чтобы посмотреть скриншот")
                print()
                print("🔍 Также сохранен preview HTML страницы:")
                if 'page_source_preview' in result:
                    print(result['page_source_preview'][:500])
                
                return True
            else:
                print("❌ В ответе нет скриншота")
                return False
        else:
            print(f"❌ Неожиданный статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    save_screenshot()
