#!/usr/bin/env python3
"""
Полный тест - оба этапа с детальной статистикой
"""

from playwright.sync_api import sync_playwright
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'playwright_version'))

from payment_step2 import complete_payment_step2


def test_full_payment():
    """Полный тест обоих этапов"""
    start_time = time.time()
    amount = 110
    card_number = "9860080323894719"
    owner_name = "Nodir Asadullayev"
    
    print(f"🚀 ПОЛНЫЙ ТЕСТ: ОБА ЭТАПА")
    print("="*70)
    print(f"💰 Сумма: {amount} RUB")
    print(f"💳 Карта: {card_number}")
    print(f"👤 Владелец: {owner_name}")
    print("="*70)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
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
            # ============ ЭТАП 1: ВВОД СУММЫ И ВЫБОР СПОСОБА ============
            print(f"\n{'='*70}")
            print("ЭТАП 1: ВВОД СУММЫ И ВЫБОР СПОСОБА ПЛАТЕЖА")
            print(f"{'='*70}")
            
            # Загрузка страницы
            print(f"\n⏱️  Открываю страницу...")
            page_load_start = time.time()
            page.goto("https://multitransfer.ru/transfer/uzbekistan", wait_until='domcontentloaded')
            page_load_time = time.time() - page_load_start
            print(f"   ✅ DOM загружен за {page_load_time:.2f}s")
            
            # Ждем поля
            print(f"   ⏳ Жду появления поля...")
            field_wait_start = time.time()
            amount_input = page.locator('input[placeholder="0 RUB"]')
            amount_input.wait_for(state='visible', timeout=5000)
            field_wait_time = time.time() - field_wait_start
            print(f"   ✅ Поле появилось за {field_wait_time:.2f}s")
            
            # НАЧАЛО ЭТАПА 1
            step1_start = time.time()
            
            # Ввод суммы
            print(f"\n⏱️  Ввожу сумму {amount} RUB...")
            amount_input.click()
            page.keyboard.press('Control+A')
            page.keyboard.press('Backspace')
            
            amount_str = str(int(amount))
            for char in amount_str:
                page.keyboard.type(char)
            
            page.keyboard.press('Enter')
            
            # Проверяем что сумма действительно введена
            page.wait_for_timeout(200)  # Даем React время обработать
            current_value = amount_input.input_value()
            print(f"   ✅ Значение в поле: {current_value}")
            
            # Если сумма не введена правильно - пробуем через fill
            if amount_str not in current_value:
                print(f"   ⚠️ Сумма не введена, пробую через fill()...")
                amount_input.fill(amount_str)
                page.keyboard.press('Enter')
                page.wait_for_timeout(200)
                current_value = amount_input.input_value()
                print(f"   ✅ Новое значение: {current_value}")
            
            amount_fill_time = time.time() - step1_start
            print(f"   ✅ Сумма введена за {amount_fill_time:.2f}s")
            
            # Расчет комиссии
            print(f"   ⏳ Жду расчета комиссии...")
            commission_start = time.time()
            try:
                page.wait_for_function("""
                    () => {
                        const input = document.querySelector('input[placeholder*="UZS"]');
                        return input && input.value && input.value !== '0 UZS' && input.value !== '';
                    }
                """, timeout=8000)  # Увеличиваем таймаут
                commission_time = time.time() - commission_start
                receive_value = page.locator('input[placeholder*="UZS"]').input_value()
                print(f"   ✅ Комиссия рассчитана за {commission_time:.2f}s! К получению: {receive_value}")
            except:
                commission_time = time.time() - commission_start
                print(f"   ❌ Комиссия не рассчиталась за {commission_time:.2f}s!")
                # Делаем скриншот
                page.screenshot(path="./debug_commission_error.png")
                print(f"   📸 Скриншот: debug_commission_error.png")
                raise Exception("Комиссия не рассчиталась - проверьте ввод суммы")
            
            # Выбор способа платежа
            print(f"\n⏱️  Выбираю способ платежа...")
            payment_method_start = time.time()
            
            transfer_selectors = [
                'div.css-c8d8yl:has-text("Способ перевода")',
                'div:has-text("Способ перевода")',
            ]
            
            for selector in transfer_selectors:
                try:
                    transfer_block = page.locator(selector).first
                    if transfer_block.is_visible(timeout=300):
                        transfer_block.click()
                        print(f"   ✅ Открыл способ платежа")
                        break
                except:
                    continue
            
            # Выбор банка
            print("   ⚡ Выбираю банк Uzcard...")
            
            bank_selectors = [
                'text=Uzcard',
                '[role="button"]:has-text("Uzcard")',
            ]
            
            for selector in bank_selectors:
                try:
                    bank_option = page.locator(selector).first
                    bank_option.wait_for(state='visible', timeout=2000)
                    bank_option.click()
                    payment_method_time = time.time() - payment_method_start
                    print(f"   ✅ Банк выбран за {payment_method_time:.2f}s")
                    break
                except:
                    continue
            
            # Ожидание кнопки
            print(f"\n⏱️  Жду активации кнопки 'Продолжить'...")
            button_start = time.time()
            
            page.wait_for_function("""
                () => {
                    const btn = document.getElementById('pay');
                    return btn && !btn.disabled;
                }
            """, timeout=10000)
            button_wait_time = time.time() - button_start
            print(f"   ✅ Кнопка активна за {button_wait_time:.2f}s, нажимаю!")
            
            # Клик
            pay_button = page.locator('#pay')
            try:
                with page.expect_navigation(timeout=10000):
                    pay_button.click()
                print("   ✅ Переход на sender-details")
            except:
                pay_button.evaluate('el => el.click()')
                page.wait_for_url('**/sender-details**', timeout=10000)
                print("   ✅ Переход на sender-details (JS)")
            
            step1_time = time.time() - step1_start
            
            # ============ ЭТАП 2: ЗАПОЛНЕНИЕ ДАННЫХ ============
            print(f"\n{'='*70}")
            print("ЭТАП 2: ЗАПОЛНЕНИЕ ДАННЫХ")
            print(f"{'='*70}")
            
            step2_start = time.time()
            step2_success = complete_payment_step2(page, card_number, owner_name)
            step2_time = time.time() - step2_start
            
            if step2_success:
                print(f"\n✅ Этап 2 завершен успешно за {step2_time:.2f}s!")
            else:
                print(f"\n⚠️ Этап 2 завершен с проблемами за {step2_time:.2f}s")
            
            # ============ ИТОГОВАЯ СТАТИСТИКА ============
            total_time = time.time() - start_time
            fill_time = step1_time + step2_time
            
            print(f"\n{'='*70}")
            print(f"⏱️  ДЕТАЛЬНАЯ СТАТИСТИКА:")
            print(f"{'='*70}")
            print(f"")
            print(f"📦 ЗАГРУЗКА:")
            print(f"   DOM загрузка:             {page_load_time:.2f}s")
            print(f"   Ожидание поля (React):    {field_wait_time:.2f}s")
            print(f"   └─ Итого загрузка:        {page_load_time + field_wait_time:.2f}s")
            print(f"")
            print(f"⚡ ЭТАП 1 (Ввод суммы и выбор):")
            print(f"   Ввод суммы:               {amount_fill_time:.2f}s")
            print(f"   Расчет комиссии:          {commission_time:.2f}s")
            print(f"   Выбор способа + банк:     {payment_method_time:.2f}s")
            print(f"   Ожидание кнопки:          {button_wait_time:.2f}s")
            print(f"   └─ Итого этап 1:          {step1_time:.2f}s")
            print(f"")
            print(f"📝 ЭТАП 2 (Заполнение данных):")
            print(f"   Время заполнения:         {step2_time:.2f}s")
            print(f"")
            print(f"{'='*70}")
            print(f"✅ ЧИСТОЕ ВРЕМЯ ЗАПОЛНЕНИЯ:  {fill_time:.2f}s")
            print(f"✅ ОБЩЕЕ ВРЕМЯ (с загрузкой): {total_time:.2f}s")
            print(f"📍 Финальный URL: {page.url}")
            print(f"{'='*70}")
            
            # Держим браузер открытым
            input("\n⏸️  Нажми Enter чтобы закрыть браузер...")
            browser.close()
            
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            
            input("\n⏸️  Нажми Enter чтобы закрыть браузер...")
            browser.close()


if __name__ == "__main__":
    test_full_payment()
