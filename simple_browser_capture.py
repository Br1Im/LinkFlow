#!/usr/bin/env python3
"""
Простой скрипт с Playwright - заходим на сайт, ждем, перехватываем запросы
"""

import asyncio
import json
import re

async def capture_qr_link():
    """Захватываем QR-ссылку используя Playwright"""
    
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Playwright не установлен. Установите: pip install playwright")
        print("   Затем: playwright install")
        return None
    
    print("🚀 Создаем новый платеж...")
    
    # Создаем новый платеж
    import requests
    try:
        response = requests.post(
            "http://85.192.56.74:5001/api/create-bot-payment/bridgeapi",
            json={"amount": 100},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Ошибка создания платежа: {response.status_code}")
            return None
            
        data = response.json()
        payment_url = data.get('payment_url')
        print(f"✅ Платеж создан: {payment_url}")
        
    except Exception as e:
        print(f"❌ Ошибка создания платежа: {e}")
        return None
    
    # Список для сохранения перехваченных запросов
    captured_requests = []
    found_qr_link = None
    
    async with async_playwright() as p:
        print("🌐 Запускаем браузер...")
        
        # Запускаем браузер
        browser = await p.chromium.launch(headless=False)  # headless=False чтобы видеть что происходит
        context = await browser.new_context()
        page = await context.new_page()
        
        # Перехватываем все сетевые запросы
        async def handle_response(response):
            nonlocal found_qr_link
            
            url = response.url
            status = response.status
            
            print(f"📡 {status} {url}")
            
            # Сохраняем запрос
            captured_requests.append({
                'url': url,
                'status': status,
                'method': response.request.method
            })
            
            # Проверяем, содержит ли URL интересные параметры
            if 'checkPaymentState=1' in url or 'qrcode' in url.lower():
                print(f"🎯 Интересный запрос: {url}")
                
                try:
                    # Пытаемся получить JSON ответ
                    if status == 200:
                        content_type = response.headers.get('content-type', '')
                        
                        if 'application/json' in content_type:
                            response_text = await response.text()
                            print(f"📋 JSON Response: {response_text}")
                            
                            try:
                                json_data = json.loads(response_text)
                                
                                # Ищем QR-ссылку в JSON
                                if isinstance(json_data, dict):
                                    if json_data.get('action') == 'qrcode' and 'url' in json_data:
                                        qr_url = json_data['url']
                                        if 'qr.nspk.ru' in qr_url:
                                            print(f"🎯 НАЙДЕНА QR-ССЫЛКА: {qr_url}")
                                            found_qr_link = qr_url
                                    
                                    # Проверяем все поля
                                    for key, value in json_data.items():
                                        if 'qr.nspk.ru' in str(value):
                                            print(f"🎯 НАЙДЕНА QR-ССЫЛКА в поле '{key}': {value}")
                                            found_qr_link = value
                                            
                            except json.JSONDecodeError:
                                pass
                        else:
                            # Проверяем текстовый ответ
                            response_text = await response.text()
                            qr_match = re.search(r'qr\.nspk\.ru/[A-Z0-9?&=]+', response_text, re.IGNORECASE)
                            if qr_match:
                                qr_link = f"https://{qr_match.group()}"
                                print(f"🎯 НАЙДЕНА QR-ССЫЛКА в тексте: {qr_link}")
                                found_qr_link = qr_link
                                
                except Exception as e:
                    print(f"❌ Ошибка обработки ответа: {e}")
        
        # Подключаем обработчик ответов
        page.on('response', handle_response)
        
        try:
            print(f"📄 Переходим на страницу: {payment_url}")
            
            # Переходим на страницу платежа
            await page.goto(payment_url, wait_until='networkidle')
            
            print("⏳ Ждем 10 секунд для загрузки JavaScript и AJAX запросов...")
            await asyncio.sleep(10)
            
            # Если QR-ссылка еще не найдена, попробуем взаимодействовать со страницей
            if not found_qr_link:
                print("🔍 QR-ссылка не найдена, пробуем взаимодействовать со страницей...")
                
                # Пробуем кликнуть на элементы, которые могут запустить загрузку QR
                try:
                    # Ищем кнопки или элементы связанные с QR
                    qr_elements = await page.query_selector_all('[id*="qr"], [class*="qr"], [id*="sbp"], [class*="sbp"]')
                    
                    for element in qr_elements[:3]:  # Пробуем первые 3 элемента
                        try:
                            await element.click()
                            print("🖱️ Кликнули на QR элемент, ждем...")
                            await asyncio.sleep(3)
                            
                            if found_qr_link:
                                break
                                
                        except Exception as e:
                            print(f"❌ Ошибка клика: {e}")
                            
                except Exception as e:
                    print(f"❌ Ошибка поиска QR элементов: {e}")
                
                # Дополнительное ожидание
                if not found_qr_link:
                    print("⏳ Ждем еще 5 секунд...")
                    await asyncio.sleep(5)
            
            print(f"\n📊 Всего перехвачено запросов: {len(captured_requests)}")
            
            # Показываем интересные запросы
            interesting_requests = [
                req for req in captured_requests 
                if any(keyword in req['url'].lower() for keyword in ['checkpaymentstate', 'qrcode', 'sbp', 'qr'])
            ]
            
            if interesting_requests:
                print(f"🎯 Интересные запросы ({len(interesting_requests)}):")
                for req in interesting_requests:
                    print(f"   {req['method']} {req['status']} {req['url']}")
            
        except Exception as e:
            print(f"❌ Ошибка работы с браузером: {e}")
        
        finally:
            await browser.close()
    
    return found_qr_link

async def main():
    """Основная функция"""
    print("=" * 60)
    print("🌐 Простой захват QR-ссылки через браузер")
    print("=" * 60)
    
    qr_link = await capture_qr_link()
    
    if qr_link:
        print(f"\n🎉 УСПЕХ! Найдена QR-ссылка: {qr_link}")
        
        # Проверяем ссылку
        import requests
        try:
            test_response = requests.head(qr_link, timeout=5)
            print(f"✅ QR-ссылка доступна (статус: {test_response.status_code})")
        except Exception as e:
            print(f"⚠️ Не удалось проверить QR-ссылку: {e}")
            
    else:
        print(f"\n❌ QR-ссылка не найдена")
        print("💡 Возможно, нужно больше времени или другой подход")

if __name__ == "__main__":
    asyncio.run(main())