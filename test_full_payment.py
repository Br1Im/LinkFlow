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
            # Устанавливаем автоматическое закрытие модалки с ошибкой через JavaScript
            page.evaluate("""
                () => {
                    // Функция для закрытия модалки
                    const closeErrorModal = () => {
                        const buttons = document.querySelectorAll('button[buttontext="Понятно"]');
                        buttons.forEach(btn => {
                            if (btn.textContent.includes('Понятно')) {
                                console.log('🔴 Закрываю модалку с ошибкой...');
                                btn.click();
                            }
                        });
                    };
                    
                    // Проверяем каждые 100ms
                    setInterval(closeErrorModal, 100);
                    
                    // Также используем MutationObserver для мгновенной реакции
                    const observer = new MutationObserver(() => {
                        closeErrorModal();
                    });
                    
                    observer.observe(document.body, {
                        childList: true,
                        subtree: true
                    });
                }
            """)
            
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
            print(f"   ✅ Установлен автоматический закрыватель модалок с ошибками")
            
            # Ждем поля
            print(f"   ⏳ Жду появления поля...")
            field_wait_start = time.time()
            amount_input = page.locator('input[placeholder="0 RUB"]')
            amount_input.wait_for(state='visible', timeout=5000)
            field_wait_time = time.time() - field_wait_start
            print(f"   ✅ Поле появилось за {field_wait_time:.2f}s")
            
            # НАЧАЛО ЭТАПА 1
            step1_start = time.time()
            
            # Ввод суммы с retry логикой
            print(f"\n⏱️  Ввожу сумму {amount} RUB...")
            
            amount_str = str(int(amount))
            commission_calculated = False
            max_retries = 3
            
            for attempt in range(max_retries):
                if attempt > 0:
                    print(f"   🔄 Попытка #{attempt + 1}...")
                
                # Вводим через клавиатуру
                amount_input.click()
                page.wait_for_timeout(100)
                page.keyboard.press('Control+A')
                page.keyboard.press('Backspace')
                page.wait_for_timeout(50)
                
                for char in amount_str:
                    page.keyboard.type(char)
                    page.wait_for_timeout(50)  # Небольшая задержка между символами
                
                # Триггерим события через JavaScript для надежности
                amount_input.evaluate("""
                    (element) => {
                        element.dispatchEvent(new Event('input', { bubbles: true }));
                        element.dispatchEvent(new Event('change', { bubbles: true }));
                        element.dispatchEvent(new Event('blur', { bubbles: true }));
                    }
                """)
                
                page.keyboard.press('Enter')
                page.wait_for_timeout(300)  # Даем время на обработку
                
                # Проверяем что комиссия рассчиталась
                print(f"   ⏳ Жду расчета комиссии (попытка {attempt + 1}/{max_retries})...")
                
                try:
                    page.wait_for_function("""
                        () => {
                            const input = document.querySelector('input[placeholder*="UZS"]');
                            if (!input) return false;
                            const val = input.value;
                            return val && val !== '0 UZS' && val !== '' && val !== '0';
                        }
                    """, timeout=3000)
                    
                    receive_value = page.locator('input[placeholder*="UZS"]').input_value()
                    print(f"   ✅ Комиссия рассчитана! К получению: {receive_value}")
                    commission_calculated = True
                    break
                except:
                    # Отладка: смотрим что в полях
                    debug_info = page.evaluate("""
                        () => {
                            const rubInput = document.querySelector('input[placeholder*="RUB"]');
                            const uzsInput = document.querySelector('input[placeholder*="UZS"]');
                            return {
                                rubValue: rubInput ? rubInput.value : 'NOT FOUND',
                                uzsValue: uzsInput ? uzsInput.value : 'NOT FOUND'
                            };
                        }
                    """)
                    print(f"   ⚠️ Комиссия не рассчиталась. RUB={debug_info['rubValue']}, UZS={debug_info['uzsValue']}")
                    
                    if attempt < max_retries - 1:
                        print(f"   🔄 Пробую еще раз...")
                        page.wait_for_timeout(500)
            
            if not commission_calculated:
                print(f"   ❌ Не удалось рассчитать комиссию за {max_retries} попыток!")
                raise Exception("Комиссия не рассчиталась - проверьте ввод суммы")
            
            amount_fill_time = time.time() - step1_start
            print(f"   ✅ Сумма введена за {amount_fill_time:.2f}s")
            commission_time = amount_fill_time  # Для статистики
            
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
            print(f"   Ввод суммы + комиссия:    {amount_fill_time:.2f}s")
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
