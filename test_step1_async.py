#!/usr/bin/env python3
"""
Тест только первого этапа - async версия для отладки
"""

from playwright.async_api import async_playwright
import asyncio
import time


async def test_step1_multiple_times(runs=5):
    """Тестируем этап 1 несколько раз"""
    
    results = []
    
    for run in range(runs):
        print(f"\n{'='*70}")
        print(f"ЗАПУСК #{run + 1} из {runs}")
        print(f"{'='*70}")
        
        start_time = time.time()
        amount = 110
        success = False
        error_msg = None
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            page = await context.new_page()
            
            try:
                # Автозакрыватель модалок
                await page.evaluate("""
                    () => {
                        const closeErrorModal = () => {
                            const buttons = document.querySelectorAll('button[buttontext="Понятно"]');
                            buttons.forEach(btn => {
                                if (btn.textContent.includes('Понятно')) btn.click();
                            });
                        };
                        setInterval(closeErrorModal, 50);
                        const observer = new MutationObserver(() => closeErrorModal());
                        observer.observe(document.body, { childList: true, subtree: true });
                    }
                """)
                
                # Загрузка
                await page.goto("https://multitransfer.ru/transfer/uzbekistan", wait_until='domcontentloaded')
                
                # Ждем поле
                amount_input = page.locator('input[placeholder="0 RUB"]')
                await amount_input.wait_for(state='visible', timeout=5000)
                
                # Ввод суммы с retry
                commission_ok = False
                for attempt in range(5):  # Увеличиваем с 3 до 5
                    if attempt > 0:
                        print(f"   🔄 Попытка #{attempt + 1}")
                    
                    # Закрываем модалку
                    try:
                        await page.evaluate("""
                            () => {
                                const buttons = document.querySelectorAll('button[buttontext="Понятно"]');
                                buttons.forEach(btn => {
                                    if (btn.textContent.includes('Понятно')) btn.click();
                                });
                            }
                        """)
                        await page.wait_for_timeout(100)
                    except:
                        pass
                    
                    # Вводим
                    await amount_input.click(force=True)
                    await page.wait_for_timeout(100)
                    await page.keyboard.press('Control+A')
                    await page.keyboard.press('Backspace')
                    await page.wait_for_timeout(50)
                    
                    for char in str(amount):
                        await page.keyboard.type(char)
                        await page.wait_for_timeout(30)  # Уменьшаем с 50 до 30
                    
                    await page.keyboard.press('Enter')
                    await page.wait_for_timeout(200)  # Уменьшаем с 300 до 200
                    
                    # Проверяем комиссию
                    try:
                        await page.wait_for_function("""
                            () => {
                                const input = document.querySelector('input[placeholder*="UZS"]');
                                return input && input.value && input.value !== '0 UZS' && input.value !== '';
                            }
                        """, timeout=3000)
                        print("   ✅ Комиссия рассчитана")
                        commission_ok = True
                        break
                    except:
                        print(f"   ⚠️ Комиссия не рассчиталась")
                        if attempt < 2:
                            await page.wait_for_timeout(500)
                
                if not commission_ok:
                    raise Exception("Не удалось рассчитать комиссию за 5 попыток")
                
                # Выбор способа платежа - надежный метод
                transfer_selectors = [
                    'div.css-c8d8yl:has-text("Способ перевода")',
                    'div:has-text("Способ перевода")',
                ]
                
                transfer_clicked = False
                for selector in transfer_selectors:
                    try:
                        transfer_block = page.locator(selector).first
                        if await transfer_block.is_visible(timeout=300):
                            await transfer_block.click()
                            print("   ✅ Открыл способ платежа")
                            transfer_clicked = True
                            break
                    except:
                        continue
                
                if not transfer_clicked:
                    raise Exception("Не удалось открыть способ платежа")
                
                await page.wait_for_timeout(300)
                
                # Выбор Uzcard - надежный метод
                bank_selectors = [
                    'text=Uzcard',
                    '[role="button"]:has-text("Uzcard")',
                ]
                
                bank_selected = False
                for selector in bank_selectors:
                    try:
                        bank_option = page.locator(selector).first
                        await bank_option.wait_for(state='visible', timeout=2000)
                        await bank_option.click()
                        print("   ✅ Uzcard выбран")
                        bank_selected = True
                        break
                    except:
                        continue
                
                if not bank_selected:
                    raise Exception("Не удалось выбрать Uzcard")
                
                # Ждем активации кнопки
                await page.wait_for_timeout(500)  # Уменьшаем с 1000 до 500
                
                # Проверяем что кнопка стала активной
                print("   ⏳ Жду активации кнопки...")
                try:
                    await page.wait_for_function("""
                        () => {
                            const btn = document.getElementById('pay');
                            return btn && !btn.disabled;
                        }
                    """, timeout=10000)
                    print("   ✅ Кнопка активна")
                except:
                    # Если кнопка не активна, пробуем еще раз выбрать банк
                    print("   ⚠️ Кнопка не активна, пробую еще раз...")
                    await page.evaluate("""
                        () => {
                            const uzcardBtn = Array.from(document.querySelectorAll('[role="button"]')).find(
                                el => el.textContent.includes('Uzcard')
                            );
                            if (uzcardBtn) uzcardBtn.click();
                        }
                    """)
                    await page.wait_for_timeout(1000)
                    await page.wait_for_function("""
                        () => {
                            const btn = document.getElementById('pay');
                            return btn && !btn.disabled;
                        }
                    """, timeout=10000)
                    print("   ✅ Кнопка активна (после повтора)")
                
                await page.locator('#pay').evaluate('el => el.click()')
                await page.wait_for_url('**/sender-details**', timeout=10000)
                print("   ✅ Переход")
                
                success = True
                
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ Ошибка: {e}")
            
            finally:
                elapsed = time.time() - start_time
                results.append({
                    'run': run + 1,
                    'success': success,
                    'time': elapsed,
                    'error': error_msg
                })
                
                await browser.close()
                
                # Пауза между запусками
                if run < runs - 1:
                    print(f"\n⏳ Пауза 2 секунды...")
                    await asyncio.sleep(2)
    
    # Статистика
    print(f"\n{'='*70}")
    print(f"ИТОГОВАЯ СТАТИСТИКА ({runs} запусков)")
    print(f"{'='*70}")
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n✅ Успешных: {len(successful)}/{runs} ({len(successful)/runs*100:.1f}%)")
    print(f"❌ Неудачных: {len(failed)}/{runs} ({len(failed)/runs*100:.1f}%)")
    
    if successful:
        avg_time = sum(r['time'] for r in successful) / len(successful)
        min_time = min(r['time'] for r in successful)
        max_time = max(r['time'] for r in successful)
        print(f"\n⏱️  Время успешных:")
        print(f"   Среднее: {avg_time:.2f}s")
        print(f"   Минимум: {min_time:.2f}s")
        print(f"   Максимум: {max_time:.2f}s")
    
    if failed:
        print(f"\n❌ Ошибки:")
        for r in failed:
            print(f"   Запуск #{r['run']}: {r['error'][:100]}")
    
    print(f"\n{'='*70}")


if __name__ == "__main__":
    asyncio.run(test_step1_multiple_times(runs=5))
