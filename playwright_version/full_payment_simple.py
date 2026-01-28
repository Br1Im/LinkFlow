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
    fill_sender_details,
    handle_checkbox,
    click_continue,
    handle_captcha,
    handle_confirmation_modal
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
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            # ШАГ 1: Открываем страницу
            print(f"\n⏱️  1️⃣ Открываю страницу...")
            page.goto("https://multitransfer.ru/transfer/uzbekistan", wait_until='domcontentloaded')  # Меняем на domcontentloaded
            print(f"   ✅ DOM загружен")
            
            # ШАГ 2: Вводим сумму (сразу после DOM)
            print(f"\n⏱️  2️⃣ Ввожу сумму {amount} RUB...")
            
            # Ждем только появления поля (не ждем networkidle)
            amount_input = page.locator('input[placeholder="0 RUB"]')
            amount_input.wait_for(state='visible', timeout=5000)
            
            # Кликаем в поле
            amount_input.click()
            page.wait_for_timeout(100)  # Уменьшаем с 200
            
            # Очищаем через выделение и удаление
            page.keyboard.press('Control+A')
            page.wait_for_timeout(30)  # Уменьшаем с 50
            page.keyboard.press('Backspace')
            page.wait_for_timeout(50)  # Уменьшаем с 100
            
            # Вводим посимвольно с паузами
            amount_str = str(int(amount))
            for i, char in enumerate(amount_str):
                page.keyboard.type(char)
                page.wait_for_timeout(50)  # Минимальная пауза
            
            # Нажимаем Enter для подтверждения
            page.keyboard.press('Enter')
            page.wait_for_timeout(300)  # Уменьшаем с 500 до 300
            
            current_value = amount_input.input_value()
            print(f"   ✅ Введено: {current_value}")
            
            # Ждем пока React рассчитает комиссию и курс
            print(f"   ⏳ Жду расчета комиссии...")
            try:
                # Ждем появления рассчитанной суммы к получению (не пустое значение)
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
            
            # ШАГ 2.5: Выбираем способ платежа (доступен сразу после расчета)
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
                    if transfer_block.is_visible(timeout=1000):
                        transfer_block.click()
                        print(f"   ✅ Открыл способ платежа")
                        transfer_clicked = True
                        break
                except:
                    continue
            
            if transfer_clicked:
                # Банк появляется мгновенно - ждем только видимости
                bank_selectors = [
                    '[role="button"]:has-text("Uzcard")',
                    'text=Uzcard',
                ]
                
                for selector in bank_selectors:
                    try:
                        bank_option = page.locator(selector).first
                        # Ждем появления элемента
                        bank_option.wait_for(state='visible', timeout=2000)
                        bank_option.click()
                        print(f"   ✅ Банк выбран")
                        break
                    except:
                        continue
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
                # Если не сработало, пробуем через JS
                pay_button.evaluate('el => el.click()')
                page.wait_for_url('**/sender-details**', timeout=10000)
            
            print(f"   ✅ Переход на sender-details")
            print(f"   📍 URL: {page.url}")
            
            # ============ ШАГ 2: Заполнение данных ============
            print(f"\n{'='*70}")
            print("ШАГ 2: ЗАПОЛНЕНИЕ ДАННЫХ")
            print(f"{'='*70}")
            
            fill_sender_details(page, card_number, owner_name)
            handle_checkbox(page)
            click_continue(page)
            handle_captcha(page)
            handle_confirmation_modal(page)
            
            # Ждем перехода на страницу оплаты
            print("\n📌 Ожидаю перехода на страницу оплаты...")
            
            for i in range(40):
                page.wait_for_timeout(500)
                current_url = page.url
                
                if "payment" in current_url or "result" in current_url or "/pay/" in current_url:
                    print(f"✅ Переход на страницу оплаты!")
                    print(f"📍 URL: {current_url}")
                    break
                
                if i % 4 == 0:
                    print(f"   ⏳ Ожидание... ({i//2}s)")
            else:
                print(f"⚠️ Не дождались перехода")
                print(f"📍 Текущий URL: {page.url}")
            
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
