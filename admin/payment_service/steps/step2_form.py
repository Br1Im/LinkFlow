#!/usr/bin/env python3
"""
ЭТАП 2: Заполнение формы с данными отправителя и получателя
"""

from playwright.async_api import Page
import time
from .form_helpers import fill_field_simple, select_country_async


async def fill_beneficiary_card(page: Page, card_number: str, log_func) -> bool:
    """Заполнение номера карты получателя"""
    log = log_func
    log(f"Заполняю номер карты: {card_number}", "DEBUG")
    
    for attempt in range(3):
        if attempt > 0:
            log(f"Попытка #{attempt + 1} заполнения карты", "WARNING")
        
        try:
            locator = page.locator('input[name="transfer_beneficiaryAccountNumber"]')
            await locator.wait_for(state="visible", timeout=7000)
            await locator.click(force=True)
            await locator.evaluate("el => { el.focus(); el.value = ''; }")
            await page.wait_for_timeout(30)
            
            escaped = card_number.replace('\\', '\\\\').replace("'", "\\'")
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
            
            current = await locator.input_value()
            if current.strip() == card_number.strip():
                log(f"✅ Номер карты заполнен: {card_number}", "SUCCESS")
                return True
        except Exception as e:
            log(f"Ошибка заполнения карты: {e}", "WARNING")
        
        await page.wait_for_timeout(300)
    
    log("Не удалось заполнить номер карты после 3 попыток", "ERROR")
    return False


async def fill_beneficiary_name(page: Page, first_name: str, last_name: str, log_func) -> tuple:
    """Заполнение имени и фамилии получателя"""
    log = log_func
    log(f"Заполняю имя получателя: {first_name} {last_name}", "DEBUG")
    
    fname_ok = False
    lname_ok = False
    
    try:
        # Имя
        fname_locator = page.locator('input[name="beneficiary_firstName"]')
        await fname_locator.wait_for(state="visible", timeout=5000)
        await fname_locator.click(force=True)
        await fname_locator.evaluate("el => { el.focus(); el.value = ''; }")
        await page.wait_for_timeout(30)
        
        escaped_fname = first_name.replace('\\', '\\\\').replace("'", "\\'")
        await fname_locator.evaluate(f"""
            (el) => {{
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value'
                ).set;
                nativeInputValueSetter.call(el, '{escaped_fname}');
                el.dispatchEvent(new Event('input',  {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                el.dispatchEvent(new Event('blur',   {{ bubbles: true }}));
            }}
        """)
        await page.wait_for_timeout(250)
        
        current_fname = await fname_locator.input_value()
        if current_fname.strip() == first_name.strip():
            log(f"✅ Имя получателя заполнено: {first_name}", "SUCCESS")
            fname_ok = True
        
        # Фамилия
        lname_locator = page.locator('input[name="beneficiary_lastName"]')
        await lname_locator.wait_for(state="visible", timeout=5000)
        await lname_locator.click(force=True)
        await lname_locator.evaluate("el => { el.focus(); el.value = ''; }")
        await page.wait_for_timeout(30)
        
        escaped_lname = last_name.replace('\\', '\\\\').replace("'", "\\'")
        await lname_locator.evaluate(f"""
            (el) => {{
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value'
                ).set;
                nativeInputValueSetter.call(el, '{escaped_lname}');
                el.dispatchEvent(new Event('input',  {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                el.dispatchEvent(new Event('blur',   {{ bubbles: true }}));
            }}
        """)
        await page.wait_for_timeout(250)
        
        current_lname = await lname_locator.input_value()
        if current_lname.strip() == last_name.strip():
            log(f"✅ Фамилия получателя заполнена: {last_name}", "SUCCESS")
            lname_ok = True
            
    except Exception as e:
        log(f"Ошибка заполнения имени/фамилии: {e}", "ERROR")
    
    return (fname_ok, lname_ok)


async def process_step2(page: Page, card_number: str, owner_name: str, sender_data: dict, log_func) -> dict:
    """
    Этап 2: Заполнение формы с данными
    
    Args:
        page: Playwright page объект
        card_number: Номер карты получателя
        owner_name: Имя владельца карты
        sender_data: Данные отправителя из БД
        log_func: Функция для логирования
    
    Returns:
        dict: {'success': bool, 'time': float, 'error': str or None}
    """
    log = log_func
    start_time = time.time()
    
    try:
        log("=" * 50, "INFO")
        log("ЭТАП 2: ЗАПОЛНЕНИЕ ПОЛЕЙ", "INFO")
        log("=" * 50, "INFO")
        
        # Ждем загрузки страницы
        await page.wait_for_selector('input', state='visible', timeout=10000)
        await page.wait_for_function("""
            () => {
                const cardInput = document.querySelector('input[name="transfer_beneficiaryAccountNumber"]');
                const firstNameInput = document.querySelector('input[name="beneficiary_firstName"]');
                const lastNameInput = document.querySelector('input[name="beneficiary_lastName"]');
                return cardInput && firstNameInput && lastNameInput;
            }
        """, timeout=5000)
        
        # Закрываем модалки
        log("Проверяю модалки...", "DEBUG")
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
            log("Модалка закрыта", "WARNING")
            await page.wait_for_timeout(50)
        
        # Разбиваем имя получателя
        owner_parts = owner_name.split()
        first_name = owner_parts[0] if len(owner_parts) > 0 else ""
        last_name = owner_parts[1] if len(owner_parts) > 1 else ""
        
        # Заполняем поля отправителя
        log("⚡ Заполняю поля отправителя...", "INFO")
        
        await fill_field_simple(page, "sender_documents_series", sender_data["passport_series"], "Серия паспорта", log)
        await page.wait_for_timeout(100)
        
        await fill_field_simple(page, "sender_documents_number", sender_data["passport_number"], "Номер паспорта", log)
        await page.wait_for_timeout(100)
        
        await fill_field_simple(page, "issueDate", sender_data["passport_issue_date"], "Дата выдачи", log)
        await page.wait_for_timeout(100)
        
        await fill_field_simple(page, "sender_middleName", sender_data["middle_name"], "Отчество", log)
        await page.wait_for_timeout(100)
        
        await fill_field_simple(page, "sender_firstName", sender_data["first_name"], "Имя отправителя", log)
        await page.wait_for_timeout(100)
        
        await fill_field_simple(page, "sender_lastName", sender_data["last_name"], "Фамилия отправителя", log)
        await page.wait_for_timeout(100)
        
        await fill_field_simple(page, "birthDate", sender_data["birth_date"], "Дата рождения", log)
        await page.wait_for_timeout(100)
        
        await fill_field_simple(page, "phoneNumber", sender_data["phone"], "Телефон", log)
        await page.wait_for_timeout(100)
        
        await fill_field_simple(page, "birthPlaceAddress_full", sender_data["birth_place"], "Место рождения", log)
        await page.wait_for_timeout(100)
        
        await fill_field_simple(page, "registrationAddress_full", sender_data["registration_place"], "Место регистрации", log)
        await page.wait_for_timeout(100)
        
        # Страны
        log("🌍 Заполняю страны...", "INFO")
        birth_country_ok = await select_country_async(page, "birthPlaceAddress_countryCode", sender_data["birth_country"], "Страна рождения", log)
        reg_country_ok = await select_country_async(page, "registrationAddress_countryCode", sender_data["registration_country"], "Страна регистрации", log)
        
        if not birth_country_ok:
            log("❌ Страна рождения: не выбрана", "WARNING")
        if not reg_country_ok:
            log("❌ Страна регистрации: не выбрана", "WARNING")
        
        # Галочка согласия
        try:
            checkbox = page.locator('input[type="checkbox"]').first
            if not await checkbox.is_checked():
                await checkbox.click(force=True)
        except:
            pass
        
        # Пауза перед заполнением получателя
        log("Жду обработки полей отправителя...", "DEBUG")
        await page.wait_for_timeout(700)
        
        # Заполняем реквизиты получателя
        log("💳 Заполняю реквизиты получателя...", "INFO")
        
        card_ok = await fill_beneficiary_card(page, card_number, log)
        if not card_ok:
            log("КРИТИЧЕСКАЯ ОШИБКА: Номер карты не заполнен!", "ERROR")
            return {
                'success': False,
                'time': time.time() - start_time,
                'error': 'Не удалось заполнить номер карты'
            }
        
        await page.wait_for_timeout(300)
        
        fname_ok, lname_ok = await fill_beneficiary_name(page, first_name, last_name, log)
        if not fname_ok or not lname_ok:
            log(f"КРИТИЧЕСКАЯ ОШИБКА: Имя/Фамилия не заполнены (fname={fname_ok}, lname={lname_ok})", "ERROR")
            return {
                'success': False,
                'time': time.time() - start_time,
                'error': 'Не удалось заполнить имя/фамилию получателя'
            }
        
        log("✅ Реквизиты получателя заполнены успешно!", "SUCCESS")
        
        # Прокликиваем все поля для валидации
        log("Прокликиваю все поля для пересчета валидации...", "DEBUG")
        try:
            all_inputs = await page.locator('input[type="text"], input[type="tel"]').all()
            for inp in all_inputs:
                try:
                    if await inp.is_visible():
                        await inp.click(timeout=100)
                        await page.wait_for_timeout(30)
                except:
                    pass
            
            await page.evaluate("document.body.click()")
            await page.wait_for_timeout(200)
            log("Все поля прокликаны", "SUCCESS")
        except Exception as e:
            log(f"Ошибка при прокликивании полей: {e}", "WARNING")
        
        # Ждем обработки
        log("Жду обработки всех полей...", "DEBUG")
        await page.wait_for_timeout(700)
        
        # Нажимаем кнопку Продолжить
        try:
            await page.locator('#pay').evaluate('el => el.click()')
            log("Кнопка Продолжить нажата (этап 2)", "SUCCESS")
        except:
            pass
        
        await page.wait_for_timeout(1000)
        
        elapsed_time = time.time() - start_time
        log(f"⏱️ Этап 2 занял: {elapsed_time:.2f}s", "INFO")
        
        return {
            'success': True,
            'time': elapsed_time,
            'error': None
        }
        
    except Exception as e:
        log(f"Ошибка на этапе 2: {e}", "ERROR")
        return {
            'success': False,
            'time': time.time() - start_time,
            'error': str(e)
        }
