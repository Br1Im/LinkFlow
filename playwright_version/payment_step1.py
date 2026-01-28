#!/usr/bin/env python3
"""
Playwright версия - Шаг 1: Сумма + Способ перевода + Продолжить
По логике рабочего Selenium кода
"""

from playwright.sync_api import sync_playwright
import time


class PaymentStep1:
    """Первый шаг создания платежа - до страницы sender-details"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.url = "https://multitransfer.ru/transfer/uzbekistan"
    
    def fill_amount_and_continue(self, amount: float) -> dict:
        """
        Заполняет сумму, выбирает способ перевода, нажимает Продолжить
        """
        start_time = time.time()
        
        print(f"🚀 Playwright - Шаг 1: Сумма {amount} RUB")
        print("="*70)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                # 1. Открываем страницу
                step_start = time.time()
                print(f"⏱️  [{self._time()}] 1️⃣ Открываю страницу...")
                page.goto(self.url, wait_until='networkidle')
                print(f"   ✅ Загружено за {time.time() - step_start:.1f}s")
                
                # 2. Вводим сумму (используем fill с delay)
                step_start = time.time()
                print(f"⏱️  [{self._time()}] 2️⃣ Ввожу сумму {amount} RUB...")
                
                amount_input = page.locator('input[placeholder="0 RUB"]')
                amount_input.wait_for(state='visible')
                
                # Кликаем в поле
                amount_input.click()
                page.wait_for_timeout(100)
                
                # Очищаем
                page.keyboard.press('Control+A')
                page.keyboard.press('Backspace')
                page.wait_for_timeout(100)
                
                # Вводим с задержкой между символами
                amount_input.type(str(int(amount)), delay=50)
                
                # Клик вне поля для trigger blur
                page.evaluate('document.body.click()')
                page.wait_for_timeout(500)  # Даем React время обработать
                
                print(f"   ✅ Сумма введена за {time.time() - step_start:.1f}s")
                
                # 3. Ждем активации кнопки
                step_start = time.time()
                print(f"⏱️  [{self._time()}] 3️⃣ Жду активации кнопки...")
                
                # Ждем пока кнопка станет enabled
                try:
                    page.wait_for_function("""
                        () => {
                            const btn = document.getElementById('pay');
                            return btn && !btn.disabled;
                        }
                    """, timeout=5000)
                    print(f"   ✅ Кнопка активна за {time.time() - step_start:.1f}s")
                except:
                    print(f"   ⚠️  Кнопка не активировалась, но продолжаем")
                
                # 4. Открываем "Способ перевода"
                step_start = time.time()
                print(f"⏱️  [{self._time()}] 4️⃣ Открываю 'Способ перевода'...")
                
                # Пробуем разные селекторы (как в Selenium)
                selectors = [
                    'text=Способ перевода',
                    'div:has-text("Способ перевода")',
                    '[class*="variant-alternative"]:has-text("Способ перевода")'
                ]
                
                transfer_block = None
                for selector in selectors:
                    try:
                        transfer_block = page.locator(selector).first
                        if transfer_block.is_visible(timeout=2000):
                            break
                    except:
                        continue
                
                if not transfer_block:
                    raise Exception("Не удалось найти блок 'Способ перевода'")
                
                # Кликаем через JS (как click_mui_element)
                transfer_block.evaluate('el => el.scrollIntoView({block: "center"})')
                page.wait_for_timeout(100)
                transfer_block.evaluate('el => el.click()')
                
                print(f"   ✅ Блок открыт за {time.time() - step_start:.1f}s")
                
                # 5. Выбираем Uzcard/Humo
                step_start = time.time()
                print(f"⏱️  [{self._time()}] 5️⃣ Выбираю Uzcard / Humo...")
                
                # Ждем появления кнопок выбора банка
                page.wait_for_selector('[role="button"][aria-label*="Uzcard"]', state='visible', timeout=5000)
                
                # Небольшая пауза для загрузки модалки
                page.wait_for_timeout(300)
                
                # Пробуем разные селекторы для Uzcard/Humo
                selectors = [
                    '[role="button"][aria-label*="Uzcard"]',
                    '[role="button"]:has-text("Uzcard/Humo")',
                    'div.css-1lvwieb:has-text("Uzcard/Humo")',
                    'text=Uzcard/Humo'
                ]
                
                bank_option = None
                for selector in selectors:
                    try:
                        bank_option = page.locator(selector).first
                        if bank_option.is_visible(timeout=1000):
                            print(f"   ✓ Найден через: {selector}")
                            break
                    except:
                        continue
                
                if not bank_option:
                    raise Exception("Не удалось найти кнопку Uzcard/Humo")
                
                # Прокручиваем к элементу
                bank_option.scroll_into_view_if_needed()
                page.wait_for_timeout(200)
                
                # Пробуем клик через JS (надежнее для MUI)
                bank_option.evaluate('el => el.click()')
                
                print(f"   ✅ Банк выбран за {time.time() - step_start:.1f}s")
                
                # 6. Нажимаем Продолжить
                step_start = time.time()
                print(f"⏱️  [{self._time()}] 6️⃣ Нажимаю 'Продолжить'...")
                
                # Ждем пока кнопка станет enabled после выбора банка
                try:
                    page.wait_for_function("""
                        () => {
                            const btn = document.getElementById('pay');
                            return btn && !btn.disabled;
                        }
                    """, timeout=10000)
                    print(f"   ✅ Кнопка активирована")
                except:
                    print(f"   ⚠️  Кнопка всё еще disabled, кликаю через JS")
                
                # Кликаем и ждем навигации
                pay_button = page.locator('#pay')
                
                try:
                    with page.expect_navigation(timeout=10000):
                        pay_button.evaluate('el => el.click()')
                except:
                    # Если навигация не произошла, пробуем обычный клик
                    pay_button.click(force=True)
                    page.wait_for_url('**/sender-details**', timeout=10000)
                
                final_url = page.url
                print(f"   ✅ Переход за {time.time() - step_start:.1f}s")
                print(f"   📍 URL: {final_url}")
                
                # Проверяем что попали на sender-details
                if 'sender-details' in final_url:
                    total_time = time.time() - start_time
                    
                    print()
                    print("="*70)
                    print(f"✅ ШАГ 1 ЗАВЕРШЕН ЗА {total_time:.1f}s")
                    print("="*70)
                    
                    input("\nНажми Enter чтобы закрыть браузер...")
                    browser.close()
                    
                    return {
                        'success': True,
                        'elapsed_time': total_time,
                        'final_url': final_url
                    }
                else:
                    browser.close()
                    return {
                        'success': False,
                        'elapsed_time': time.time() - start_time,
                        'final_url': final_url,
                        'error': f'Неожиданный URL: {final_url}'
                    }
                    
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                import traceback
                traceback.print_exc()
                
                input("\nНажми Enter чтобы закрыть браузер...")
                browser.close()
                
                return {
                    'success': False,
                    'elapsed_time': time.time() - start_time,
                    'error': str(e)
                }
    
    def _time(self):
        """Текущее время для логов"""
        return time.strftime('%H:%M:%S')


def test_step1():
    """Тест первого шага"""
    step1 = PaymentStep1(headless=False)
    
    result = step1.fill_amount_and_continue(amount=110)
    
    if result['success']:
        print(f"\n🎉 Успех! Время: {result['elapsed_time']:.1f}s")
        print(f"📍 URL: {result['final_url']}")
    else:
        print(f"\n❌ Ошибка: {result.get('error')}")


if __name__ == "__main__":
    test_step1()
