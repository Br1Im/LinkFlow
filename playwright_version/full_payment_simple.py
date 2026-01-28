#!/usr/bin/env python3
"""
Упрощенная версия - только сумма и продолжить
"""

from playwright.sync_api import sync_playwright
import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from payment_step2 import (
    complete_payment_step2
)


def simple_payment_flow(amount: float, card_number: str, owner_name: str, headless: bool = False):
    """Упрощенный цикл - только сумма и кнопка"""
    start_time = time.time()
    
    print(f"🚀 СОЗДАНИЕ ПЛАТЕЖА (УПРОЩЕННАЯ ВЕРСИЯ)")
    print("="*70)
    print(f"💰 Сумма: {amount} RUB")
    print(f"💳 Карта: {card_number}")
    print(f"👤 Владелец: {owner_name}")
    print("="*70)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            # Дополнительные опции для имитации человеческого браузера
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Добавляем дополнительные заголовки для имитации человека
            extra_http_headers={
                'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        # Убираем признаки автоматизации
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Убираем другие признаки автоматизации
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """)
        
        page = context.new_page()
        
        try:
            # ШАГ 1: Открываем страницу
            print(f"\n⏱️  1️⃣ Открываю страницу...")
            page.goto("https://multitransfer.ru/transfer/uzbekistan", wait_until='domcontentloaded')  # Меняем на domcontentloaded
            print(f"   ✅ DOM загружен")
            
            # ШАГ 2: Вводим сумму (БЫСТРАЯ ВЕРСИЯ)
            print(f"\n⏱️  2️⃣ Ввожу сумму {amount} RUB...")
            
            # Ждем только появления поля (не ждем networkidle)
            amount_input = page.locator('input[placeholder="0 RUB"]')
            amount_input.wait_for(state='visible', timeout=5000)
            
            # Кликаем в поле
            amount_input.click()
            page.wait_for_timeout(30)  # Уменьшаем с 50 до 30
            
            # Очищаем через выделение и удаление
            page.keyboard.press('Control+A')
            page.wait_for_timeout(15)  # Уменьшаем с 20 до 15
            page.keyboard.press('Backspace')
            page.wait_for_timeout(20)  # Уменьшаем с 30 до 20
            
            # Вводим посимвольно с минимальными паузами
            amount_str = str(int(amount))
            for i, char in enumerate(amount_str):
                page.keyboard.type(char)
                page.wait_for_timeout(20)  # Уменьшаем с 30 до 20
            
            # Нажимаем Enter для подтверждения
            page.keyboard.press('Enter')
            page.wait_for_timeout(150)  # Уменьшаем с 200 до 150
            
            current_value = amount_input.input_value()
            print(f"   ✅ Введено: {current_value}")
            
            # Ждем пока React рассчитает комиссию и курс (БЫСТРЕЕ)
            print(f"   ⏳ Жду расчета комиссии...")
            try:
                # Ждем появления рассчитанной суммы к получению (сокращаем время)
                page.wait_for_function("""
                    () => {
                        const input = document.querySelector('input[placeholder*="UZS"]');
                        return input && input.value && input.value !== '0 UZS' && input.value !== '';
                    }
                """, timeout=2500)  # Уменьшаем с 3000 до 2500
                receive_value = page.locator('input[placeholder*="UZS"]').input_value()
                print(f"   ✅ Комиссия рассчитана. К получению: {receive_value}")
            except:
                print(f"   ⚠️ Не дождался расчета, но продолжаю")
            
            # ШАГ 2.5: Выбираем способ платежа (БЫСТРЕЕ)
            print(f"\n⏱️  2.5️⃣ Выбираю способ платежа...")
            
            # Кликаем по блоку "Способ перевода" (доступен сразу)
            transfer_clicked = False
            transfer_selectors = [
                'div.css-c8d8yl:has-text("Способ перевода")',
                'div:has-text("Способ перевода")',
            ]
            
            for selector in transfer_selectors:
                try:
                    transfer_block = page.locator(selector).first
                    if transfer_block.is_visible(timeout=500):  # Уменьшаем с 1000 до 500
                        transfer_block.click()
                        print(f"   ✅ Открыл способ платежа")
                        transfer_clicked = True
                        break
                except:
                    continue
            
            if transfer_clicked:
                # Банк можно выбирать сразу после клика!
                print("   ⚡ Выбираю банк сразу...")
                page.wait_for_timeout(200)  # Минимальная пауза вместо 1000
                
                bank_selectors = [
                    'text=Uzcard',
                    '[role="button"]:has-text("Uzcard")',
                    'button:has-text("Uzcard")',
                    '*[text*="Uzcard"]',
                    '*[text*="Humo"]'
                ]
                
                bank_selected = False
                for selector in bank_selectors:
                    try:
                        print(f"   Пробую селектор: {selector}")
                        bank_option = page.locator(selector).first
                        # Ждем появления элемента
                        bank_option.wait_for(state='visible', timeout=2000)
                        bank_option.click()
                        print(f"   ✅ Банк выбран через: {selector}")
                        bank_selected = True
                        break
                    except Exception as e:
                        print(f"   ⚠️ Селектор {selector} не сработал: {str(e)[:50]}")
                        continue
                
                if not bank_selected:
                    print(f"   ❌ Не удалось выбрать банк - пробую альтернативный способ")
                    # Пробуем кликнуть по любому элементу с текстом банка
                    try:
                        page.locator('text=Uzcard').or_(page.locator('text=Humo')).first.click(timeout=2000)
                        print(f"   ✅ Банк выбран (альтернативный способ)")
                        bank_selected = True
                    except:
                        print(f"   ❌ Альтернативный способ тоже не сработал")
                
                # Минимальное время на обработку выбора банка
                if bank_selected:
                    page.wait_for_timeout(300)  # Уменьшаем с 1000 до 300
            else:
                print(f"   ⚠️ Не удалось открыть способ платежа")
            
            # ШАГ 3: Нажимаем Продолжить (БЫСТРЕЕ)
            print(f"\n⏱️  3️⃣ Нажимаю 'Продолжить'...")
            
            # Ждем активации кнопки
            try:
                page.wait_for_function("""
                    () => {
                        const btn = document.getElementById('pay');
                        return btn && !btn.disabled;
                    }
                """, timeout=10000)  # Возвращаем стабильное время как в рабочей версии
                print("   ✅ Кнопка активна")
            except:
                print("   ⚠️  Кнопка disabled, но пробуем кликнуть")
            
            pay_button = page.locator('#pay')
            
            # Кликаем и ждем навигации
            try:
                with page.expect_navigation(timeout=10000):  # Возвращаем стабильное время
                    pay_button.click()
            except:
                # Если не сработало, пробуем через JS
                pay_button.evaluate('el => el.click()')
                page.wait_for_url('**/sender-details**', timeout=10000)  # Возвращаем стабильное время
            
            print(f"   ✅ Переход на sender-details")
            print(f"   📍 URL: {page.url}")
            
            # ============ ШАГ 2: Заполнение данных ============
            print(f"\n{'='*70}")
            print("ШАГ 2: ЗАПОЛНЕНИЕ ДАННЫХ")
            print(f"{'='*70}")
            
            # Используем новую автоматическую функцию
            step2_success = complete_payment_step2(page, card_number, owner_name)
            
            if step2_success:
                print(f"✅ Шаг 2 завершен успешно!")
            else:
                print(f"⚠️ Шаг 2 завершен с проблемами")
            
            total_time = time.time() - start_time
            
            print(f"\n{'='*70}")
            print(f"✅ ПЛАТЕЖ СОЗДАН ЗА {total_time:.1f}s")
            print(f"📍 Финальный URL: {page.url}")
            print(f"{'='*70}")
            
            input("\nНажми Enter чтобы закрыть браузер...")
            browser.close()
            
            return {
                'success': True,
                'elapsed_time': total_time,
                'final_url': page.url
            }
            
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            
            input("\nНажми Enter чтобы закрыть браузер...")
            browser.close()
            
            return {
                'success': False,
                'elapsed_time': time.time() - start_time,
                'error': str(e)
            }


def test():
    """Тест"""
    result = simple_payment_flow(
        amount=110,
        card_number="9860080323894719",  # Из HAR
        owner_name="Nodir Asadullayev",  # Из HAR (латиница)
        headless=False
    )
    
    if result['success']:
        print(f"\n🎉 Успех! Время: {result['elapsed_time']:.1f}s")
    else:
        print(f"\n❌ Ошибка: {result.get('error')}")


if __name__ == "__main__":
    test()
