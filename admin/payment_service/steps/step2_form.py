#!/usr/bin/env python3
"""
ЭТАП 2: Заполнение формы с данными отправителя и получателя
"""

from playwright.async_api import Page
import time
from .form_helpers import fill_field_simple, select_country_async


async def fill_masked_date(page: Page, field_name: str, value: str, label: str, log) -> bool:
    """
    Заполнение поля даты с masked input (react-input-mask / IMask)
    value — уже в формате dd.mm.yyyy (например "17.08.2012")
    field_name — "issueDate" или "birthDate"
    """
    selector = f'input[name="{field_name}"]'
    loc = page.locator(selector)
    
    try:
        # Конвертируем в ISO формат для внутреннего значения
        iso_value = ""
        if '.' in value and len(value.split('.')) == 3:
            d, m, y = value.split('.')
            iso_value = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
        
        log(f"{label}: пробую форматы '{value}' (display) и '{iso_value}' (ISO)", "DEBUG")
        
        # 1. Диагностика - проверяем скрытые поля
        hidden_info = await page.evaluate(f"""
            () => {{
                const el = document.querySelector('input[name="{field_name}"]');
                const hidden = document.querySelector('input[name="{field_name}_hidden"], input[type="hidden"][name*="{field_name}"]');
                return {{
                    visible: el ? el.value : 'not found',
                    hidden: hidden ? hidden.value : 'no hidden',
                    dataRaw: el ? (el.dataset.rawValue || el.dataset.unmasked || 'no data') : 'not found',
                    type: el ? el.type : 'unknown'
                }};
            }}
        """)
        log(f"{label} internals: {hidden_info}", "DEBUG")
        
        # 2. Клик → фокус + активация маски
        await loc.click(force=True, timeout=5000)
        await page.wait_for_timeout(80)
        
        # 3. Очистка
        await loc.fill("", force=True)
        
        # 4. Пробуем заполнить ISO формат через прямую установку value
        if iso_value:
            await loc.evaluate(f"""
                (el) => {{
                    // Устанавливаем ISO значение напрямую
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype,
                        'value'
                    ).set;
                    nativeInputValueSetter.call(el, '{iso_value}');
                    
                    // Триггерим все события
                    ['input', 'change', 'blur'].forEach(eventName => {{
                        el.dispatchEvent(new Event(eventName, {{ bubbles: true, cancelable: true }}));
                    }});
                }}
            """)
            await page.wait_for_timeout(80)  # Сокращено с 200
            
            # Проверяем сработало ли
            check_value = await loc.input_value(timeout=1000)
            if check_value and len(check_value) >= 8:
                log(f"{label} ISO формат сработал: '{check_value}'", "SUCCESS")
                return True
        
        # 5. Fallback - посимвольный ввод display формата
        await loc.click(force=True)
        await page.wait_for_timeout(50)
        await loc.fill("", force=True)
        await loc.press_sequentially(value, delay=15)
        
        # 6. Явно триггерим события
        await loc.evaluate("""
            (el) => {
                ['input', 'change', 'blur'].forEach(eventName => {
                    el.dispatchEvent(new Event(eventName, { bubbles: true, cancelable: true }));
                });
            }
        """)
        
        # 7. Даём React обновить состояние (минимально)
        await page.wait_for_timeout(100)  # Сокращено с 250
        
        # 8. Финальная проверка
        real_val = await loc.input_value(timeout=2000)
        log(f"{label} после заполнения → DOM value = '{real_val}' (ожидали '{value}')", "DEBUG")
        
        return True
        
    except Exception as e:
        log(f"Ошибка заполнения {label}: {str(e)}", "ERROR")
        return False


def ensure_dd_mm_yyyy(s: str) -> str:
    """Нормализация формата даты в dd.mm.yyyy"""
    s = s.strip()
    if '.' not in s:
        return s
    parts = s.split('.')
    if len(parts) == 3:
        d, m, y = [p.zfill(2) if len(p) <= 2 else p for p in parts]
        if len(y) == 2:
            y = '20' + y if int(y) < 50 else '19' + y
        return f"{d}.{m}.{y}"
    return s


async def fill_beneficiary_card(page: Page, card_number: str, log_func) -> bool:
    """Заполнение номера карты получателя"""
    from .form_helpers import fill_react_input
    
    log = log_func
    log(f"Заполняю номер карты: {card_number}", "DEBUG")
    
    for attempt in range(3):
        if attempt > 0:
            log(f"Попытка #{attempt + 1} заполнения карты", "WARNING")
        
        success = await fill_react_input(
            page,
            'input[name="transfer_beneficiaryAccountNumber"]',
            card_number,
            "Номер карты",
            log_func
        )
        
        if success:
            return True
        
        await page.wait_for_timeout(200)
    
    log("Не удалось заполнить номер карты после 3 попыток", "ERROR")
    return False


async def fill_beneficiary_name(page: Page, first_name: str, last_name: str, log_func) -> tuple:
    """Заполнение имени и фамилии получателя"""
    from .form_helpers import fill_react_input
    
    log = log_func
    log(f"Заполняю имя получателя: {first_name} {last_name}", "DEBUG")
    
    fname_ok = await fill_react_input(
        page,
        'input[name="beneficiary_firstName"]',
        first_name,
        "Имя получателя",
        log_func
    )
    
    await page.wait_for_timeout(150)
    
    lname_ok = await fill_react_input(
        page,
        'input[name="beneficiary_lastName"]',
        last_name,
        "Фамилия получателя",
        log_func
    )
    
    return (fname_ok, lname_ok)


async def process_step2(page: Page, card_number: str, owner_name: str, sender_data: dict, log_func, amount: int = 0) -> dict:
    """
    Этап 2: Заполнение формы с данными
    
    Args:
        page: Playwright page объект
        card_number: Номер карты получателя
        owner_name: Имя владельца карты
        sender_data: Данные отправителя из БД
        log_func: Функция для логирования
        amount: Сумма платежа для отправки в PayzTeam API
    
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
        
        log("📝 Серия паспорта...", "DEBUG")
        await fill_field_simple(page, "sender_documents_series", sender_data["passport_series"], "Серия паспорта", log)
        
        log("📝 Номер паспорта...", "DEBUG")
        await fill_field_simple(page, "sender_documents_number", sender_data["passport_number"], "Номер паспорта", log)
        
        log("📝 Дата выдачи паспорта...", "DEBUG")
        issue_date = ensure_dd_mm_yyyy(sender_data["passport_issue_date"])
        ok_issue = await fill_masked_date(page, "issueDate", issue_date, "Дата выдачи паспорта", log)
        if not ok_issue:
            log("⚠️ Дата выдачи паспорта не заполнена корректно", "WARNING")
        
        log("📝 Отчество...", "DEBUG")
        await fill_field_simple(page, "sender_middleName", sender_data["middle_name"], "Отчество", log)
        
        log("📝 Имя отправителя...", "DEBUG")
        await fill_field_simple(page, "sender_firstName", sender_data["first_name"], "Имя отправителя", log)
        
        log("📝 Фамилия отправителя...", "DEBUG")
        await fill_field_simple(page, "sender_lastName", sender_data["last_name"], "Фамилия отправителя", log)
        
        log("📝 Дата рождения...", "DEBUG")
        birth_date = ensure_dd_mm_yyyy(sender_data["birth_date"])
        ok_birth = await fill_masked_date(page, "birthDate", birth_date, "Дата рождения", log)
        if not ok_birth:
            log("⚠️ Дата рождения не заполнена корректно", "WARNING")
        
        log("📝 Телефон...", "DEBUG")
        await fill_field_simple(page, "phoneNumber", sender_data["phone"], "Телефон", log)
        
        log("📝 Место рождения...", "DEBUG")
        await fill_field_simple(page, "birthPlaceAddress_full", sender_data["birth_place"], "Место рождения", log)
        
        log("📝 Место регистрации...", "DEBUG")
        await fill_field_simple(page, "registrationAddress_full", sender_data["registration_place"], "Место регистрации", log)
        
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
        
        # Пауза перед заполнением получателя (убрана)
        log("Жду обработки полей отправителя...", "DEBUG")
        # await page.wait_for_timeout(100)  # Убрано для скорости
        
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
        
        await page.wait_for_timeout(50)
        
        fname_ok, lname_ok = await fill_beneficiary_name(page, first_name, last_name, log)
        if not fname_ok or not lname_ok:
            log(f"КРИТИЧЕСКАЯ ОШИБКА: Имя/Фамилия не заполнены (fname={fname_ok}, lname={lname_ok})", "ERROR")
            return {
                'success': False,
                'time': time.time() - start_time,
                'error': 'Не удалось заполнить имя/фамилию получателя'
            }
        
        log("✅ Реквизиты получателя заполнены успешно!", "SUCCESS")
        
        # Прокликиваем ключевые поля для валидации (оптимизировано)
        log("Прокликиваю ключевые поля для валидации...", "DEBUG")
        try:
            # Клик по body для общей валидации
            await page.evaluate("document.body.click()")
            await page.wait_for_timeout(30)  # Минимальная пауза
            log("Поля прокликаны", "SUCCESS")
        except Exception as e:
            log(f"Ошибка при прокликивании полей: {e}", "WARNING")
        
        # Ждем обработки (убрана)
        log("Жду обработки всех полей...", "DEBUG")
        # await page.wait_for_timeout(100)  # Убрано для скорости
        
        # Нажимаем кнопку Продолжить
        try:
            await page.locator('#pay').evaluate('el => el.click()')
            log("Кнопка Продолжить нажата (этап 2)", "SUCCESS")
        except:
            pass
        
        await page.wait_for_timeout(50)  # Сокращено с 100
        
        # === ОБРАБОТКА КАПЧИ (МАКСИМАЛЬНО БЫСТРАЯ) ===
        log("Отслеживаю появление капчи...", "DEBUG")
        try:
            captcha_iframe_selector = 'iframe[src*="smartcaptcha.yandexcloud.net/checkbox"]'
            
            # Ждем появления iframe капчи
            await page.wait_for_selector(captcha_iframe_selector, state='visible', timeout=2000)
            log("✅ Капча появилась!", "SUCCESS")
            
            # Сразу получаем фрейм и кнопку БЕЗ ЗАДЕРЖЕК
            captcha_frame = page.frame_locator(captcha_iframe_selector)
            checkbox_button = captcha_frame.locator('#js-button')
            
            # Ждем кнопку и НЕМЕДЛЕННО кликаем
            await checkbox_button.wait_for(state='visible', timeout=1500)
            await checkbox_button.click(timeout=1000)
            log("✅ Капча решена мгновенно!", "SUCCESS")
            
            # Даём время на появление модалки после капчи
            await page.wait_for_timeout(100)  # Сокращено с 200
            
        except Exception as e:
            log(f"Капча не обнаружена или ошибка: {e}", "DEBUG")
            # Если капчи не было, всё равно даём время на модалку
            await page.wait_for_timeout(100)
        
        # Модалка "Проверка данных" - ждём её появления активно (оптимизировано)
        log("Отслеживаю модалку 'Проверка данных'...", "DEBUG")
        modal_found = False
        try:
            # Активное ожидание модалки до 2 секунд (было 3)
            for attempt in range(4):  # Было 6
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
                    modal_found = True
                    break
                
                if attempt < 3:  # Было 5
                    await page.wait_for_timeout(150)  # Было 200
            
            modal_info = modal_info if modal_found else {'found': False, 'text': ''}
            
            if modal_info['found']:
                log(f"📋 Модалка 'Проверка данных' обнаружена!", "INFO")
                log(f"Текст модалки: {modal_info['text']}", "DEBUG")
                
                if 'Ошибка' in modal_info['text'] or 'ошибка' in modal_info['text']:
                    log("⚠️ ОШИБКА: Реквизиты получателя устарели!", "WARNING")
                    return {
                        'success': False,
                        'time': time.time() - start_time,
                        'error': 'Реквизиты получателя больше не актуальны'
                    }
                else:
                    log("✅ Модалка подтверждения - нажимаю 'Продолжить'", "SUCCESS")
                    try:
                        button = page.locator('button:has-text("Продолжить")').last
                        await button.wait_for(state='visible', timeout=3000)
                        
                        for method in ['click', 'force', 'js']:
                            try:
                                if method == 'click':
                                    await button.click(timeout=2000)
                                elif method == 'force':
                                    await button.click(force=True, timeout=2000)
                                elif method == 'js':
                                    await button.evaluate('el => el.click()')
                                log(f"Кнопка модалки нажата ({method})", "DEBUG")
                                break
                            except:
                                pass
                        
                        await page.wait_for_timeout(50)  # Сокращено с 100
                        log("Модалка закрыта, нажимаю основную кнопку", "DEBUG")
                        
                        # ВАЖНО: После закрытия модалки нажимаем основную кнопку #pay
                        try:
                            is_enabled = await page.evaluate("""
                                () => {
                                    const btn = document.getElementById('pay');
                                    return btn && !btn.disabled;
                                }
                            """)
                            
                            if is_enabled:
                                await page.locator('#pay').click(force=True)
                                log("✅ Основная кнопка Продолжить нажата", "SUCCESS")
                                
                                # Ждем навигации или изменения URL
                                try:
                                    await page.wait_for_url(lambda url: 'sender-details' not in url, timeout=5000)
                                    log(f"✅ Навигация выполнена: {page.url}", "SUCCESS")
                                except:
                                    log(f"URL не изменился: {page.url}", "DEBUG")
                            else:
                                log("⚠️ Основная кнопка не активна", "WARNING")
                        except Exception as e:
                            log(f"⚠️ Ошибка при нажатии основной кнопки: {e}", "WARNING")
                        
                    except Exception as e:
                        log(f"⚠️ Ошибка при обработке модалки: {e}", "WARNING")
            else:
                log("Модалка 'Проверка данных' не появилась (это нормально)", "DEBUG")
        except Exception as e:
            log(f"Ошибка при отслеживании модалки: {e}", "WARNING")
        
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
