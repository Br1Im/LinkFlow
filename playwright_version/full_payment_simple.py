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
    screenshot_dir = "./screenshots"  # Локальная директория
    os.makedirs(screenshot_dir, exist_ok=True)
    
    def take_screenshot(page, name):
        """Сохранить скриншот"""
        try:
            path = f"{screenshot_dir}/{name}_{int(time.time())}.png"
            page.screenshot(path=path, full_page=True)
            print(f"   📸 Скриншот: {path}")
        except Exception as e:
            print(f"   ⚠️ Ошибка скриншота: {e}")
    
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
            take_screenshot(page, "01_page_loaded")
            
            # ШАГ 2: Вводим сумму (УЛЬТРА БЫСТРО - сразу после появления поля)
            print(f"\n⏱️  2️⃣ Ввожу сумму {amount} RUB...")
            
            # Ждем только появления поля
            amount_input = page.locator('input[placeholder="0 RUB"]')
            amount_input.wait_for(state='visible', timeout=5000)
            
            # Сразу кликаем и вводим
            amount_input.click()
            page.wait_for_timeout(20)  # Минимальная пауза
            
            # Очищаем
            page.keyboard.press('Control+A')
            page.wait_for_timeout(10)
            page.keyboard.press('Backspace')
            page.wait_for_timeout(15)
            
            # Вводим посимвольно
            amount_str = str(int(amount))
            for char in amount_str:
                page.keyboard.type(char)
                page.wait_for_timeout(15)  # Уменьшаем с 20 до 15
            
            # Enter для подтверждения
            page.keyboard.press('Enter')
            page.wait_for_timeout(100)  # Уменьшаем с 150 до 100
            
            current_value = amount_input.input_value()
            print(f"   ✅ Введено: {current_value}")
            take_screenshot(page, "02_amount_entered")
            
            # Ждем расчета комиссии ПАРАЛЛЕЛЬНО с подготовкой к клику
            print(f"   ⏳ Жду расчета комиссии...")
            try:
                page.wait_for_function("""
                    () => {
                        const input = document.querySelector('input[placeholder*="UZS"]');
                        return input && input.value && input.value !== '0 UZS' && input.value !== '';
                    }
                """, timeout=3000)
                receive_value = page.locator('input[placeholder*="UZS"]').input_value()
                print(f"   ✅ Комиссия рассчитана. К получению: {receive_value}")
            except:
                print(f"   ⚠️ Не дождался расчета, но продолжаю")
            
            # ШАГ 2.5: Выбираем способ платежа (СРАЗУ после расчета комиссии)
            print(f"\n⏱️  2.5️⃣ Выбираю способ платежа...")
            
            # Кликаем по блоку "Способ перевода"
            transfer_clicked = False
            transfer_selectors = [
                'div.css-c8d8yl:has-text("Способ перевода")',
                'div:has-text("Способ перевода")',
            ]
            
            for selector in transfer_selectors:
                try:
                    transfer_block = page.locator(selector).first
                    if transfer_block.is_visible(timeout=300):  # Уменьшаем с 500 до 300
                        transfer_block.click()
                        print(f"   ✅ Открыл способ платежа")
                        transfer_clicked = True
                        break
                except:
                    continue
            
            if transfer_clicked:
                # Банк выбираем СРАЗУ после клика (без паузы!)
                print("   ⚡ Выбираю банк сразу...")
                page.wait_for_timeout(50)  # Минимальная пауза с 200 до 50
                
                bank_selectors = [
                    'text=Uzcard',
                    '[role="button"]:has-text("Uzcard")',
                ]
                
                bank_selected = False
                for selector in bank_selectors:
                    try:
                        bank_option = page.locator(selector).first
                        bank_option.wait_for(state='visible', timeout=1500)  # Уменьшаем с 2000 до 1500
                        bank_option.click()
                        print(f"   ✅ Банк выбран через: {selector}")
                        bank_selected = True
                        break
                    except:
                        continue
                
                if not bank_selected:
                    print(f"   ❌ Не удалось выбрать банк")
                    # Пробуем кликнуть по любому элементу с текстом банка
                    try:
                        page.locator('text=Uzcard').or_(page.locator('text=Humo')).first.click(timeout=2000)
                        print(f"   ✅ Банк выбран (альтернативный способ)")
                        bank_selected = True
                    except:
                        print(f"   ❌ Альтернативный способ тоже не сработал")
                
                # Минимальное время на обработку выбора банка
                if bank_selected:
                    page.wait_for_timeout(100)  # Уменьшаем с 300 до 100
            else:
                print(f"   ⚠️ Не удалось открыть способ платежа")
            
            # ШАГ 3: Нажимаем Продолжить
            print(f"\n⏱️  3️⃣ Нажимаю 'Продолжить'...")
            
            # Ждем активации кнопки
            try:
                page.wait_for_function("""
                    () => {
                        const btn = document.getElementById('pay');
                        return btn && !btn.disabled;
                    }
                """, timeout=10000)
                print("   ✅ Кнопка активна")
            except:
                print("   ⚠️  Кнопка disabled, но пробуем кликнуть")
            
            pay_button = page.locator('#pay')
            
            # Кликаем и ждем навигации
            try:
                with page.expect_navigation(timeout=10000):
                    pay_button.click()
            except:
                pay_button.evaluate('el => el.click()')
                page.wait_for_url('**/sender-details**', timeout=10000)
                page.wait_for_url('**/sender-details**', timeout=10000)  # Возвращаем стабильное время
            
            print(f"   ✅ Переход на sender-details")
            print(f"   📍 URL: {page.url}")
            take_screenshot(page, "03_sender_details_page")
            
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
            take_screenshot(page, "04_final_result")
            
            # Задержка перед закрытием для просмотра результата
            print("\n⏳ Жду 10 секунд перед закрытием...")
            page.wait_for_timeout(10000)
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
            
            # Задержка перед закрытием для просмотра ошибки
            print("\n⏳ Жду 10 секунд перед закрытием...")
            page.wait_for_timeout(10000)
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
        headless=False  # Открываем браузер визуально
    )
    
    if result['success']:
        print(f"\n🎉 Успех! Время: {result['elapsed_time']:.1f}s")
    else:
        print(f"\n❌ Ошибка: {result.get('error')}")


if __name__ == "__main__":
    test()
