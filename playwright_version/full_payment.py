#!/usr/bin/env python3
"""
Полный цикл создания платежа через Playwright
Шаг 1: Сумма + Способ перевода
Шаг 2: Данные получателя и отправителя
"""

from playwright.sync_api import sync_playwright
import time
import sys
import os

# Добавляем путь для импорта
sys.path.insert(0, os.path.dirname(__file__))

from payment_step2 import (
    fill_sender_details,
    handle_checkbox,
    click_continue,
    handle_captcha,
    handle_confirmation_modal
)


def full_payment_flow(amount: float, card_number: str, owner_name: str, headless: bool = False):
    """
    Полный цикл создания платежа
    """
    start_time = time.time()
    
    print(f"🚀 ПОЛНЫЙ ЦИКЛ СОЗДАНИЯ ПЛАТЕЖА")
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
            # ============ ШАГ 1: Сумма + Способ перевода ============
            print(f"\n{'='*70}")
            print("ШАГ 1: СУММА + СПОСОБ ПЕРЕВОДА")
            print(f"{'='*70}")
            
            step_start = time.time()
            
            # 1. Открываем страницу
            print(f"⏱️  1️⃣ Открываю страницу...")
            page.goto("https://multitransfer.ru/transfer/uzbekistan", wait_until='networkidle')
            print(f"   ✅ Загружено за {time.time() - step_start:.1f}s")
            
            # 2. Вводим сумму
            step_start = time.time()
            print(f"⏱️  2️⃣ Ввожу сумму {amount} RUB...")
            
            amount_input = page.locator('input[placeholder="0 RUB"]')
            amount_input.wait_for(state='visible')
            
            # Кликаем в поле
            amount_input.click()
            page.wait_for_timeout(100)
            
            # Очищаем
            amount_input.clear()
            page.wait_for_timeout(100)
            
            # Вводим посимвольно с паузами (как в Selenium)
            for char in str(int(amount)):
                page.keyboard.type(char)
                page.wait_for_timeout(50)
            
            # Blur для trigger React
            page.keyboard.press('Tab')
            page.wait_for_timeout(500)
            
            # Проверяем что значение установилось
            current_value = amount_input.input_value()
            print(f"   📝 Значение в поле: {current_value}")
            print(f"   ✅ Сумма введена за {time.time() - step_start:.1f}s")
            
            bank_option.scroll_into_view_if_needed()
            page.wait_for_timeout(200)
            bank_option.evaluate('el => el.click()')
            
            print(f"   ✅ Банк выбран за {time.time() - step_start:.1f}s")
            
            # 3. Нажимаем Продолжить
            step_start = time.time()
            print(f"⏱️  5️⃣ Нажимаю 'Продолжить'...")
            
            try:
                page.wait_for_function("""
                    () => {
                        const btn = document.getElementById('pay');
                        return btn && !btn.disabled;
                    }
                """, timeout=10000)
                print(f"   ✅ Кнопка активирована")
            except:
                print(f"   ⚠️  Кнопка disabled, кликаю через JS")
            
            pay_button = page.locator('#pay')
            
            try:
                with page.expect_navigation(timeout=10000):
                    pay_button.evaluate('el => el.click()')
            except:
                pay_button.click(force=True)
                page.wait_for_url('**/sender-details**', timeout=10000)
            
            print(f"   ✅ Переход за {time.time() - step_start:.1f}s")
            print(f"   📍 URL: {page.url}")
            
            # ============ ШАГ 2: Заполнение данных ============
            print(f"\n{'='*70}")
            print("ШАГ 2: ЗАПОЛНЕНИЕ ДАННЫХ")
            print(f"{'='*70}")
            
            step_start = time.time()
            
            # Заполняем все поля
            fill_sender_details(page, card_number, owner_name)
            
            # Ставим галочку
            handle_checkbox(page)
            
            # Нажимаем Продолжить
            click_continue(page)
            
            # Проверяем капчу
            handle_captcha(page)
            
            # Проверяем модалку подтверждения
            handle_confirmation_modal(page)
            
            # Ждем перехода на страницу оплаты
            print("\n📌 Ожидаю перехода на страницу оплаты...")
            
            for i in range(40):  # 20 секунд максимум
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
            
            # Итоговое время
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


def test_full_payment():
    """Тест полного цикла"""
    result = full_payment_flow(
        amount=110,
        card_number="8600123456789012",
        owner_name="Иван Иванов",
        headless=False
    )
    
    if result['success']:
        print(f"\n🎉 Успех! Время: {result['elapsed_time']:.1f}s")
    else:
        print(f"\n❌ Ошибка: {result.get('error')}")


if __name__ == "__main__":
    test_full_payment()
