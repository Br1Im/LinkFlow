#!/usr/bin/env python3
"""
Вспомогательные функции для заполнения форм
"""

from playwright.async_api import Page


async def fill_react_input(page: Page, selector: str, value: str, field_name_for_log: str = "", log_func=None):
    """
    Надёжный способ заполнения controlled input в React/MUI
    Для дат используем посимвольный ввод
    """
    log = log_func if log_func else print
    
    try:
        locator = page.locator(selector)
        await locator.wait_for(state="visible", timeout=7000)
        
        # Проверяем если это поле даты
        is_date_field = 'Date' in selector or 'date' in selector.lower()
        
        if is_date_field:
            # Для дат используем посимвольный ввод
            await locator.click()
            await page.wait_for_timeout(50)
            await locator.fill("")
            await page.wait_for_timeout(50)
            
            # Вводим каждый символ с задержкой
            for char in value:
                await locator.type(char, delay=10)
            
            await page.wait_for_timeout(50)
            await locator.blur()
            await page.wait_for_timeout(100)
        else:
            # Для обычных полей используем JavaScript подход
            await locator.click(force=True)
            await locator.evaluate("el => { el.focus(); el.value = ''; }")
            await page.wait_for_timeout(30)
            
            escaped = value.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
            await locator.evaluate(f"""
                (el) => {{
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value'
                    ).set;
                    nativeInputValueSetter.call(el, '{escaped}');
                    
                    el.dispatchEvent(new Event('input',  {{ bubbles: true }}));
                    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    el.dispatchEvent(new Event('blur',   {{ bubbles: true }}));
                }}
            """)
            await page.wait_for_timeout(120)
        
        # Проверка результата
        current = await locator.input_value()
        is_invalid = await locator.evaluate("el => el.getAttribute('aria-invalid') === 'true'")
        
        # Для телефона проверяем что номер содержится
        if 'phoneNumber' in selector:
            value_digits = ''.join(filter(str.isdigit, value))
            current_digits = ''.join(filter(str.isdigit, current))
            if value_digits in current_digits and not is_invalid:
                log(f"✅ {field_name_for_log or selector}: {current}", "SUCCESS")
                return True
        
        if current.strip() == value.strip() and not is_invalid:
            log(f"✅ {field_name_for_log or selector}: {value}", "SUCCESS")
            return True
        elif len(value) > 5 and value in current and not is_invalid:
            log(f"✅ {field_name_for_log or selector}: {current}", "SUCCESS")
            return True
        else:
            log(f"⚠️ {field_name_for_log or selector}: value={current}, invalid={is_invalid}", "WARNING")
            return False
    
    except Exception as e:
        log(f"❌ Ошибка заполнения {field_name_for_log}: {e}", "ERROR")
        return False


async def fill_field_simple(page: Page, field_name: str, value: str, label: str, log_func=None):
    """Заполнение поля через надёжный React-паттерн"""
    return await fill_react_input(
        page,
        f'input[name="{field_name}"]',
        value,
        label,
        log_func
    )


async def select_country_async(page: Page, pattern: str, country: str, field_name: str, log_func=None):
    """Асинхронный выбор страны с проверкой правильного выбора"""
    log = log_func if log_func else print
    
    try:
        inputs = await page.locator('input').all()
        
        for inp in inputs:
            name_attr = await inp.get_attribute('name') or ""
            if pattern in name_attr:
                # Пробуем до 3 раз
                for attempt in range(3):
                    await inp.click()
                    await page.wait_for_timeout(100)
                    await inp.fill("")
                    await page.wait_for_timeout(50)
                    await inp.fill(country)
                    await page.wait_for_timeout(200)
                    
                    try:
                        # Ждем появления опций
                        await page.wait_for_selector('li[role="option"]', state='visible', timeout=1000)
                        
                        # Ищем нужную страну в списке
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
                                    log(f"   ✅ {field_name}: {current_value}", "SUCCESS")
                                    found = True
                                    break
                        
                        if found:
                            return True
                        else:
                            log(f"   ⚠️ {field_name}: страна не найдена в списке, попытка {attempt + 1}", "WARNING")
                            
                    except Exception:
                        # Если опции не появились, жмем Enter
                        await page.keyboard.press('Enter')
                        await page.wait_for_timeout(100)
                        
                        # Проверяем результат
                        current_value = await inp.input_value()
                        if country.lower() in current_value.lower():
                            log(f"   ✅ {field_name}: {current_value} (Enter)", "SUCCESS")
                            return True
                
                log(f"   ❌ {field_name}: не удалось выбрать после 3 попыток", "ERROR")
                return False
        
        return False
    except Exception as e:
        log(f"   ❌ {field_name}: ошибка - {e}", "ERROR")
        return False
