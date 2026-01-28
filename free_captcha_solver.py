#!/usr/bin/env python3
"""
БЕСПЛАТНОЕ решение Yandex SmartCaptcha
Используя https://github.com/yoori/yandex-captcha-puzzle-solver
"""

import asyncio
import json
from playwright.async_api import async_playwright
from multitransfer_api import MultitransferAPI

class FreeCaptchaSolver:
    def __init__(self):
        self.token = None
        
    async def solve_captcha_and_get_token(self) -> str:
        """Решение капчи и получение токена через Playwright"""
        print("🚀 Запускаю браузер для решения капчи...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Перехватываем токен
            captured_token = None
            
            def handle_request(request):
                nonlocal captured_token
                if 'api.multitransfer.ru' in request.url:
                    headers = request.headers
                    if 'fhptokenid' in headers:
                        captured_token = headers['fhptokenid']
                        print(f"✅ Токен перехвачен: {captured_token[:30]}...")
            
            page.on('request', handle_request)
            
            # Открываем страницу
            print("🌐 Открываю multitransfer.ru...")
            await page.goto("https://multitransfer.ru/transfer/uzbekistan")
            await asyncio.sleep(3)
            
            # Заполняем сумму
            print("📝 Заполняю сумму...")
            try:
                amount_input = await page.wait_for_selector("input[placeholder='0 RUB']", timeout=10000)
                await amount_input.fill("110")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"❌ Ошибка заполнения суммы: {e}")
                await browser.close()
                return None
            
            # Нажимаем продолжить
            print("🔘 Нажимаю 'Продолжить'...")
            try:
                continue_btn = await page.wait_for_selector("button:has-text('Продолжить')", timeout=10000)
                await continue_btn.click()
                await asyncio.sleep(5)
            except Exception as e:
                print(f"❌ Ошибка с кнопкой: {e}")
            
            # Заполняем данные получателя
            print("📝 Заполняю данные получателя...")
            
            # Карта
            try:
                card_selectors = [
                    "input[placeholder*='карт']",
                    "input[name='card']",
                    "input[type='text']:not([placeholder*='RUB']):not([placeholder*='UZS'])"
                ]
                
                for selector in card_selectors:
                    try:
                        card_input = await page.wait_for_selector(selector, timeout=3000)
                        if card_input and await card_input.is_visible():
                            await card_input.fill("9860080323894719")
                            print("✅ Карта заполнена")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"⚠️ Карта: {e}")
            
            # Имя
            try:
                name_selectors = [
                    "input[placeholder*='имя']",
                    "input[name='name']"
                ]
                
                for selector in name_selectors:
                    try:
                        name_input = await page.wait_for_selector(selector, timeout=3000)
                        if name_input and await name_input.is_visible():
                            await name_input.fill("Nodir Asadullayev")
                            print("✅ Имя заполнено")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"⚠️ Имя: {e}")
            
            await asyncio.sleep(2)
            
            # Инжектим скрипт для автоматического решения капчи
            print("🧩 Инжектирую решатель капчи...")
            
            captcha_solver_script = """
            // Автоматическое решение Yandex SmartCaptcha
            // На основе https://github.com/yoori/yandex-captcha-puzzle-solver
            
            async function solveCaptcha() {
                console.log('🔍 Ищу SmartCaptcha...');
                
                // Ждем появления iframe с капчей
                const checkIframe = setInterval(async () => {
                    const iframes = document.querySelectorAll('iframe');
                    
                    for (const iframe of iframes) {
                        if (iframe.src.includes('smartcaptcha')) {
                            console.log('✅ Найден iframe SmartCaptcha');
                            clearInterval(checkIframe);
                            
                            try {
                                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                                
                                // Ищем checkbox
                                const checkbox = iframeDoc.querySelector('input[type="checkbox"], .checkbox, [role="checkbox"]');
                                
                                if (checkbox) {
                                    console.log('✅ Найден checkbox, кликаю...');
                                    checkbox.click();
                                    
                                    // Ждем появления puzzle
                                    setTimeout(() => {
                                        const puzzle = iframeDoc.querySelector('.puzzle, .challenge, canvas');
                                        if (puzzle) {
                                            console.log('🧩 Найден puzzle, решаю...');
                                            // Здесь можно добавить логику решения puzzle
                                            // Пока просто кликаем в центр
                                            const rect = puzzle.getBoundingClientRect();
                                            const x = rect.left + rect.width / 2;
                                            const y = rect.top + rect.height / 2;
                                            
                                            const clickEvent = new MouseEvent('click', {
                                                view: window,
                                                bubbles: true,
                                                cancelable: true,
                                                clientX: x,
                                                clientY: y
                                            });
                                            puzzle.dispatchEvent(clickEvent);
                                        }
                                    }, 2000);
                                }
                            } catch (e) {
                                console.error('❌ Ошибка доступа к iframe:', e);
                            }
                            
                            break;
                        }
                    }
                }, 1000);
            }
            
            solveCaptcha();
            """
            
            await page.evaluate(captcha_solver_script)
            
            print("⏳ Жду решения капчи и перехвата токена...")
            print("💡 Если капча не решается автоматически - реши вручную")
            
            # Ждем токен
            for i in range(120):  # 2 минуты
                if captured_token:
                    break
                await asyncio.sleep(1)
                
                if i % 10 == 0:
                    print(f"⏳ Жду токен... ({i}/120 сек)")
            
            await browser.close()
            
            if captured_token:
                self.token = captured_token
                return captured_token
            else:
                print("❌ Токен не получен")
                return None
    
    def create_qr_payment(self, card_number: str, recipient_name: str, amount: float) -> str:
        """Создание QR-платежа с автоматическим решением капчи"""
        print(f"🎯 Создаю QR-платеж: {amount} RUB → {card_number}")
        
        # Получаем токен через решение капчи
        token = asyncio.run(self.solve_captcha_and_get_token())
        
        if not token:
            print("❌ Не удалось получить токен")
            return None
        
        # Используем API с токеном
        api = MultitransferAPI(token)
        
        try:
            qr_link = api.create_qr_payment(card_number, recipient_name, amount)
            return qr_link
        except Exception as e:
            print(f"❌ Ошибка создания платежа: {e}")
            return None

def main():
    """Тест бесплатного решателя капчи"""
    print("🚀 БЕСПЛАТНОЕ РЕШЕНИЕ YANDEX SMARTCAPTCHA")
    print("="*50)
    
    solver = FreeCaptchaSolver()
    
    qr_link = solver.create_qr_payment(
        card_number="9860080323894719",
        recipient_name="Nodir Asadullayev",
        amount=110
    )
    
    if qr_link:
        print(f"🎉 УСПЕХ! QR-ссылка: {qr_link}")
        
        with open('free_result.txt', 'w') as f:
            f.write(f"QR Link: {qr_link}\n")
        
        print("💾 Результат сохранен в free_result.txt")
        print("✅ БЕСПЛАТНАЯ АВТОМАТИЗАЦИЯ РАБОТАЕТ!")
    else:
        print("❌ Не удалось создать QR-ссылку")

if __name__ == "__main__":
    main()