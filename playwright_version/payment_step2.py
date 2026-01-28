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
    "birth_date": "03.07.2000",
    "phone": "+79880260334",
    "registration_country": "Россия",
    "registration_place": "камышин"
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
    """Заполняет все поля с триггером React событий"""
    
    print("📌 Заполняю данные с триггером событий...")
    start_time = time.time()
    
    # Ждем загрузки формы
    page.wait_for_selector('input', state='visible', timeout=10000)
    page.wait_for_timeout(300)
    
    print(f"\n🚀 Заполняю все поля...")
    
    # owner_name уже на латинице в формате "Имя Фамилия"
    fields = [
        ('input[name="beneficiary_firstName"]', owner_name.split()[0] if owner_name else "", "Имя получателя"),
        ('input[name="beneficiary_lastName"]', owner_name.split()[1] if len(owner_name.split()) > 1 else "", "Фамилия получателя"),
        ('input[name="sender_documents_series"]', SENDER_DATA["passport_series"], "Серия паспорта"),
        ('input[name="sender_documents_number"]', SENDER_DATA["passport_number"], "Номер паспорта"),
        ('input[name="issueDate"]', SENDER_DATA["passport_issue_date"], "Дата выдачи"),
        ('input[name="birthPlaceAddress_full"]', SENDER_DATA["birth_place"], "Место рождения"),
        ('input[name="registrationAddress_full"]', SENDER_DATA["registration_place"], "Место регистрации"),
        ('input[name="sender_firstName"]', SENDER_DATA["first_name"], "Имя отправителя"),
        ('input[name="sender_lastName"]', SENDER_DATA["last_name"], "Фамилия отправителя"),
        ('input[name="birthDate"]', SENDER_DATA["birth_date"], "Дата рождения"),
        ('input[name="phoneNumber"]', SENDER_DATA["phone"], "Телефон"),
        ('input[name="transfer_beneficiaryAccountNumber"]', card_number, "Номер карты"),  # В КОНЦЕ!
    ]
    
    # Заполняем каждое поле с триггером React событий
    for selector, value, label in fields:
        try:
            input_field = page.locator(selector).first
            
            # Кликаем в поле
            input_field.click()
            page.wait_for_timeout(50)
            
            # Очищаем
            input_field.fill('')
            page.wait_for_timeout(30)
            
            # Вводим посимвольно для триггера React
            input_field.type(value, delay=20)
            
            # Tab для blur и подтверждения
            page.keyboard.press('Tab')
            page.wait_for_timeout(50)
            
            print(f"   ✅ {label}: {value}")
        except Exception as e:
            print(f"   ⚠️ {label}: {str(e)[:50]}")
    
    # Заполняем автокомплиты (страны) отдельно
    print(f"\n🌍 Заполняю автокомплиты...")
    
    # Страна рождения
    try:
        birth_country_input = page.locator('input[name="birthPlaceAddress_countryCode"]').first
        birth_country_input.click()
        page.wait_for_timeout(100)
        birth_country_input.fill(SENDER_DATA["birth_country"])
        page.wait_for_timeout(300)
        page.locator('li[role="option"]').first.click()
        print(f"   ✅ Страна рождения: {SENDER_DATA['birth_country']}")
    except:
        print(f"   ⚠️ Страна рождения: не удалось")
    
    # Страна регистрации
    try:
        reg_country_input = page.locator('input[name="registrationAddress_countryCode"]').first
        reg_country_input.click()
        page.wait_for_timeout(100)
        reg_country_input.fill(SENDER_DATA["registration_country"])
        page.wait_for_timeout(300)
        page.locator('li[role="option"]').first.click()
        print(f"   ✅ Страна регистрации: {SENDER_DATA['registration_country']}")
    except:
        print(f"   ⚠️ Страна регистрации: не удалось")
    
    elapsed = time.time() - start_time
    print(f"\n✅ Заполнение завершено за {elapsed:.1f}s")
    
    return True


def handle_checkbox(page: Page):
    """Ставит галочку согласия"""
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
    """Нажимает кнопку Продолжить"""
    print("\n📌 Нажимаю 'Продолжить'...")
    try:
        pay_button = page.locator('#pay')
        pay_button.wait_for(state='visible', timeout=5000)
        
        # Ждем пока кнопка станет enabled
        try:
            page.wait_for_function("""
                () => {
                    const btn = document.getElementById('pay');
                    return btn && !btn.disabled;
                }
            """, timeout=5000)
            print("✅ Кнопка активна")
        except:
            print("⚠️ Кнопка disabled, но пробуем кликнуть")
        
        # Кликаем через JS
        pay_button.evaluate('el => el.click()')
        
        print("✅ Кнопка нажата")
        page.wait_for_timeout(500)
        
        return True
    except Exception as e:
        print(f"⚠️ Ошибка нажатия кнопки: {e}")
        return False


def handle_captcha(page: Page):
    """Обрабатывает Yandex SmartCaptcha если появилась"""
    print("\n📌 Проверяю наличие капчи...")
    
    try:
        # Ждем iframe капчи
        captcha_iframe = page.frame_locator('iframe[src*="smartcaptcha.yandexcloud.net/checkbox"]')
        
        # Проверяем что iframe существует
        checkbox = captcha_iframe.locator('#js-button')
        checkbox.wait_for(state='visible', timeout=3000)
        
        print("⚠️ Обнаружена Yandex SmartCaptcha!")
        
        # Кликаем по чекбоксу
        page.wait_for_timeout(500)
        checkbox.click()
        print("✅ Кликнул по чекбоксу капчи")
        
        # Ждем обработки
        page.wait_for_timeout(1500)
        
        print("✅ Капча пройдена!")
        return True
        
    except:
        print("✅ Капча не обнаружена")
        return False


def handle_confirmation_modal(page: Page):
    """Обрабатывает модалку 'Проверка данных'"""
    print("\n📌 Проверяю модалку 'Проверка данных'...")
    
    try:
        page.wait_for_timeout(500)
        
        # Ищем все кнопки "Продолжить"
        buttons = page.locator('button:has-text("Продолжить")').all()
        
        if len(buttons) > 1:
            # Берем последнюю (в модалке)
            final_btn = buttons[-1]
            print(f"✅ Найдено {len(buttons)} кнопок, кликаю по последней")
            
            final_btn.scroll_into_view_if_needed()
            page.wait_for_timeout(200)
            
            final_btn.evaluate('el => el.click()')
            print("✅ Кнопка в модалке нажата")
            
            return True
        else:
            print("⚠️ Модалка не найдена")
            return False
            
    except Exception as e:
        print(f"⚠️ Ошибка с модалкой: {e}")
        return False


def test_step2():
    """Тест второго шага - нужно сначала пройти step1"""
    print("⚠️ Этот тест требует URL от step1")
    print("Запусти сначала payment_step1.py и скопируй URL sender-details")
    
    # Для теста можно вручную указать URL
    # test_url = "https://multitransfer.ru/transfer/uzbekistan/sender-details?..."
    

if __name__ == "__main__":
    test_step2()
