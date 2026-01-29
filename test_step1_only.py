#!/usr/bin/env python3
"""
Тест только первого этапа - ввод суммы и выбор способа платежа
"""

from playwright.sync_api import sync_playwright
import time

def test_step1_only():
    """Тест только шага 1"""
    start_time = time.time()
    amount = 110
    
    print(f"🚀 ТЕСТ ШАГА 1: ВВОД СУММЫ И ВЫБОР СПОСОБА ПЛАТЕЖА")
    print("="*70)
    print(f"💰 Сумма: {amount} RUB")
    print("="*70)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
            ]
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        page = context.new_page()
        
        try:
            # ШАГ 1: Открываем страницу
            print(f"\n⏱️  1️⃣ Открываю страницу...")
            page_load_start = time.time()
            page.goto("https://multitransfer.ru/transfer/uzbekistan", wait_until='domcontentloaded')
            page_load_time = time.time() - page_load_start
            print(f"   ✅ DOM загружен за {page_load_time:.1f}s")
            
            # ШАГ 2: Ждем появления поля суммы (это часть загрузки React)
            print(f"\n⏱️  2️⃣ Жду появления поля суммы...")
            field_wait_start = time.time()
            amount_input = page.locator('input[placeholder="0 RUB"]')
            amount_input.wait_for(state='visible', timeout=5000)
            field_wait_time = time.time() - field_wait_start
            print(f"   ✅ Поле появилось за {field_wait_time:.2f}s")
            
            # НАЧИНАЕМ ОТСЧЕТ ЧИСТОГО ВРЕМЕНИ ЗАПОЛНЕНИЯ (после появления поля!)
            fill_start = time.time()
            print(f"   ⚡ Ввожу сумму {amount} RUB...")
            
            # Вводим БЕЗ ПАУЗ
            amount_input.click()
            page.keyboard.press('Control+A')
            page.keyboard.press('Backspace')
            
            amount_str = str(int(amount))
            for char in amount_str:
                page.keyboard.type(char)
            
            page.keyboard.press('Enter')
            amount_fill_time = time.time() - fill_start
            print(f"   ✅ Сумма введена за {amount_fill_time:.2f}s")
            
            # ШАГ 3: Ждем расчета комиссии (event-driven!)
            print(f"   ⏳ Жду расчета комиссии...")
            commission_start = time.time()
            page.wait_for_function("""
                () => {
                    const input = document.querySelector('input[placeholder*="UZS"]');
                    return input && input.value && input.value !== '0 UZS' && input.value !== '';
                }
            """, timeout=5000)
            commission_time = time.time() - commission_start
            receive_value = page.locator('input[placeholder*="UZS"]').input_value()
            print(f"   ✅ Комиссия рассчитана за {commission_time:.2f}s! К получению: {receive_value}")
            
            # ШАГ 4: СРАЗУ выбираем способ платежа (без паузы!)
            print(f"\n⏱️  3️⃣ Выбираю способ платежа...")
            payment_method_start = time.time()
            
            transfer_selectors = [
                'div.css-c8d8yl:has-text("Способ перевода")',
                'div:has-text("Способ перевода")',
            ]
            
            transfer_clicked = False
            for selector in transfer_selectors:
                try:
                    transfer_block = page.locator(selector).first
                    if transfer_block.is_visible(timeout=300):
                        transfer_block.click()
                        print(f"   ✅ Открыл способ платежа")
                        transfer_clicked = True
                        break
                except:
                    continue
            
            if not transfer_clicked:
                raise Exception("Не удалось открыть способ платежа")
            
            # ШАГ 5: Выбираем банк (банки появляются сразу после клика)
            print("   ⚡ Выбираю банк Uzcard...")
            
            bank_selectors = [
                'text=Uzcard',
                '[role="button"]:has-text("Uzcard")',
            ]
            
            bank_selected = False
            for selector in bank_selectors:
                try:
                    bank_option = page.locator(selector).first
                    bank_option.wait_for(state='visible', timeout=2000)
                    bank_option.click()
                    payment_method_time = time.time() - payment_method_start
                    print(f"   ✅ Банк выбран за {payment_method_time:.2f}s")
                    bank_selected = True
                    break
                except:
                    continue
            
            if not bank_selected:
                raise Exception("Не удалось выбрать банк")
            
            # ШАГ 6: Ждем когда кнопка станет активной и СРАЗУ кликаем (event-driven!)
            print(f"\n⏱️  4️⃣ Жду активации кнопки 'Продолжить'...")
            button_start = time.time()
            
            page.wait_for_function("""
                () => {
                    const btn = document.getElementById('pay');
                    return btn && !btn.disabled;
                }
            """, timeout=10000)
            button_wait_time = time.time() - button_start
            print(f"   ✅ Кнопка активна за {button_wait_time:.2f}s, нажимаю СРАЗУ!")
            
            # Кликаем моментально
            pay_button = page.locator('#pay')
            try:
                with page.expect_navigation(timeout=10000):
                    pay_button.click()
                print("   ✅ Переход на sender-details")
            except:
                pay_button.evaluate('el => el.click()')
                page.wait_for_url('**/sender-details**', timeout=10000)
                print("   ✅ Переход на sender-details (JS)")
            
            # КОНЕЦ ОТСЧЕТА ЧИСТОГО ВРЕМЕНИ ЗАПОЛНЕНИЯ
            fill_time = time.time() - fill_start
            
            total_time = time.time() - start_time
            
            print(f"\n{'='*70}")
            print(f"⏱️  ДЕТАЛЬНАЯ СТАТИСТИКА:")
            print(f"{'='*70}")
            print(f"📊 Загрузка DOM:             {page_load_time:.2f}s")
            print(f"📊 Ожидание поля (React):    {field_wait_time:.2f}s")
            print(f"   └─ Итого загрузка:        {page_load_time + field_wait_time:.2f}s")
            print(f"")
            print(f"📊 Ввод суммы:               {amount_fill_time:.2f}s")
            print(f"📊 Расчет комиссии:          {commission_time:.2f}s")
            print(f"📊 Выбор способа + банк:     {payment_method_time:.2f}s")
            print(f"📊 Ожидание кнопки:          {button_wait_time:.2f}s")
            print(f"{'='*70}")
            print(f"✅ ЧИСТОЕ ВРЕМЯ ЗАПОЛНЕНИЯ:  {fill_time:.2f}s")
            print(f"✅ ОБЩЕЕ ВРЕМЯ (с загрузкой): {total_time:.2f}s")
            print(f"📍 URL: {page.url}")
            print(f"{'='*70}")
            
            # Держим браузер открытым для проверки
            input("\n⏸️  Нажми Enter чтобы закрыть браузер...")
            browser.close()
            
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            
            input("\n⏸️  Нажми Enter чтобы закрыть браузер...")
            browser.close()


if __name__ == "__main__":
    test_step1_only()
