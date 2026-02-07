#!/usr/bin/env python3
"""
ЭТАП 3: Обработка модалки "Проверка данных" и капчи
"""

from playwright.async_api import Page
import time


async def process_step3(page: Page, log_func) -> dict:
    """
    Этап 3: Обработка модалки подтверждения и капчи
    
    Args:
        page: Playwright page объект
        log_func: Функция для логирования
    
    Returns:
        dict: {'success': bool, 'time': float, 'error': str or None}
    """
    log = log_func
    start_time = time.time()
    
    try:
        log("=" * 50, "INFO")
        log("ЭТАП 3: МОДАЛКА И КАПЧА", "INFO")
        log("=" * 50, "INFO")
        
        # Капча (если есть)
        log("Проверяю наличие капчи...", "DEBUG")
        try:
            captcha_iframe_selector = 'iframe[src*="smartcaptcha.yandexcloud.net/checkbox"]'
            await page.wait_for_selector(captcha_iframe_selector, state='visible', timeout=3000)
            
            log("Капча обнаружена, решаю...", "DEBUG")
            await page.wait_for_timeout(300)
            
            captcha_frame = page.frame_locator(captcha_iframe_selector)
            checkbox_button = captcha_frame.locator('#js-button')
            
            await checkbox_button.wait_for(state='visible', timeout=3000)
            
            # Пробуем разные способы клика
            captcha_clicked = False
            for attempt in range(3):
                try:
                    await checkbox_button.click(timeout=2000)
                    log(f"Капча решена (попытка {attempt + 1})", "SUCCESS")
                    captcha_clicked = True
                    break
                except:
                    try:
                        await checkbox_button.click(force=True, timeout=2000)
                        log(f"Капча решена force (попытка {attempt + 1})", "SUCCESS")
                        captcha_clicked = True
                        break
                    except:
                        pass
            
            if captcha_clicked:
                await page.wait_for_timeout(800)
            else:
                log("⚠️ Не удалось решить капчу", "WARNING")
                    
        except Exception as e:
            log(f"Капча не обнаружена: {e}", "DEBUG")
        
        # Модалка "Проверка данных"
        log("Проверяю модалку проверки данных...", "DEBUG")
        try:
            modal_info = await page.evaluate("""
                () => {
                    const headers = document.querySelectorAll('h4');
                    for (const h of headers) {
                        if (h.textContent.includes('Проверка данных')) {
                            const parent = h.closest('div');
                            const paragraphs = parent ? parent.querySelectorAll('p') : [];
                            let text = '';
                            paragraphs.forEach(p => { text += p.textContent + ' '; });
                            return { found: true, text: text.trim() };
                        }
                    }
                    return { found: false, text: '' };
                }
            """)
            
            if modal_info['found']:
                log(f"📋 Модалка 'Проверка данных': {modal_info['text'][:100]}", "INFO")
                
                # Проверяем текст модалки
                if 'Ошибка' in modal_info['text'] or 'ошибка' in modal_info['text']:
                    log("⚠️ ОШИБКА: Реквизиты получателя устарели!", "WARNING")
                    
                    # Закрываем модалку
                    buttons = await page.locator('button[buttontext="Продолжить"]').all()
                    if len(buttons) > 0:
                        await buttons[-1].click()
                        log("Модалка закрыта", "SUCCESS")
                        await page.wait_for_timeout(300)
                    
                    elapsed_time = time.time() - start_time
                    return {
                        'success': False,
                        'time': elapsed_time,
                        'error': 'Реквизиты получателя больше не актуальны'
                    }
                else:
                    # Подтверждение данных - нажимаем "Продолжить"
                    log("✅ Модалка подтверждения - нажимаю 'Продолжить'", "SUCCESS")
                    
                    try:
                        button = page.locator('button:has-text("Продолжить")').last
                        await button.wait_for(state='visible', timeout=3000)
                        
                        # Пробуем разные способы клика
                        clicked = False
                        for method in ['click', 'force', 'js', 'dispatch']:
                            if clicked:
                                break
                            try:
                                if method == 'click':
                                    await button.click(timeout=2000)
                                elif method == 'force':
                                    await button.click(force=True, timeout=2000)
                                elif method == 'js':
                                    await button.evaluate('el => el.click()')
                                elif method == 'dispatch':
                                    await button.evaluate("""
                                        el => el.dispatchEvent(new MouseEvent('click', {
                                            view: window, bubbles: true, cancelable: true
                                        }))
                                    """)
                                log(f"Кнопка нажата ({method})", "DEBUG")
                                clicked = True
                            except:
                                pass
                        
                        if clicked:
                            log("✅ Модалка закрыта", "SUCCESS")
                            await page.wait_for_timeout(2000)
                        else:
                            log("⚠️ Не удалось нажать кнопку", "WARNING")
                            
                    except Exception as e:
                        log(f"⚠️ Ошибка при нажатии кнопки: {e}", "WARNING")
            else:
                log("Модалка проверки данных не обнаружена", "DEBUG")
                
        except Exception as e:
            log(f"Ошибка при проверке модалки: {e}", "DEBUG")
        
        elapsed_time = time.time() - start_time
        log(f"⏱️ Этап 3 занял: {elapsed_time:.2f}s", "INFO")
        
        return {
            'success': True,
            'time': elapsed_time,
            'error': None
        }
        
    except Exception as e:
        log(f"Ошибка на этапе 3: {e}", "ERROR")
        return {
            'success': False,
            'time': time.time() - start_time,
            'error': str(e)
        }
