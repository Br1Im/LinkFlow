#!/usr/bin/env python3
"""
БЫСТРАЯ ВЕРСИЯ - ЧАСТЬ 1: Сумма + Способ платежа
Оптимизировано для максимальной скорости:
- Использует domcontentloaded вместо networkidle
- Ожидает состояния элементов вместо фиксированных таймаутов
- Минимальные паузы между действиями
"""

from playwright.sync_api import sync_playwright
import time


def fast_step1(amount: float, headless: bool = False):
    """
    Быстрое прохождение первого шага
    Возвращает URL страницы sender-details
    """
    start_time = time.time()
    
    print(f"🚀 БЫСТРАЯ ВЕРСИЯ - ШАГ 1")
    print("="*70)
    print(f"💰 Сумма: {amount} RUB")
    print("="*70)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            # ШАГ 1: Открываем страницу (быстрая загрузка)
            print(f"\n⏱️  1️⃣ Открываю страницу...")
            page.goto("https://multitransfer.ru/transfer/uzbekistan", wait_until='domcontentloaded')
            print(f"   ✅ DOM загружен")
            
            # ШАГ 2: Вводим сумму
            print(f"\n⏱️  2️⃣ Ввожу сумму {amount} RUB...")
            
            amount_input = page.locator('input[placeholder="0 RUB"]')
            amount_input.wait_for(state='visible', timeout=5000)
            
            # Кликаем и очищаем
            amount_input.click()
            page.wait_for_timeout(100)
            page.keyboard.press('Control+A')
            page.wait_for_timeout(30)
            page.keyboard.press('Backspace')
            page.wait_for_timeout(50)
            
            # Вводим посимвольно
            amount_str = str(int(amount))
            for char in amount_str:
                page.keyboard.type(char)
                page.wait_for_timeout(50)
            
            # Enter для подтверждения
            page.keyboard.press('Enter')
            page.wait_for_timeout(300)
            
            current_value = amount_input.input_value()
            print(f"   ✅ Введено: {current_value}")
            
            # Ждем расчета комиссии
            print(f"   ⏳ Жду расчета комиссии...")
            try:
                page.wait_for_function("""
                    () => {
                        const input = document.querySelector('input[placeholder*="UZS"]');
                        return input && input.value && input.value !== '0 UZS' && input.value !== '';
                    }
                """, timeout=5000)
                receive_value = page.locator('input[placeholder*="UZS"]').input_value()
                print(f"   ✅ Комиссия рассчитана. К получению: {receive_value}")
            except:
                print(f"   ⚠️ Не дождался расчета, но продолжаю")
            
            # ШАГ 2.5: Выбираем способ платежа
            print(f"\n⏱️  2.5️⃣ Выбираю способ платежа...")
            
            transfer_clicked = False
            transfer_selectors = [
                'div.css-c8d8yl:has-text("Способ перевода")',
                'div:has-text("Способ перевода")',
            ]
            
            for selector in transfer_selectors:
                try:
                    transfer_block = page.locator(selector).first
                    if transfer_block.is_visible(timeout=1000):
                        transfer_block.click()
                        print(f"   ✅ Открыл способ платежа")
                        transfer_clicked = True
                        break
                except:
                    continue
            
            if transfer_clicked:
                # Ждем появления банка
                bank_selectors = [
                    '[role="button"]:has-text("Uzcard")',
                    'text=Uzcard',
                ]
                
                for selector in bank_selectors:
                    try:
                        bank_option = page.locator(selector).first
                        bank_option.wait_for(state='visible', timeout=2000)
                        bank_option.click()
                        print(f"   ✅ Банк выбран")
                        break
                    except:
                        continue
            
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
                print("   ⚠️ Кнопка disabled, но пробуем кликнуть")
            
            pay_button = page.locator('#pay')
            
            # Кликаем
            try:
                with page.expect_navigation(timeout=10000):
                    pay_button.click()
            except:
                pay_button.evaluate('el => el.click()')
                page.wait_for_url('**/sender-details**', timeout=10000)
            
            print(f"   ✅ Переход на sender-details")
            
            total_time = time.time() - start_time
            final_url = page.url
            
            print(f"\n{'='*70}")
            print(f"✅ ШАГ 1 ЗАВЕРШЕН ЗА {total_time:.1f}s")
            print(f"📍 URL: {final_url}")
            print(f"{'='*70}")
            
            input("\nНажми Enter чтобы закрыть браузер...")
            browser.close()
            
            return {
                'success': True,
                'elapsed_time': total_time,
                'url': final_url
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
    """Тест быстрой версии"""
    result = fast_step1(amount=110, headless=False)
    
    if result['success']:
        print(f"\n🎉 Успех! Время: {result['elapsed_time']:.1f}s")
    else:
        print(f"\n❌ Ошибка: {result.get('error')}")


if __name__ == "__main__":
    test()
