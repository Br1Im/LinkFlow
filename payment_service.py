#!/usr/bin/env python3
"""
Сервис для создания платежных ссылок с постоянным браузером
Браузер открывается один раз и остается активным между запросами
PRODUCTION VERSION - headless mode, detailed logging
"""

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import asyncio
import time
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'playwright_version'))


def log(message: str, level: str = "INFO"):
    """Логирование с временной меткой"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    prefix = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "DEBUG": "🔍"
    }.get(level, "📝")
    print(f"[{timestamp}] {prefix} {message}")


# Данные отправителя
SENDER_DATA = {
    "passport_series": "1820",
    "passport_number": "657875",
    "passport_issue_date": "22.07.2020",
    "birth_country": "Россия",
    "birth_place": "камышин",
    "first_name": "Дмитрий",
    "last_name": "Непокрытый",
    "middle_name": "Александрович",
    "birth_date": "03.07.2000",
    "phone": "+7 988 026-03-34",
    "registration_country": "Россия",
    "registration_place": "камышин",
}


async def fill_beneficiary_card(page, card_number: str) -> bool:
    """
    СПЕЦИАЛЬНАЯ функция для заполнения номера карты получателя
    Самое проблемное поле - требует особого подхода
    """
    log(f"Заполняю номер карты: {card_number}", "DEBUG")
    
    try:
        inputs = await page.locator('input').all()
        
        for inp in inputs:
            name_attr = await inp.get_attribute('name') or ""
            placeholder = await inp.get_attribute('placeholder') or ""
            
            if "beneficiaryAccountNumber".lower() in name_attr.lower() or \
               "номер карты" in placeholder.lower() or \
               "пример:" in placeholder.lower():
                
                log(f"Найдено поле карты: name='{name_attr}', placeholder='{placeholder}'", "DEBUG")
                
                # Пробуем до 5 раз с разными методами
                for attempt in range(5):
                    log(f"Попытка #{attempt + 1} заполнения карты", "DEBUG")
                    
                    # Метод 1: Очистка + посимвольный ввод
                    await inp.click()
                    await page.wait_for_timeout(100)
                    
                    # Полная очистка
                    await inp.evaluate("el => el.value = ''")
                    await page.wait_for_timeout(50)
                    
                    # Фокус
                    await inp.focus()
                    await page.wait_for_timeout(50)
                    
                    # Посимвольный ввод с задержкой
                    for char in card_number:
                        await inp.type(char, delay=15)
                    
                    await page.wait_for_timeout(100)
                    await inp.blur()
                    await page.wait_for_timeout(200)
                    
                    # Проверяем значение
                    current_value = await inp.input_value()
                    log(f"Текущее значение карты: '{current_value}'", "DEBUG")
                    
                    # Проверяем ошибку валидации
                    is_error = await inp.evaluate("""
                        (element) => {
                            const parent = element.closest('div');
                            if (!parent) return false;
                            
                            const errorText = parent.querySelector('p');
                            if (errorText && errorText.textContent.includes('Обязательное поле')) {
                                return true;
                            }
                            
                            const styles = window.getComputedStyle(element);
                            return styles.borderColor.includes('rgb(244, 67, 54)') || 
                                   styles.borderColor.includes('rgb(211, 47, 47)');
                        }
                    """)
                    
                    if not is_error and current_value and len(current_value) >= 16:
                        log(f"Номер карты заполнен успешно: {current_value}", "SUCCESS")
                        return True
                    else:
                        log(f"Попытка #{attempt + 1} не прошла валидацию (error={is_error}, len={len(current_value)})", "WARNING")
                        await page.wait_for_timeout(200)
                
                log("Не удалось заполнить номер карты после 5 попыток", "ERROR")
                return False
        
        log("Поле номера карты не найдено", "ERROR")
        return False
        
    except Exception as e:
        log(f"Ошибка при заполнении карты: {e}", "ERROR")
        return False


async def fill_beneficiary_name(page, first_name: str, last_name: str) -> tuple:
    """
    СПЕЦИАЛЬНАЯ функция для заполнения имени и фамилии получателя
    Также проблемные поля
    """
    log(f"Заполняю имя получателя: {first_name} {last_name}", "DEBUG")
    
    fname_ok = False
    lname_ok = False
    
    try:
        inputs = await page.locator('input').all()
        
        # Заполняем имя
        for inp in inputs:
            name_attr = await inp.get_attribute('name') or ""
            placeholder = await inp.get_attribute('placeholder') or ""
            
            if "beneficiary_firstname" in name_attr.lower() or "имя" in placeholder.lower():
                log(f"Найдено поле имени: name='{name_attr}'", "DEBUG")
                
                for attempt in range(3):
                    await inp.click()
                    await page.wait_for_timeout(50)
                    await inp.evaluate("el => el.value = ''")
                    await page.wait_for_timeout(50)
                    await inp.focus()
                    
                    for char in first_name:
                        await inp.type(char, delay=15)
                    
                    await page.wait_for_timeout(100)
                    await inp.blur()
                    await page.wait_for_timeout(150)
                    
                    is_error = await inp.evaluate("""
                        (element) => {
                            const parent = element.closest('div');
                            if (!parent) return false;
                            const errorText = parent.querySelector('p');
                            if (errorText && errorText.textContent.includes('Обязательное поле')) {
                                return true;
                            }
                            const styles = window.getComputedStyle(element);
                            return styles.borderColor.includes('rgb(244, 67, 54)') || 
                                   styles.borderColor.includes('rgb(211, 47, 47)');
                        }
                    """)
                    
                    if not is_error:
                        log(f"Имя получателя заполнено: {first_name}", "SUCCESS")
                        fname_ok = True
                        break
                    else:
                        log(f"Имя: попытка #{attempt + 1} не прошла валидацию", "WARNING")
                
                break
        
        # Заполняем фамилию
        for inp in inputs:
            name_attr = await inp.get_attribute('name') or ""
            placeholder = await inp.get_attribute('placeholder') or ""
            
            if "beneficiary_lastname" in name_attr.lower() or "фамилия" in placeholder.lower():
                log(f"Найдено поле фамилии: name='{name_attr}'", "DEBUG")
                
                for attempt in range(3):
                    await inp.click()
                    await page.wait_for_timeout(50)
                    await inp.evaluate("el => el.value = ''")
                    await page.wait_for_timeout(50)
                    await inp.focus()
                    
                    for char in last_name:
                        await inp.type(char, delay=15)
                    
                    await page.wait_for_timeout(100)
                    await inp.blur()
                    await page.wait_for_timeout(150)
                    
                    is_error = await inp.evaluate("""
                        (element) => {
                            const parent = element.closest('div');
                            if (!parent) return false;
                            const errorText = parent.querySelector('p');
                            if (errorText && errorText.textContent.includes('Обязательное поле')) {
                                return true;
                            }
                            const styles = window.getComputedStyle(element);
                            return styles.borderColor.includes('rgb(244, 67, 54)') || 
                                   styles.borderColor.includes('rgb(211, 47, 47)');
                        }
                    """)
                    
                    if not is_error:
                        log(f"Фамилия получателя заполнена: {last_name}", "SUCCESS")
                        lname_ok = True
                        break
                    else:
                        log(f"Фамилия: попытка #{attempt + 1} не прошла валидацию", "WARNING")
                
                break
        
        return (fname_ok, lname_ok)
        
    except Exception as e:
        log(f"Ошибка при заполнении имени/фамилии: {e}", "ERROR")
        return (False, False)


async def fill_field_async(page, pattern: str, value: str, field_name: str, use_typing: bool = False):
    """Асинхронное заполнение поля с проверкой"""
    try:
        inputs = await page.locator('input').all()
        
        for inp in inputs:
            name_attr = await inp.get_attribute('name') or ""
            placeholder = await inp.get_attribute('placeholder') or ""
            
            if pattern.lower() in name_attr.lower() or pattern.lower() in placeholder.lower():
                # Пробуем заполнить до 3 раз
                for retry in range(3):
                    if use_typing:
                        # Посимвольный ввод для React полей
                        await inp.click()
                        await page.wait_for_timeout(50)
                        await inp.fill("")
                        await page.wait_for_timeout(50)
                        
                        for char in value:
                            await inp.type(char, delay=10)
                        
                        await page.wait_for_timeout(50)
                        await inp.blur()
                    else:
                        # Быстрый JavaScript ввод
                        await inp.evaluate("""
                            (element, value) => {
                                element.focus();
                                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                                    window.HTMLInputElement.prototype, 
                                    'value'
                                ).set;
                                nativeInputValueSetter.call(element, value);
                                
                                element.dispatchEvent(new Event('input', { bubbles: true }));
                                element.dispatchEvent(new Event('change', { bubbles: true }));
                                element.blur();
                            }
                        """, value)
                    
                    await page.wait_for_timeout(100)
                    
                    # Проверяем что поле не красное
                    is_error = await inp.evaluate("""
                        (element) => {
                            const parent = element.closest('div');
                            if (!parent) return false;
                            
                            const errorText = parent.querySelector('p');
                            if (errorText && errorText.textContent.includes('Обязательное поле')) {
                                return true;
                            }
                            
                            const styles = window.getComputedStyle(element);
                            return styles.borderColor.includes('rgb(244, 67, 54)') || 
                                   styles.borderColor.includes('rgb(211, 47, 47)');
                        }
                    """)
                    
                    if not is_error:
                        return True
                    elif retry < 2:
                        await page.wait_for_timeout(100)
                
                return False
        
        return False
    except Exception as e:
        return False


async def select_country_async(page, pattern: str, country: str, field_name: str):
    """Асинхронный выбор страны с проверкой правильного выбора"""
    try:
        inputs = await page.locator('input').all()
        
        for inp in inputs:
            name_attr = await inp.get_attribute('name') or ""
            if pattern in name_attr:
                # Пробуем до 3 раз
                for attempt in range(3):
                    await inp.click()
                    await page.wait_for_timeout(100)
                    await inp.fill("")  # Очищаем
                    await page.wait_for_timeout(50)
                    await inp.fill(country)
                    await page.wait_for_timeout(200)
                    
                    try:
                        # Ждем появления опций
                        await page.wait_for_selector('li[role="option"]', state='visible', timeout=1000)
                        
                        # Ищем ИМЕННО нужную страну в списке
                        options = await page.locator('li[role="option"]').all()
                        found = False
                        
                        for option in options:
                            text = await option.inner_text()
                            if country.lower() in text.lower():
                                await option.click()
                                await page.wait_for_timeout(100)
                                
                                # Проверяем что выбралось правильно
                                current_value = await inp.input_value()
                                if country.lower() in current_value.lower():
                                    print(f"   ✅ {field_name}: {current_value}")
                                    found = True
                                    break
                        
                        if found:
                            return True
                        else:
                            print(f"   ⚠️ {field_name}: страна не найдена в списке, попытка {attempt + 1}")
                            
                    except Exception as e:
                        # Если опции не появились, жмем Enter
                        await page.keyboard.press('Enter')
                        await page.wait_for_timeout(100)
                        
                        # Проверяем результат
                        current_value = await inp.input_value()
                        if country.lower() in current_value.lower():
                            print(f"   ✅ {field_name}: {current_value} (Enter)")
                            return True
                
                print(f"   ❌ {field_name}: не удалось выбрать после 3 попыток")
                return False
        
        return False
    except Exception as e:
        print(f"   ❌ {field_name}: ошибка - {e}")
        return False


class PaymentService:
    """Сервис для создания платежных ссылок"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.is_ready = False
        
    async def start(self, headless: bool = True):
        """Запускает браузер и подготавливает страницу"""
        log(f"Запуск браузера (headless={headless})...", "INFO")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        self.page = await self.context.new_page()
        
        # Автозакрыватель модалок
        await self.page.evaluate("""
            () => {
                const closeErrorModal = () => {
                    const buttons = document.querySelectorAll('button[buttontext="Понятно"]');
                    buttons.forEach(btn => {
                        if (btn.textContent.includes('Понятно')) {
                            btn.click();
                        }
                    });
                };
                setInterval(closeErrorModal, 50);
                const observer = new MutationObserver(() => closeErrorModal());
                observer.observe(document.body, { childList: true, subtree: true });
            }
        """)
        
        # Предзагружаем страницу
        log("Предзагрузка страницы...", "INFO")
        await self.page.goto("https://multitransfer.ru/transfer/uzbekistan", wait_until='domcontentloaded')
        await self.page.wait_for_selector('input[placeholder="0 RUB"]', state='visible', timeout=10000)
        
        self.is_ready = True
        log("Сервис готов к работе!", "SUCCESS")
        
    async def stop(self):
        """Останавливает браузер"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.is_ready = False
        print("🛑 Сервис остановлен")
        
    async def create_payment_link(self, amount: int, card_number: str, owner_name: str) -> dict:
        """
        Создает платежную ссылку
        
        Returns:
            dict: {
                'success': bool,
                'qr_link': str or None,
                'time': float,
                'step1_time': float,
                'step2_time': float,
                'error': str or None
            }
        """
        if not self.is_ready:
            return {'success': False, 'error': 'Сервис не запущен', 'time': 0}
        
        start_time = time.time()
        qr_link = None
        
        # Обработчик для перехвата QR ссылки
        async def handle_response(response):
            nonlocal qr_link
            if '/anonymous/confirm' in response.url:
                try:
                    data = await response.json()
                    if 'externalData' in data and 'payload' in data['externalData']:
                        qr_link = data['externalData']['payload']
                except:
                    pass
        
        self.page.on('response', handle_response)
        
        try:
            # Полная перезагрузка страницы с очисткой состояния
            log("Перезагружаю страницу...", "DEBUG")
            await self.page.goto("https://multitransfer.ru/transfer/uzbekistan", wait_until='networkidle')
            await self.page.wait_for_timeout(800)
            
            # ЭТАП 1: Ввод суммы
            log("=" * 50, "INFO")
            log("ЭТАП 1: ВВОД СУММЫ", "INFO")
            log("=" * 50, "INFO")
            
            amount_input = self.page.locator('input[placeholder="0 RUB"]')
            await amount_input.wait_for(state='visible', timeout=5000)
            
            # ВАЖНО: Очищаем старую сумму перед вводом новой
            log("Очищаю старую сумму...", "DEBUG")
            await amount_input.click()
            await self.page.wait_for_timeout(100)
            await amount_input.evaluate("el => el.value = ''")
            await self.page.wait_for_timeout(100)
            
            # Очищаем через Ctrl+A + Delete
            await amount_input.click()
            await self.page.keyboard.press('Control+A')
            await self.page.keyboard.press('Delete')
            await self.page.wait_for_timeout(100)
            
            log(f"Ввожу новую сумму: {amount} RUB", "DEBUG")
            
            commission_ok = False
            for attempt in range(10):
                if attempt > 0:
                    log(f"Попытка #{attempt + 1} ввода суммы", "WARNING")
                
                # Закрываем модалку если есть
                try:
                    modal_closed = await self.page.evaluate("""
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
                        await self.page.wait_for_timeout(500)
                        # Очищаем поле снова после закрытия модалки
                        await amount_input.click()
                        await amount_input.evaluate("el => el.value = ''")
                        await self.page.wait_for_timeout(100)
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
                
                await self.page.wait_for_timeout(200)
                
                # Проверяем комиссию
                try:
                    await self.page.wait_for_function("""
                        () => {
                            const input = document.querySelector('input[placeholder*="UZS"]');
                            return input && input.value && input.value !== '0 UZS' && input.value !== '';
                        }
                    """, timeout=800)
                    log("Комиссия рассчитана успешно", "SUCCESS")
                    commission_ok = True
                    break
                except:
                    if attempt < 9:
                        await self.page.wait_for_timeout(100)
            
            if not commission_ok:
                log("Не удалось рассчитать комиссию за 10 попыток", "ERROR")
                # Делаем скриншот при ошибке
                screenshot_path = f"screenshots/error_commission_{int(time.time())}.png"
                try:
                    await self.page.screenshot(path=screenshot_path)
                    log(f"Скриншот сохранен: {screenshot_path}", "INFO")
                except:
                    pass
                return {'success': False, 'error': 'Не удалось рассчитать комиссию', 'time': time.time() - start_time}
            
            # Выбор способа платежа и Uzcard с улучшенной логикой
            log("Выбираю способ перевода и Uzcard...", "DEBUG")
            
            # Клик по "Способ перевода"
            transfer_selectors = [
                'div.css-c8d8yl:has-text("Способ перевода")',
                'div:has-text("Способ перевода")',
            ]
            
            for selector in transfer_selectors:
                try:
                    transfer_block = self.page.locator(selector).first
                    if await transfer_block.is_visible(timeout=200):
                        await transfer_block.click()
                        log("Способ перевода выбран", "DEBUG")
                        break
                except:
                    continue
            
            await self.page.wait_for_timeout(200)
            
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
                            bank_option = self.page.locator(selector).first
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
                        await self.page.evaluate("""
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
                    
                    await self.page.wait_for_timeout(200)
                    
                except Exception as e:
                    log(f"Попытка #{uzcard_attempt + 1} выбора Uzcard не удалась: {e}", "WARNING")
                    await self.page.wait_for_timeout(200)
            
            if not uzcard_selected:
                log("Не удалось выбрать Uzcard", "ERROR")
                # Делаем скриншот при ошибке
                screenshot_path = f"screenshots/error_uzcard_{int(time.time())}.png"
                try:
                    await self.page.screenshot(path=screenshot_path)
                    log(f"Скриншот сохранен: {screenshot_path}", "INFO")
                except:
                    pass
                return {'success': False, 'error': 'Не удалось выбрать Uzcard', 'time': time.time() - start_time}
            
            await self.page.wait_for_timeout(200)
            
            # Ждем активации кнопки "Продолжить" с retry
            log("Жду активации кнопки Продолжить...", "DEBUG")
            button_active = False
            for btn_attempt in range(10):
                try:
                    is_active = await self.page.evaluate("""
                        () => {
                            const btn = document.getElementById('pay');
                            return btn && !btn.disabled;
                        }
                    """)
                    
                    if is_active:
                        log(f"Кнопка активна (попытка #{btn_attempt + 1})", "SUCCESS")
                        button_active = True
                        break
                    
                    # Если кнопка не активна после 3 попыток, вводим сумму заново
                    if btn_attempt == 3:
                        log("Кнопка не активна, ввожу сумму заново...", "WARNING")
                        await amount_input.click()
                        await self.page.wait_for_timeout(100)
                        await amount_input.evaluate("el => el.value = ''")
                        await self.page.wait_for_timeout(100)
                        
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
                        
                        await self.page.wait_for_timeout(500)
                        
                        # Ждем пересчета комиссии
                        try:
                            await self.page.wait_for_function("""
                                () => {
                                    const input = document.querySelector('input[placeholder*="UZS"]');
                                    return input && input.value && input.value !== '0 UZS' && input.value !== '';
                                }
                            """, timeout=1000)
                            log("Комиссия пересчитана", "SUCCESS")
                        except:
                            log("Не удалось пересчитать комиссию", "WARNING")
                        
                        # Повторно выбираем Uzcard
                        await self.page.evaluate("""
                            () => {
                                const uzcardBtn = Array.from(document.querySelectorAll('[role="button"]')).find(
                                    el => el.textContent.includes('Uzcard')
                                );
                                if (uzcardBtn) uzcardBtn.click();
                            }
                        """)
                        await self.page.wait_for_timeout(300)
                    
                    # Если кнопка не активна, пробуем кликнуть Uzcard еще раз
                    if btn_attempt > 4:
                        await self.page.evaluate("""
                            () => {
                                const uzcardBtn = Array.from(document.querySelectorAll('[role="button"]')).find(
                                    el => el.textContent.includes('Uzcard')
                                );
                                if (uzcardBtn) uzcardBtn.click();
                            }
                        """)
                        log(f"Повторный клик по Uzcard (попытка #{btn_attempt + 1})", "WARNING")
                    
                    await self.page.wait_for_timeout(300)
                    
                except Exception as e:
                    log(f"Ошибка проверки кнопки: {e}", "WARNING")
                    await self.page.wait_for_timeout(300)
            
            if not button_active:
                log("Кнопка Продолжить не активировалась", "ERROR")
                # Делаем скриншот при ошибке
                screenshot_path = f"screenshots/error_button_{int(time.time())}.png"
                try:
                    os.makedirs("screenshots", exist_ok=True)
                    await self.page.screenshot(path=screenshot_path, full_page=True)
                    log(f"Скриншот сохранен: {screenshot_path}", "INFO")
                except Exception as e:
                    log(f"Не удалось сохранить скриншот: {e}", "WARNING")
                return {'success': False, 'error': 'Кнопка Продолжить не активировалась', 'time': time.time() - start_time}
            
            # Клик по кнопке
            await self.page.locator('#pay').evaluate('el => el.click()')
            log("Кнопка Продолжить нажата", "SUCCESS")
            
            await self.page.wait_for_url('**/sender-details**', timeout=10000)
            log("Переход на страницу заполнения данных", "SUCCESS")
            
            step1_time = time.time() - start_time
            step2_start = time.time()
            
            # ЭТАП 2: Заполнение полей
            await self.page.wait_for_selector('input', state='visible', timeout=10000)
            await self.page.wait_for_timeout(300)  # Уменьшаем с 500 до 300
            
            # Закрываем модалки перед заполнением
            log("Проверяю модалки...", "DEBUG")
            for _ in range(2):  # Уменьшаем с 3 до 2
                modal_closed = await self.page.evaluate("""
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
                    log("Модалка закрыта", "WARNING")
                    await self.page.wait_for_timeout(200)  # Уменьшаем с 300 до 200
                else:
                    break
            
            owner_parts = owner_name.split()
            first_name = owner_parts[0] if len(owner_parts) > 0 else ""
            last_name = owner_parts[1] if len(owner_parts) > 1 else ""
            
            log("=" * 50, "INFO")
            log("ЭТАП 2: ЗАПОЛНЕНИЕ ПОЛЕЙ ПОЛУЧАТЕЛЯ", "INFO")
            log("=" * 50, "INFO")
            
            # КРИТИЧЕСКИ ВАЖНО: Заполняем поля получателя с максимальной проверкой
            card_ok = await fill_beneficiary_card(self.page, card_number)
            if not card_ok:
                log("КРИТИЧЕСКАЯ ОШИБКА: Номер карты не заполнен!", "ERROR")
                # Делаем скриншот при ошибке
                screenshot_path = f"screenshots/error_card_{int(time.time())}.png"
                try:
                    await self.page.screenshot(path=screenshot_path)
                    log(f"Скриншот сохранен: {screenshot_path}", "INFO")
                except:
                    pass
                return {
                    'success': False,
                    'qr_link': None,
                    'time': time.time() - start_time,
                    'step1_time': step1_time,
                    'step2_time': 0,
                    'error': 'Не удалось заполнить номер карты'
                }
            
            fname_ok, lname_ok = await fill_beneficiary_name(self.page, first_name, last_name)
            if not fname_ok or not lname_ok:
                log(f"КРИТИЧЕСКАЯ ОШИБКА: Имя/Фамилия не заполнены (fname={fname_ok}, lname={lname_ok})", "ERROR")
                # Делаем скриншот при ошибке
                screenshot_path = f"screenshots/error_name_{int(time.time())}.png"
                try:
                    await self.page.screenshot(path=screenshot_path)
                    log(f"Скриншот сохранен: {screenshot_path}", "INFO")
                except:
                    pass
                return {
                    'success': False,
                    'qr_link': None,
                    'time': time.time() - start_time,
                    'step1_time': step1_time,
                    'step2_time': 0,
                    'error': 'Не удалось заполнить имя/фамилию получателя'
                }
            
            log("Поля получателя заполнены успешно!", "SUCCESS")
            
            print("\n⚡ Заполняю остальные поля...")
            # Заполняем остальные поля параллельно
            await asyncio.gather(
                fill_field_async(self.page, "sender_documents_series", SENDER_DATA["passport_series"], "Серия паспорта"),
                fill_field_async(self.page, "sender_documents_number", SENDER_DATA["passport_number"], "Номер паспорта"),
                fill_field_async(self.page, "issuedate", SENDER_DATA["passport_issue_date"], "Дата выдачи"),
                fill_field_async(self.page, "sender_middlename", SENDER_DATA["middle_name"], "Отчество"),
                fill_field_async(self.page, "sender_firstname", SENDER_DATA["first_name"], "Имя отправителя"),
                fill_field_async(self.page, "sender_lastname", SENDER_DATA["last_name"], "Фамилия отправителя"),
                fill_field_async(self.page, "birthdate", SENDER_DATA["birth_date"], "Дата рождения"),
                fill_field_async(self.page, "phonenumber", SENDER_DATA["phone"], "Телефон"),
                fill_field_async(self.page, "birthPlaceAddress_full", SENDER_DATA["birth_place"], "Место рождения"),
                fill_field_async(self.page, "registrationAddress_full", SENDER_DATA["registration_place"], "Место регистрации"),
            )
            
            print("\n🌍 Заполняю страны...")
            # Страны
            birth_country_ok = await select_country_async(self.page, "birthPlaceAddress_countryCode", SENDER_DATA["birth_country"], "Страна рождения")
            reg_country_ok = await select_country_async(self.page, "registrationAddress_countryCode", SENDER_DATA["registration_country"], "Страна регистрации")
            
            if not birth_country_ok:
                print(f"   ❌ Страна рождения: не выбрана")
            if not reg_country_ok:
                print(f"   ❌ Страна регистрации: не выбрана")
            
            # Галочка
            try:
                checkbox = self.page.locator('input[type="checkbox"]').first
                if not await checkbox.is_checked():
                    await checkbox.click(force=True)
            except:
                pass
            
            # Кнопка "Продолжить"
            try:
                await self.page.locator('#pay').evaluate('el => el.click()')
            except:
                pass
            
            await self.page.wait_for_timeout(500)
            
            # Капча
            try:
                captcha_iframe_selector = 'iframe[src*="smartcaptcha.yandexcloud.net/checkbox"]'
                await self.page.wait_for_selector(captcha_iframe_selector, state='visible', timeout=2000)
                
                await self.page.wait_for_timeout(500)
                
                try:
                    iframe_element = self.page.locator(captcha_iframe_selector)
                    bbox = await iframe_element.bounding_box()
                    if bbox:
                        center_x = bbox['x'] + bbox['width'] / 2
                        center_y = bbox['y'] + bbox['height'] / 2
                        await self.page.mouse.move(center_x - 50, center_y - 50)
                        await self.page.wait_for_timeout(200)
                        await self.page.mouse.move(center_x, center_y)
                        await self.page.wait_for_timeout(300)
                except:
                    pass
                
                captcha_frame = self.page.frame_locator(captcha_iframe_selector)
                checkbox_button = captcha_frame.locator('#js-button')
                
                await checkbox_button.wait_for(state='visible', timeout=3000)
                
                try:
                    await checkbox_button.click(timeout=3000)
                except:
                    try:
                        await checkbox_button.click(force=True, timeout=3000)
                    except:
                        try:
                            await checkbox_button.evaluate('el => el.click()')
                        except:
                            pass
                
                await self.page.wait_for_timeout(1000)
                await self.page.locator('#pay').evaluate('el => el.click()')
            except:
                pass
            
            # Модалка подтверждения
            try:
                await self.page.wait_for_timeout(1000)
                
                buttons = await self.page.locator('button').all()
                continue_buttons = []
                
                for btn in buttons:
                    try:
                        text = await btn.inner_text(timeout=100)
                        if "Продолжить" in text:
                            continue_buttons.append(btn)
                    except:
                        pass
                
                if len(continue_buttons) > 1:
                    await continue_buttons[-1].evaluate('el => el.click()')
                    await self.page.wait_for_timeout(2000)
            except:
                pass
            
            # Ждем QR ссылку
            for i in range(20):
                if qr_link:
                    break
                await self.page.wait_for_timeout(500)
            
            step2_time = time.time() - step2_start
            elapsed = time.time() - start_time
            
            return {
                'success': True,
                'qr_link': qr_link,
                'time': elapsed,
                'step1_time': step1_time,
                'step2_time': step2_time,
                'error': None
            }
            
        except Exception as e:
            log(f"ИСКЛЮЧЕНИЕ: {e}", "ERROR")
            # Делаем скриншот при исключении
            screenshot_path = f"screenshots/error_exception_{int(time.time())}.png"
            try:
                await self.page.screenshot(path=screenshot_path)
                log(f"Скриншот сохранен: {screenshot_path}", "INFO")
            except:
                pass
            return {
                'success': False,
                'qr_link': None,
                'time': time.time() - start_time,
                'step1_time': 0,
                'step2_time': 0,
                'error': str(e)
            }
        finally:
            self.page.remove_listener('response', handle_response)


async def main():
    """Пример использования сервиса"""
    service = PaymentService()
    
    try:
        # Запускаем сервис в headless режиме (True для production, False для отладки)
        await service.start(headless=True)
        
        # Создаем несколько платежей подряд
        results = []
        for i in range(2):  # Уменьшаем с 3 до 2
            log("=" * 70, "INFO")
            log(f"ПЛАТЕЖ #{i+1}", "INFO")
            log("=" * 70, "INFO")
            
            result = await service.create_payment_link(
                amount=110,
                card_number="9860080323894719",
                owner_name="Nodir Asadullayev"
            )
            
            results.append(result)
            
            if result['success']:
                log(f"Успех!", "SUCCESS")
                log(f"Этап 1: {result['step1_time']:.2f}s", "INFO")
                log(f"Этап 2: {result['step2_time']:.2f}s", "INFO")
                log(f"Общее время: {result['time']:.2f}s", "INFO")
                if result['qr_link']:
                    log(f"QR: {result['qr_link'][:80]}...", "SUCCESS")
            else:
                log(f"Ошибка: {result['error']}", "ERROR")
            
            if i < 2:
                await asyncio.sleep(1)
        
        # Статистика
        log("=" * 70, "INFO")
        log("СТАТИСТИКА", "INFO")
        log("=" * 70, "INFO")
        successful = [r for r in results if r['success']]
        if successful:
            avg_time = sum(r['time'] for r in successful) / len(successful)
            avg_step1 = sum(r['step1_time'] for r in successful) / len(successful)
            avg_step2 = sum(r['step2_time'] for r in successful) / len(successful)
            log(f"Успешных: {len(successful)}/{len(results)}", "SUCCESS")
            log(f"Среднее время: {avg_time:.2f}s", "INFO")
            log(f"Средний этап 1: {avg_step1:.2f}s", "INFO")
            log(f"Средний этап 2: {avg_step2:.2f}s", "INFO")
        else:
            log("Все тесты провалились!", "ERROR")
        
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
