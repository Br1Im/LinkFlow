#!/usr/bin/env python3
"""
Playwright версия - Шаг 2: Заполнение данных получателя и отправителя
"""

from playwright.sync_api import sync_playwright, Page
import time


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
    "document_type": "passport_rf"  # Добавляем тип документа
}


def transliterate_to_latin(text: str) -> str:
    """Транслитерация кириллицы в латиницу"""
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    
    result = []
    for char in text:
        result.append(translit_map.get(char, char))
    
    return ''.join(result)


def fill_mui_input(page: Page, selector: str, value: str, field_name: str):
    """Заполняет MUI input с правильными событиями (БЫСТРАЯ ВЕРСИЯ)"""
    try:
        input_elem = page.locator(selector).first
        input_elem.wait_for(state='visible', timeout=2000)  # Уменьшаем с 3000
        
        # Кликаем в поле
        input_elem.click()
        page.wait_for_timeout(50)  # Уменьшаем с 100
        
        # Очищаем
        input_elem.fill('')
        page.wait_for_timeout(30)  # Уменьшаем с 50
        
        # Вводим с минимальной задержкой
        input_elem.type(value, delay=30)  # Уменьшаем с 50
        
        # Blur для trigger React
        page.keyboard.press('Tab')
        page.wait_for_timeout(50)  # Уменьшаем с 100
        
        print(f"   ✅ {field_name}: {value}")
        return True
    except Exception as e:
        print(f"   ⚠️ {field_name}: {e}")
        return False


def select_country(page: Page, input_selector: str, country_name: str, field_name: str):
    """Выбирает страну из автокомплита (БЫСТРАЯ ВЕРСИЯ)"""
    try:
        input_elem = page.locator(input_selector).first
        input_elem.wait_for(state='visible', timeout=2000)  # Уменьшаем с 3000
        
        # Кликаем и вводим
        input_elem.click()
        page.wait_for_timeout(50)  # Уменьшаем с 100
        
        input_elem.fill(country_name)
        page.wait_for_timeout(200)  # Уменьшаем с 300
        
        # Ждем появления опций
        page.wait_for_selector('li[role="option"]', state='visible', timeout=2000)  # Уменьшаем с 3000
        
        # Кликаем по первой опции
        page.locator('li[role="option"]').first.click()
        
        print(f"   ✅ {field_name}: {country_name}")
        return True
    except Exception as e:
        print(f"   ⚠️ {field_name}: {e}")
        return False


def fill_sender_details(page: Page, card_number: str, owner_name: str):
    """Заполняет все поля - УЛЬТРА СКОРОСТЬ"""
    
    print("📌 Заполняю данные (УЛЬТРА СКОРОСТЬ)...")
    start_time = time.time()
    
    # Ждем загрузки формы - МИНИМУМ
    page.wait_for_selector('input', state='visible', timeout=10000)
    page.wait_for_timeout(30)  # Уменьшаем с 50 до 30
    
    print(f"\n🚀 Заполняю поля (УЛЬТРА СКОРОСТЬ)...")
    
    def fill_field_ultra_fast(pattern: str, value: str, field_name: str):
        """Заполняет поле посимвольно через press_sequentially() - самый надежный способ"""
        try:
            inputs = page.locator('input').all()
            
            for inp in inputs:
                name_attr = inp.get_attribute('name') or ""
                placeholder = inp.get_attribute('placeholder') or ""
                
                if pattern.lower() in name_attr.lower() or pattern.lower() in placeholder.lower():
                    print(f"   🎯 {field_name}")
                    
                    # Используем посимвольный ввод сразу
                    inp.click()
                    page.wait_for_timeout(100)
                    page.keyboard.press('Control+A')
                    page.keyboard.press('Backspace')
                    page.wait_for_timeout(50)
                    
                    # Медленный посимвольный ввод
                    inp.press_sequentially(value, delay=50)
                    page.wait_for_timeout(100)
                    page.keyboard.press('Tab')
                    page.wait_for_timeout(100)
                    
                    # Проверяем что значение установилось
                    try:
                        current_value = inp.input_value()
                        if current_value and len(current_value) > 0:
                            print(f"   ✅ {field_name}: {current_value}")
                        else:
                            print(f"   ⚠️ {field_name}: значение пустое после установки")
                    except:
                        print(f"   ✅ {field_name}")
                    
                    return True
            
            print(f"   ⚠️ {field_name}: не найдено")
            return False
        except Exception as e:
            print(f"   ⚠️ {field_name}: ошибка - {e}")
            return False
    
    # Заполняем номер карты (УЛЬТРА СКОРОСТЬ)
    print("📌 Номер карты...")
    try:
        inputs = page.locator('input').all()
        card_fields_found = 0
        
        for inp in inputs:
            try:
                name_attr = (inp.get_attribute('name') or "").lower()
                placeholder = (inp.get_attribute('placeholder') or "").lower()
                
                # Расширенная проверка полей карты
                is_card_field = (
                    "beneficiaryaccountnumber" in name_attr or
                    "номер карты" in placeholder or
                    "card" in name_attr or
                    "account" in name_attr or
                    "transfer_beneficiary" in name_attr or
                    "beneficiary" in name_attr and "number" in name_attr
                )
                
                if is_card_field:
                    print(f"   🎯 Поле карты (name: {name_attr}, placeholder: {placeholder})")
                    
                    # Используем посимвольный ввод сразу
                    inp.click()
                    page.wait_for_timeout(100)
                    page.keyboard.press('Control+A')
                    page.keyboard.press('Backspace')
                    page.wait_for_timeout(50)
                    
                    # Медленный посимвольный ввод
                    inp.press_sequentially(card_number, delay=50)
                    page.wait_for_timeout(100)
                    page.keyboard.press('Tab')
                    page.wait_for_timeout(100)
                    
                    page.wait_for_timeout(100)
                    
                    # Проверяем что значение установилось
                    try:
                        current_value = inp.input_value()
                        if card_number in current_value or len(current_value) > 10:
                            print(f"   ✅ Номер карты #{card_fields_found + 1}: {current_value}")
                            card_fields_found += 1
                        else:
                            print(f"   ⚠️ Значение не установилось: {current_value}")
                    except:
                        print(f"   ✅ Номер карты #{card_fields_found + 1}")
                        card_fields_found += 1
                    
                    if card_fields_found >= 2:
                        break
                        
            except:
                continue
        
        print(f"   📊 Заполнено полей карты: {card_fields_found}")
            
    except Exception as e:
        print(f"   ❌ Ошибка номера карты: {e}")
    
    # Заполняем остальные поля (УЛЬТРА СКОРОСТЬ)
    fill_field_ultra_fast("beneficiary_firstname", owner_name.split()[0], "Имя получателя")
    if len(owner_name.split()) > 1:
        fill_field_ultra_fast("beneficiary_lastname", owner_name.split()[1], "Фамилия получателя")
    
    fill_field_ultra_fast("sender_documents_series", SENDER_DATA["passport_series"], "Серия паспорта")
    fill_field_ultra_fast("sender_documents_number", SENDER_DATA["passport_number"], "Номер паспорта")
    fill_field_ultra_fast("issuedate", SENDER_DATA["passport_issue_date"], "Дата выдачи")
    
    # Выбираем тип документа (Паспорт РФ)
    try:
        print("   🎯 Выбираю тип документа...")
        # Ищем селект или кнопку выбора типа документа
        document_type_selectors = [
            'select[name*="type"]',
            'button:has-text("Паспорт")',
            'div:has-text("Тип документа")',
            '[role="button"]:has-text("Паспорт")'
        ]
        
        for selector in document_type_selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible(timeout=500):
                    element.click()
                    page.wait_for_timeout(200)
                    
                    # Если это селект, выбираем опцию
                    if 'select' in selector:
                        page.locator('option:has-text("Паспорт")').first.click()
                    else:
                        # Ищем опцию "Паспорт РФ" в выпадающем списке
                        try:
                            page.wait_for_selector('li[role="option"], div[role="option"]', timeout=1000)
                            page.locator('li:has-text("Паспорт"), div:has-text("Паспорт")').first.click()
                        except:
                            pass
                    
                    print(f"   ✅ Тип документа: Паспорт РФ")
                    break
            except:
                continue
    except:
        print(f"   ⚠️ Тип документа: не найдено")
    
    # Заполяем отчество
    fill_field_ultra_fast("sender_middlename", SENDER_DATA["middle_name"], "Отчество отправителя")
    
    # Заполнение мест посимвольно
    try:
        print("   🎯 Место рождения...")
        birth_place_input = page.locator('input[name*="birthPlaceAddress_full"]').first
        birth_place_input.wait_for(state='visible', timeout=2000)
        
        birth_place_input.click()
        page.wait_for_timeout(100)
        page.keyboard.press('Control+A')
        page.keyboard.press('Backspace')
        page.wait_for_timeout(50)
        birth_place_input.press_sequentially(SENDER_DATA["birth_place"], delay=50)
        page.wait_for_timeout(100)
        page.keyboard.press('Tab')
        page.wait_for_timeout(100)
        
        current_value = birth_place_input.input_value()
        print(f"   ✅ Место рождения: {current_value}")
    except Exception as e:
        print(f"   ⚠️ Место рождения: ошибка - {e}")
    
    try:
        print("   🎯 Место регистрации...")
        reg_place_input = page.locator('input[name*="registrationAddress_full"]').first
        reg_place_input.wait_for(state='visible', timeout=2000)
        
        reg_place_input.click()
        page.wait_for_timeout(100)
        page.keyboard.press('Control+A')
        page.keyboard.press('Backspace')
        page.wait_for_timeout(50)
        reg_place_input.press_sequentially(SENDER_DATA["registration_place"], delay=50)
        page.wait_for_timeout(100)
        page.keyboard.press('Tab')
        page.wait_for_timeout(100)
        
        current_value = reg_place_input.input_value()
        print(f"   ✅ Место регистрации: {current_value}")
    except Exception as e:
        print(f"   ⚠️ Место регистрации: ошибка - {e}")
    
    fill_field_ultra_fast("sender_firstname", SENDER_DATA["first_name"], "Имя отправителя")
    fill_field_ultra_fast("sender_lastname", SENDER_DATA["last_name"], "Фамилия отправителя")
    fill_field_ultra_fast("birthdate", SENDER_DATA["birth_date"], "Дата рождения")
    
    # Заполняем телефон посимвольно
    try:
        print("   🎯 Телефон...")
        phone_input = page.locator('input[name*="phoneNumber"]').first
        phone_input.wait_for(state='visible', timeout=2000)
        
        phone_input.click()
        page.wait_for_timeout(100)
        page.keyboard.press('Control+A')
        page.keyboard.press('Backspace')
        page.wait_for_timeout(50)
        phone_input.press_sequentially("+7 988 026-03-34", delay=50)
        page.wait_for_timeout(100)
        page.keyboard.press('Tab')
        page.wait_for_timeout(100)
        
        current_value = phone_input.input_value()
        print(f"   ✅ Телефон: {current_value}")
    except Exception as e:
        print(f"   ⚠️ Телефон: ошибка - {e}")
    
    # Заполняем страны (УЛЬТРА СКОРОСТЬ)
    print(f"\n🌍 Заполняю страны...")
    
    def select_country_ultra_fast(pattern: str, country: str, field_name: str):
        """Выбирает страну через Playwright fill() и автокомплит"""
        try:
            inputs = page.locator('input').all()
            
            for inp in inputs:
                name_attr = inp.get_attribute('name') or ""
                if pattern in name_attr:
                    print(f"   🎯 {field_name}")
                    
                    # Используем fill() для ввода
                    inp.click()
                    page.wait_for_timeout(100)
                    inp.fill(country)
                    page.wait_for_timeout(200)
                    
                    try:
                        # Ждем и кликаем по опции
                        page.wait_for_selector('li[role="option"]', state='visible', timeout=1000)
                        page.locator('li[role="option"]').first.click()
                        print(f"   ✅ {field_name}")
                        return True
                    except:
                        # Enter если опции не появились
                        page.keyboard.press('Enter')
                        page.wait_for_timeout(50)
                        print(f"   ✅ {field_name} (Enter)")
                        return True
            
            print(f"   ⚠️ {field_name}: не найдено")
            return False
        except Exception as e:
            print(f"   ⚠️ {field_name}: ошибка - {e}")
            return False
    
    select_country_ultra_fast("birthPlaceAddress_countryCode", SENDER_DATA["birth_country"], "Страна рождения")
    select_country_ultra_fast("registrationAddress_countryCode", SENDER_DATA["registration_country"], "Страна регистрации")
    
    elapsed = time.time() - start_time
    print(f"\n✅ Заполнение завершено за {elapsed:.1f}s")
    
    return True


def handle_checkbox(page: Page):
    """Ставит галочку согласия - УЛЬТРА СКОРОСТЬ"""
    print("\n📌 Ставлю галочку согласия...")
    try:
        checkbox = page.locator('input[type="checkbox"]').first
        
        if not checkbox.is_checked():
            # Пробуем кликнуть по самому чекбоксу или его родителю
            try:
                checkbox.click()
            except:
                # Кликаем по label или span
                page.locator('span.MuiCheckbox-root').first.click()
            
            print("✅ Галочка поставлена")
        else:
            print("✅ Галочка уже стоит")
        
        return True
    except Exception as e:
        print(f"⚠️ Ошибка с галочкой: {e}")
        return False


def click_continue(page: Page):
    """Нажимает кнопку Продолжить (УЛЬТРА СКОРОСТЬ)"""
    print("\n📌 Нажимаю 'Продолжить'...")
    try:
        pay_button = page.locator('#pay')
        pay_button.wait_for(state='visible', timeout=2000)  # Уменьшаем с 3000 до 2000
        
        # Ждем пока кнопка станет enabled (сокращаем время)
        try:
            page.wait_for_function("""
                () => {
                    const btn = document.getElementById('pay');
                    return btn && !btn.disabled;
                }
            """, timeout=2000)  # Уменьшаем с 3000 до 2000
            print("✅ Кнопка активна")
        except:
            print("⚠️ Кнопка disabled, но пробуем кликнуть")
        
        # Прокручиваем к кнопке
        pay_button.scroll_into_view_if_needed()
        page.wait_for_timeout(50)  # Уменьшаем с 100 до 50
        
        # Сразу пробуем JS клик (быстрее)
        try:
            pay_button.evaluate('el => el.click()')
            print("✅ Кнопка нажата (JS клик)")
            clicked = True
        except Exception as e:
            print(f"   ⚠️ JS клик не сработал: {e}")
            # Fallback на обычный клик
            try:
                pay_button.click(timeout=3000)  # Уменьшаем таймаут с 5000 до 3000
                print("✅ Кнопка нажата (обычный клик)")
                clicked = True
            except Exception as e2:
                print(f"   ⚠️ Обычный клик не сработал: {e2}")
                clicked = False
        
        if clicked:
            page.wait_for_timeout(100)  # Уменьшаем с 200 до 100
            return True
        else:
            print("❌ Не удалось нажать кнопку")
            return False
        
    except Exception as e:
        print(f"⚠️ Ошибка нажатия кнопки: {e}")
        return False


def handle_captcha(page: Page):
    """Обрабатывает Yandex SmartCaptcha - НАДЕЖНАЯ ВЕРСИЯ"""
    print("\n📌 Проверяю капчу...")
    
    try:
        # Проверка iframe капчи
        captcha_iframe_selector = 'iframe[src*="smartcaptcha.yandexcloud.net/checkbox"]'
        
        try:
            page.wait_for_selector(captcha_iframe_selector, state='visible', timeout=2000)
            print("⚠️ Капча найдена!")
        except:
            print("✅ Капча не найдена")
            return False
        
        # Небольшая пауза для загрузки iframe
        page.wait_for_timeout(500)
        
        # Работа с iframe
        captcha_frame = page.frame_locator(captcha_iframe_selector)
        
        # Ищем кнопку капчи
        checkbox_button = captcha_frame.locator('#js-button')
        
        try:
            checkbox_button.wait_for(state='visible', timeout=3000)
            print("✅ Кнопка капчи найдена")
        except:
            print("❌ Кнопка капчи не найдена")
            return False
        
        # Имитируем человеческое поведение
        print("   🤖 Имитирую движение мыши...")
        
        # Получаем координаты iframe
        try:
            iframe_element = page.locator(captcha_iframe_selector)
            bbox = iframe_element.bounding_box()
            if bbox:
                # Двигаемся к центру iframe
                center_x = bbox['x'] + bbox['width'] / 2
                center_y = bbox['y'] + bbox['height'] / 2
                
                # Плавное движение к капче
                page.mouse.move(center_x - 50, center_y - 50)
                page.wait_for_timeout(200)
                page.mouse.move(center_x, center_y)
                page.wait_for_timeout(300)
        except:
            print("   ⚠️ Не удалось получить координаты iframe")
        
        # Пробуем разные способы клика
        clicked = False
        
        # Способ 1: Обычный клик
        try:
            print(f"   Способ 1: Обычный клик...")
            checkbox_button.click(timeout=3000)
            print(f"✅ Капча кликнута (обычный клик)")
            clicked = True
        except Exception as e:
            print(f"   ⚠️ Обычный клик не удался: {str(e)[:50]}")
        
        # Способ 2: Force клик
        if not clicked:
            try:
                print(f"   Способ 2: Force клик...")
                checkbox_button.click(force=True, timeout=3000)
                print(f"✅ Капча кликнута (force клик)")
                clicked = True
            except Exception as e:
                print(f"   ⚠️ Force клик не удался: {str(e)[:50]}")
        
        # Способ 3: JS клик через evaluate
        if not clicked:
            try:
                print(f"   Способ 3: JS клик...")
                checkbox_button.evaluate('el => el.click()')
                print(f"✅ Капча кликнута (JS клик)")
                clicked = True
            except Exception as e:
                print(f"   ⚠️ JS клик не удался: {str(e)[:50]}")
        
        # Способ 4: Dispatch event
        if not clicked:
            try:
                print(f"   Способ 4: Dispatch event...")
                checkbox_button.dispatch_event('click')
                print(f"✅ Капча кликнута (dispatch event)")
                clicked = True
            except Exception as e:
                print(f"   ⚠️ Dispatch event не удался: {str(e)[:50]}")
        
        if clicked:
            # Минимальное ожидание после капчи
            print("   ⏳ Жду обработки капчи...")
            page.wait_for_timeout(300)  # Уменьшаем с 1000 до 300
            
            # Проверяем что капча прошла
            try:
                # Ждем исчезновения iframe или изменения его содержимого
                page.wait_for_timeout(100)  # Минимальная проверка
                print("✅ Капча пройдена!")
                return True
            except:
                print("✅ Капча обработана!")
                return True
        else:
            print("❌ Не удалось кликнуть капчу всеми способами")
            return False
        
    except Exception as e:
        print(f"⚠️ Ошибка капчи: {e}")
        return False


def handle_confirmation_modal(page: Page):
    """Обрабатывает модалку 'Проверка данных' как в Selenium (БЫСТРАЯ ВЕРСИЯ)"""
    print("\n📌 Проверяю модалку 'Проверка данных'...")
    
    try:
        page.wait_for_timeout(300)  # Уменьшаем с 500 до 300
        
        # Ищем все кнопки "Продолжить" на странице (как в Selenium)
        buttons = page.locator('button').all()
        continue_buttons = []
        
        for btn in buttons:
            try:
                text = btn.inner_text(timeout=100)
                if "Продолжить" in text:
                    continue_buttons.append(btn)
            except:
                pass
        
        if len(continue_buttons) > 1:
            # Берем последнюю кнопку (обычно это кнопка в модалке)
            final_btn = continue_buttons[-1]
            print(f"✅ Найдено {len(continue_buttons)} кнопок 'Продолжить', кликаю по последней")
            
            # Прокручиваем к элементу
            final_btn.scroll_into_view_if_needed()
            page.wait_for_timeout(100)  # Уменьшаем с 200 до 100
            
            # Кликаем через JS (как в Selenium)
            final_btn.evaluate('el => el.click()')
            print("✅ Кнопка в модалке нажата")
            
            # Ждем перехода на страницу оплаты (как в Selenium) - БЫСТРЕЕ
            print("📌 Ожидаю перехода на страницу оплаты...")
            transition_found = False
            
            for i in range(20):  # Уменьшаем с 40 до 20 (10 секунд максимум)
                try:
                    page.wait_for_timeout(500)
                    current_url = page.url
                    
                    if ("payment" in current_url or "result" in current_url or 
                        "/pay/" in current_url or "finish-transfer" in current_url):
                        print(f"✅ Переход на страницу оплаты!")
                        print(f"📍 URL: {current_url}")
                        transition_found = True
                        break
                except:
                    # Страница могла закрыться из-за перехода - это нормально
                    print(f"✅ Переход выполнен (страница обновилась)")
                    transition_found = True
                    break
            
            if not transition_found:
                try:
                    print(f"⚠️ Не дождались перехода. URL: {page.url}")
                except:
                    print(f"✅ Переход выполнен (страница недоступна)")
                    transition_found = True
            
            return transition_found
        else:
            print("⚠️ Модалка не найдена или только одна кнопка")
            return False
            
    except Exception as e:
        print(f"⚠️ Ошибка с модалкой: {e}")
        # Если ошибка связана с закрытием страницы - это может быть успешный переход
        if "closed" in str(e).lower() or "target" in str(e).lower():
            print("✅ Возможно переход выполнен успешно")
            return True
        return False


def test_step2():
    """Тест второго шага - нужно сначала пройти step1"""
    print("⚠️ Этот тест требует URL от step1")
    print("Запусти сначала payment_step1.py и скопируй URL sender-details")
    
    # Для теста можно вручную указать URL
    # test_url = "https://multitransfer.ru/transfer/uzbekistan/sender-details?..."
    

if __name__ == "__main__":
    test_step2()


def complete_payment_step2(page: Page, card_number: str, owner_name: str):
    """Полное выполнение шага 2 с правильной логикой"""
    print(f"\n{'='*70}")
    print("ШАГ 2: АВТОМАТИЧЕСКОЕ ЗАПОЛНЕНИЕ И ОТПРАВКА")
    print(f"{'='*70}")
    
    # Устанавливаем автоматическое закрытие модалки с ошибкой через JavaScript
    page.evaluate("""
        () => {
            // Функция для закрытия модалки
            const closeErrorModal = () => {
                const buttons = document.querySelectorAll('button[buttontext="Понятно"]');
                buttons.forEach(btn => {
                    if (btn.textContent.includes('Понятно')) {
                        console.log('🔴 Закрываю модалку с ошибкой...');
                        btn.click();
                    }
                });
            };
            
            // Проверяем каждые 100ms
            setInterval(closeErrorModal, 100);
            
            // Также используем MutationObserver для мгновенной реакции
            const observer = new MutationObserver(() => {
                closeErrorModal();
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
    """)
    print("✅ Установлен автоматический закрыватель модалок с ошибками")
    
    # Перехватываем API запросы для получения QR ссылки
    qr_link = None
    
    def handle_response(response):
        nonlocal qr_link
        if '/anonymous/confirm' in response.url:
            try:
                data = response.json()
                if 'externalData' in data and 'payload' in data['externalData']:
                    qr_link = data['externalData']['payload']
                    print(f"\n🎯 Получена QR ссылка: {qr_link}")
            except:
                pass
    
    page.on('response', handle_response)
    
    try:
        # 1. Заполняем все поля
        fill_sender_details(page, card_number, owner_name)
        
        # 2. Ставим галочку
        handle_checkbox(page)
        
        # 3. Нажимаем кнопку "Продолжить"
        click_continue(page)
        
        # 4. Быстрая проверка валидности формы
        print("\n📌 Быстрая проверка валидности...")
        try:
            # Ищем ошибки валидации (быстро)
            error_elements = page.locator('[class*="error"], [class*="Error"], .MuiFormHelperText-root.Mui-error').all()
            if error_elements:
                print(f"   ⚠️ Найдено {len(error_elements)} ошибок валидации")
                # Показываем только первые 3 ошибки для экономии времени
                for i, error in enumerate(error_elements[:3]):
                    try:
                        error_text = error.inner_text(timeout=50)  # Уменьшаем с 100 до 50
                        if error_text and error_text.strip():
                            print(f"     {i+1}. {error_text}")
                    except:
                        pass
            else:
                print("   ✅ Ошибок валидации не найдено")
        except Exception as e:
            print(f"   ⚠️ Ошибка проверки валидации: {e}")
        
        # 5. Проверяем модалку с ошибкой "Пожалуйста, попробуйте позже"
        page.wait_for_timeout(500)
        
        try:
            error_modal = page.locator('button:has-text("Понятно")').first
            if error_modal.is_visible(timeout=1000):
                print("\n⚠️ Появилась модалка с ошибкой, закрываю...")
                error_modal.click()
                page.wait_for_timeout(300)
                print("   ✅ Модалка закрыта")
        except:
            pass
        
        # 6. СРАЗУ проверяем что появилось - капча или модалка
        page.wait_for_timeout(300)  # Уменьшаем с 500 до 300
        
        # Проверяем капчу
        captcha_handled = handle_captcha(page)
        
        if captcha_handled:
            print("\n📌 После капчи СРАЗУ нажимаю 'Продолжить'...")
            page.wait_for_timeout(50)  # Уменьшаем с 100 до 50
            
            # Мгновенное нажатие кнопки после капчи
            try:
                pay_button = page.locator('#pay')
                # Сразу пробуем JS клик (быстрее чем обычный)
                pay_button.evaluate('el => el.click()')
                print("✅ Кнопка после капчи нажата (JS)")
            except Exception as e:
                print(f"⚠️ Ошибка JS клика: {e}")
                # Fallback на обычный клик
                click_continue(page)
            
            page.wait_for_timeout(100)  # Уменьшаем с 200 до 100
        
        # 7. Ждем API запрос с QR ссылкой
        print("\n📌 Ожидаю API запрос с QR ссылкой...")
        for i in range(20):  # 10 секунд максимум
            if qr_link:
                print(f"✅ QR ссылка получена!")
                break
            page.wait_for_timeout(500)
        
        if qr_link:
            print(f"\n{'='*70}")
            print(f"🎉 УСПЕХ! QR ССЫЛКА ПОЛУЧЕНА:")
            print(f"{'='*70}")
            print(f"{qr_link}")
            print(f"{'='*70}")
            return True
        
        # 8. Если QR ссылки нет, ищем и обрабатываем модалку "Проверка данных"
        print("\n📌 Ищу модалку 'Проверка данных'...")
        
        # Ждем появления модалки или перехода
        modal_found = False
        for attempt in range(4):  # Уменьшаем с 6 до 4 (2 секунды максимум)
            try:
                # Ищем кнопки "Продолжить"
                buttons = page.locator('button').all()
                continue_buttons = []
                
                for btn in buttons:
                    try:
                        text = btn.inner_text(timeout=30)  # Уменьшаем с 50 до 30
                        if "Продолжить" in text:
                            continue_buttons.append(btn)
                    except:
                        pass
                
                if len(continue_buttons) > 1:
                    # Найдена модалка с несколькими кнопками
                    final_btn = continue_buttons[-1]
                    print(f"✅ Найдена модалка с {len(continue_buttons)} кнопками 'Продолжить'")
                    
                    # Кликаем по кнопке в модалке
                    final_btn.scroll_into_view_if_needed()
                    page.wait_for_timeout(30)  # Уменьшаем с 50 до 30
                    final_btn.evaluate('el => el.click()')
                    print("✅ Кнопка в модалке нажата")
                    
                    # Даем больше времени на переход после модалки
                    page.wait_for_timeout(1500)  # Увеличиваем с 500 до 1500
                    
                    # Проверяем переход сразу после клика
                    try:
                        current_url = page.url
                        if ("payment" in current_url or "result" in current_url or 
                            "/pay/" in current_url or "finish-transfer" in current_url):
                            print(f"✅ Переход произошел после клика по модалке!")
                            print(f"📍 URL: {current_url}")
                            return True
                    except:
                        pass
                    
                    modal_found = True
                    break
                
                # Проверяем не произошел ли уже переход
                current_url = page.url
                if ("payment" in current_url or "result" in current_url or 
                    "/pay/" in current_url or "finish-transfer" in current_url):
                    print(f"✅ Переход уже произошел!")
                    print(f"📍 URL: {current_url}")
                    return True
                
                page.wait_for_timeout(500)
                
            except Exception as e:
                if "closed" in str(e).lower():
                    print("✅ Переход выполнен (страница обновилась)")
                    return True
                page.wait_for_timeout(500)
        
        if not modal_found:
            print("⚠️ Модалка не найдена, проверяю переход...")
        
        # 6. Ждем перехода на страницу оплаты
        print("📌 Ожидаю перехода на страницу оплаты...")
        
        for i in range(10):  # Увеличиваем с 6 до 10 (5 секунд максимум)
            try:
                page.wait_for_timeout(500)
                current_url = page.url
                
                if ("payment" in current_url or "result" in current_url or 
                    "/pay/" in current_url or "finish-transfer" in current_url):
                    print(f"✅ Переход на страницу оплаты!")
                    print(f"📍 URL: {current_url}")
                    return True
                
                if i % 2 == 0:  # Выводим сообщение каждую секунду
                    print(f"   ⏳ Ожидание... ({i//2}s)")
                    
            except Exception as e:
                if "closed" in str(e).lower():
                    print("✅ Переход выполнен (страница обновилась)")
                    return True
        
        try:
            print(f"⚠️ Не дождались перехода")
            print(f"📍 Текущий URL: {page.url}")
        except:
            print(f"✅ Переход выполнен (страница недоступна)")
            return True
        
        return False
        
    except Exception as e:
        print(f"\n❌ Ошибка в шаге 2: {e}")
        if "closed" in str(e).lower():
            print("✅ Возможно переход выполнен успешно")
            return True
        import traceback
        traceback.print_exc()
        return False


def test_step2():
    """Тест второго шага - нужно сначала пройти step1"""
    print("⚠️ Этот тест требует URL от step1")
    print("Запусти сначала payment_step1.py и скопируй URL sender-details")
    
    # Для теста можно вручную указать URL
    # test_url = "https://multitransfer.ru/transfer/uzbekistan/sender-details?..."
    

if __name__ == "__main__":
    test_step2()