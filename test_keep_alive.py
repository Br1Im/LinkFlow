#!/usr/bin/env python3
"""
Keep-alive режим - браузер остается открытым между платежами
"""

from playwright.sync_api import sync_playwright
import time

def create_payment_keep_alive(page, amount, card_number, owner_name):
    """Создать платеж на уже открытой странице"""
    fill_start = time.time()
    
    print(f"\n{'='*70}")
    print(f"🚀 СОЗДАНИЕ ПЛАТЕЖА (KEEP-ALIVE)")
    print(f"💰 Сумма: {amount} RUB")
    print(f"{'='*70}")
    
    try:
        # ШАГ 1: Очищаем форму (если нужно) - просто обновляем страницу
        print(f"\n⏱️  1️⃣ Обновляю форму...")
        refresh_start = time.time()
        page.reload(wait_until='domcontentloaded')
        refresh_time = time.time() - refresh_start
        print(f"   ✅ Форма обновлена за {refresh_time:.2f}s")
        
        # НАЧИНАЕМ ОТСЧЕТ ЧИСТОГО ВРЕМЕНИ
        fill_start = time.time()
        
        # ШАГ 2: Поле уже видно - сразу вводим!
        print(f"\n⏱️  2️⃣ Ввожу сумму {amount} RUB...")
        amount_input = page.locator('input[placeholder="0 RUB"]')
        amount_input.wait_for(state='visible', timeout=2000)
        
        amount_input.click()
        page.keyboard.press('Control+A')
        page.keyboard.press('Backspace')
        
        amount_str = str(int(amount))
        for char in amount_str:
            page.keyboard.type(char)
        
        page.keyboard.press('Enter')
        amount_fill_time = time.time() - fill_start
        print(f"   ✅ Сумма введена за {amount_fill_time:.2f}s")
        
        # ШАГ 3: Ждем расчета комиссии
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
        
        # ШАГ 4: Выбираем способ платежа
        print(f"\n⏱️  3️⃣ Выбираю способ платежа...")
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
        
        # ШАГ 5: Выбираем банк
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
        
        # ШАГ 6: Ждем кнопку и кликаем
        print(f"\n⏱️  4️⃣ Жду активации кнопки 'Продолжить'...")
        button_start = time.time()
        
        page.wait_for_function("""
            () => {
                const btn = document.getElementById('pay');
                return btn && !btn.disabled;
            }
        """, timeout=10000)
        button_wait_time = time.time() - button_start
        print(f"   ✅ Кнопка активна за {button_wait_time:.2f}s, нажимаю!")
        
        pay_button = page.locator('#pay')
        try:
            with page.expect_navigation(timeout=10000):
                pay_button.click()
            print("   ✅ Переход на sender-details")
        except:
            pay_button.evaluate('el => el.click()')
            page.wait_for_url('**/sender-details**', timeout=10000)
            print("   ✅ Переход на sender-details (JS)")
        
        fill_time = time.time() - fill_start
        
        print(f"\n{'='*70}")
        print(f"⏱️  СТАТИСТИКА (KEEP-ALIVE):")
        print(f"{'='*70}")
        print(f"📊 Обновление формы:         {refresh_time:.2f}s")
        print(f"📊 Ввод суммы:               {amount_fill_time:.2f}s")
        print(f"📊 Расчет комиссии:          {commission_time:.2f}s")
        print(f"📊 Выбор способа + банк:     {payment_method_time:.2f}s")
        print(f"📊 Ожидание кнопки:          {button_wait_time:.2f}s")
        print(f"{'='*70}")
        print(f"✅ ЧИСТОЕ ВРЕМЯ ЗАПОЛНЕНИЯ:  {fill_time:.2f}s")
        print(f"📍 URL: {page.url}")
        print(f"{'='*70}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_keep_alive():
    """Тест keep-alive режима"""
    
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
        
        # Первая загрузка страницы
        print(f"🌐 Первая загрузка страницы...")
        initial_load_start = time.time()
        page.goto("https://multitransfer.ru/transfer/uzbekistan", wait_until='domcontentloaded')
        
        # Ждем полной загрузки React
        page.locator('input[placeholder="0 RUB"]').wait_for(state='visible', timeout=5000)
        initial_load_time = time.time() - initial_load_start
        print(f"✅ Страница загружена за {initial_load_time:.2f}s")
        print(f"💡 Теперь браузер остается открытым для быстрых платежей!")
        
        # Создаем несколько платежей подряд
        for i in range(3):
            print(f"\n\n{'#'*70}")
            print(f"# ПЛАТЕЖ #{i+1}")
            print(f"{'#'*70}")
            
            success = create_payment_keep_alive(
                page=page,
                amount=100 + i * 10,
                card_number="9860080323894719",
                owner_name="Nodir Asadullayev"
            )
            
            if not success:
                break
            
            if i < 2:
                input(f"\n⏸️  Нажми Enter для создания следующего платежа...")
        
        input("\n⏸️  Нажми Enter чтобы закрыть браузер...")
        browser.close()


if __name__ == "__main__":
    test_keep_alive()
