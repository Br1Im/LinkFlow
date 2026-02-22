#!/usr/bin/env python3
"""
ЭТАП 1: Ввод суммы и выбор способа оплаты
"""

from playwright.async_api import Page
import time


async def process_step1(page: Page, amount: int, log_func) -> dict:
    """
    Этап 1: Ввод суммы, выбор Uzcard, активация кнопки Продолжить
    
    Args:
        page: Playwright page объект
        amount: Сумма платежа
        log_func: Функция для логирования
    
    Returns:
        dict: {'success': bool, 'time': float, 'error': str or None}
    """
    log = log_func
    start_time = time.time()
    
    try:
        log("=" * 50, "INFO")
        log("ЭТАП 1: ВВОД СУММЫ", "INFO")
        log("=" * 50, "INFO")
        
        amount_input = page.locator('input[placeholder="0 RUB"]')
        await amount_input.wait_for(state='visible', timeout=5000)
        
        # Очищаем старую сумму
        log("Очищаю старую сумму...", "DEBUG")
        await amount_input.click()
        await amount_input.evaluate("el => el.value = ''")
        await amount_input.click()
        await page.keyboard.press('Control+A')
        await page.keyboard.press('Delete')
        
        log(f"Ввожу новую сумму: {amount} RUB", "DEBUG")
        
        # Ввод суммы с retry
        commission_ok = False
        for attempt in range(10):
            if attempt > 0:
                log(f"Попытка #{attempt + 1} ввода суммы", "WARNING")
            
            # Закрываем модалку если есть
            try:
                modal_closed = await page.evaluate("""
                    () => {
                        const buttons = document.querySelectorAll('button[buttontext="Понятно"]');
                        let closed = false;
                        buttons.forEach(btn => {
                            if (btn.textContent.includes('Понятно')) {
                                btn.click();
                                closed = true;
                            }
                        });
                        return closed;
                    }
                """)
                if modal_closed:
                    log("Модалка закрыта, повторяю ввод", "WARNING")
                    await page.wait_for_timeout(500)
                    await amount_input.click()
                    await amount_input.evaluate("el => el.value = ''")
                    await page.wait_for_timeout(100)
            except:
                pass
            
            # Вводим сумму
            await amount_input.evaluate(f"""
                (element) => {{
                    element.focus();
                    element.click();
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 
                        'value'
                    ).set;
                    nativeInputValueSetter.call(element, '{amount}');
                    element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    element.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', bubbles: true }}));
                    element.dispatchEvent(new KeyboardEvent('keyup', {{ key: 'Enter', bubbles: true }}));
                }}
            """)
            
            # Проверяем комиссию
            try:
                await page.wait_for_function("""
                    () => {
                        const input = document.querySelector('input[placeholder*="UZS"]');
                        return input && input.value && input.value !== '0 UZS' && input.value !== '';
                    }
                """, timeout=1000)
                log("Комиссия рассчитана успешно", "SUCCESS")
                commission_ok = True
                break
            except:
                pass
        
        if not commission_ok:
            log("Не удалось рассчитать комиссию за 10 попыток", "ERROR")
            return {
                'success': False,
                'time': time.time() - start_time,
                'error': 'Не удалось рассчитать комиссию'
            }
        
        # Выбор способа платежа и Uzcard
        log("Выбираю способ перевода и Uzcard...", "DEBUG")
        
        # Клик по "Способ перевода"
        transfer_selectors = [
            'div.css-c8d8yl:has-text("Способ перевода")',
            'div:has-text("Способ перевода")',
        ]
        
        for selector in transfer_selectors:
            try:
                transfer_block = page.locator(selector).first
                if await transfer_block.is_visible(timeout=200):
                    await transfer_block.click()
                    log("Способ перевода выбран", "DEBUG")
                    break
            except:
                continue
        
        await page.wait_for_timeout(150)
        
        # Выбор Uzcard с retry
        uzcard_selected = False
        for uzcard_attempt in range(5):
            try:
                bank_selectors = [
                    'text=Uzcard',
                    '[role="button"]:has-text("Uzcard")',
                ]
                
                for selector in bank_selectors:
                    try:
                        bank_option = page.locator(selector).first
                        if await bank_option.is_visible(timeout=500):
                            await bank_option.click()
                            log(f"Uzcard выбран (попытка #{uzcard_attempt + 1})", "DEBUG")
                            uzcard_selected = True
                            break
                    except:
                        continue
                
                if uzcard_selected:
                    break
                
                # Если не нашли, пробуем через JS
                if uzcard_attempt > 1:
                    await page.evaluate("""
                        () => {
                            const uzcardBtn = Array.from(document.querySelectorAll('[role="button"]')).find(
                                el => el.textContent.includes('Uzcard')
                            );
                            if (uzcardBtn) {
                                uzcardBtn.click();
                                return true;
                            }
                            return false;
                        }
                    """)
                    uzcard_selected = True
                    log(f"Uzcard выбран через JS (попытка #{uzcard_attempt + 1})", "DEBUG")
                    break
                
                await page.wait_for_timeout(150)
                
            except Exception as e:
                log(f"Попытка #{uzcard_attempt + 1} выбора Uzcard не удалась: {e}", "WARNING")
                await page.wait_for_timeout(150)
        
        if not uzcard_selected:
            log("Не удалось выбрать Uzcard", "ERROR")
            return {
                'success': False,
                'time': time.time() - start_time,
                'error': 'Не удалось выбрать Uzcard'
            }
        
        await page.wait_for_timeout(150)
        
        # Ждем активации кнопки "Продолжить"
        log("Жду активации кнопки Продолжить...", "DEBUG")
        button_active = False
        
        for btn_attempt in range(15):
            try:
                is_active = await page.evaluate("""
                    () => {
                        const btn = document.getElementById('pay');
                        return btn && !btn.disabled;
                    }
                """)
                
                if is_active:
                    log(f"Кнопка активна (попытка #{btn_attempt + 1})", "SUCCESS")
                    button_active = True
                    break
                
                # Повторный ввод суммы на 3 попытке
                if btn_attempt == 3:
                    log("Кнопка не активна, ввожу сумму заново...", "WARNING")
                    await amount_input.click()
                    await page.wait_for_timeout(100)
                    await amount_input.evaluate("el => el.value = ''")
                    await page.wait_for_timeout(100)
                    
                    await amount_input.evaluate(f"""
                        (element) => {{
                            element.focus();
                            element.click();
                            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                                window.HTMLInputElement.prototype, 
                                'value'
                            ).set;
                            nativeInputValueSetter.call(element, '{amount}');
                            element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            element.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', bubbles: true }}));
                            element.dispatchEvent(new KeyboardEvent('keyup', {{ key: 'Enter', bubbles: true }}));
                        }}
                    """)
                    
                    await page.wait_for_timeout(400)
                    
                    # Повторно выбираем Uzcard
                    await page.evaluate("""
                        () => {
                            const uzcardBtn = Array.from(document.querySelectorAll('[role="button"]')).find(
                                el => el.textContent.includes('Uzcard')
                            );
                            if (uzcardBtn) uzcardBtn.click();
                        }
                    """)
                    await page.wait_for_timeout(250)
                
                # Повторный клик по "Способ перевода" на 7 попытке
                if btn_attempt == 7:
                    log("Повторный клик по 'Способ перевода'...", "WARNING")
                    try:
                        transfer_block = page.locator('div:has-text("Способ перевода")').first
                        if await transfer_block.is_visible(timeout=500):
                            await transfer_block.click()
                            await page.wait_for_timeout(150)
                    except:
                        pass
                    
                    await page.evaluate("""
                        () => {
                            const uzcardBtn = Array.from(document.querySelectorAll('[role="button"]')).find(
                                el => el.textContent.includes('Uzcard')
                            );
                            if (uzcardBtn) uzcardBtn.click();
                        }
                    """)
                    await page.wait_for_timeout(250)
                
                # Периодический клик по Uzcard
                if btn_attempt > 4 and btn_attempt % 2 == 0:
                    await page.evaluate("""
                        () => {
                            const uzcardBtn = Array.from(document.querySelectorAll('[role="button"]')).find(
                                el => el.textContent.includes('Uzcard')
                            );
                            if (uzcardBtn) uzcardBtn.click();
                        }
                    """)
                    log(f"Повторный клик по Uzcard (попытка #{btn_attempt + 1})", "WARNING")
                
                await page.wait_for_timeout(250)
                
            except Exception as e:
                log(f"Ошибка проверки кнопки: {e}", "WARNING")
                await page.wait_for_timeout(250)
        
        if not button_active:
            log("Кнопка Продолжить не активировалась", "ERROR")
            return {
                'success': False,
                'time': time.time() - start_time,
                'error': 'Кнопка Продолжить не активировалась'
            }
        
        # Клик по кнопке
        log("Нажимаю кнопку Продолжить...", "DEBUG")
        
        # Проверяем и закрываем модалки перед кликом
        try:
            modal_closed = await page.evaluate("""
                () => {
                    const buttons = document.querySelectorAll('button[buttontext="Понятно"]');
                    let closed = false;
                    buttons.forEach(btn => {
                        if (btn.textContent.includes('Понятно')) {
                            btn.click();
                            closed = true;
                        }
                    });
                    return closed;
                }
            """)
            if modal_closed:
                log("Модалка закрыта перед кликом", "WARNING")
                await page.wait_for_timeout(300)
        except:
            pass
        
        # Пробуем разные способы клика
        click_success = False
        for method in ['evaluate', 'click', 'force']:
            try:
                if method == 'evaluate':
                    await page.locator('#pay').evaluate('el => el.click()')
                elif method == 'click':
                    await page.locator('#pay').click(timeout=2000)
                elif method == 'force':
                    await page.locator('#pay').click(force=True, timeout=2000)
                
                log(f"Кнопка Продолжить нажата ({method})", "SUCCESS")
                click_success = True
                break
            except Exception as e:
                log(f"Метод {method} не сработал: {e}", "WARNING")
                await page.wait_for_timeout(200)
        
        if not click_success:
            log("Не удалось нажать кнопку Продолжить", "ERROR")
            return {
                'success': False,
                'time': time.time() - start_time,
                'error': 'Не удалось нажать кнопку Продолжить'
            }
        
        # Ждём навигацию с увеличенным таймаутом и обработкой ошибок
        try:
            await page.wait_for_url('**/sender-details**', timeout=15000)
            log("Переход на страницу заполнения данных", "SUCCESS")
        except Exception as e:
            # Проверяем текущий URL
            current_url = page.url
            log(f"Таймаут навигации. Текущий URL: {current_url}", "WARNING")
            
            # Если уже на нужной странице - это успех
            if 'sender-details' in current_url:
                log("Уже на странице sender-details", "SUCCESS")
            else:
                # Проверяем наличие модалок
                modal_info = await page.evaluate("""
                    () => {
                        const modals = document.querySelectorAll('[role="dialog"], .modal, [class*="modal"]');
                        if (modals.length > 0) {
                            return {
                                found: true,
                                count: modals.length,
                                text: Array.from(modals).map(m => m.textContent.substring(0, 100)).join(' | ')
                            };
                        }
                        return { found: false };
                    }
                """)
                
                if modal_info.get('found'):
                    log(f"Обнаружена модалка: {modal_info.get('text', '')[:200]}", "ERROR")
                    return {
                        'success': False,
                        'time': time.time() - start_time,
                        'error': f'Модалка блокирует навигацию: {modal_info.get("text", "")[:100]}'
                    }
                else:
                    log(f"Навигация не произошла. URL: {current_url}", "ERROR")
                    return {
                        'success': False,
                        'time': time.time() - start_time,
                        'error': f'Timeout навигации. URL: {current_url}'
                    }
        
        elapsed_time = time.time() - start_time
        log(f"⏱️ Этап 1 занял: {elapsed_time:.2f}s", "INFO")
        
        return {
            'success': True,
            'time': elapsed_time,
            'error': None
        }
        
    except Exception as e:
        log(f"Ошибка на этапе 1: {e}", "ERROR")
        return {
            'success': False,
            'time': time.time() - start_time,
            'error': str(e)
        }
