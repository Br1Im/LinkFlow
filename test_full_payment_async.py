#!/usr/bin/env python3
"""
Полный тест - оба этапа с АСИНХРОННЫМ заполнением полей
"""

from playwright.async_api import async_playwright
import asyncio
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'playwright_version'))


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


async def fill_field_async(page, pattern: str, value: str, field_name: str):
    """Асинхронное заполнение поля"""
    try:
        inputs = await page.locator('input').all()
        
        for inp in inputs:
            name_attr = await inp.get_attribute('name') or ""
            placeholder = await inp.get_attribute('placeholder') or ""
            
            if pattern.lower() in name_attr.lower() or pattern.lower() in placeholder.lower():
                print(f"   🎯 {field_name}")
                
                # Используем JavaScript для быстрой установки
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
                
                print(f"   ✅ {field_name}")
                return True
        
        print(f"   ⚠️ {field_name}: не найдено")
        return False
    except Exception as e:
        print(f"   ⚠️ {field_name}: ошибка - {e}")
        return False


async def select_country_async(page, pattern: str, country: str, field_name: str):
    """Асинхронный выбор страны из автокомплита"""
    try:
        inputs = await page.locator('input').all()
        
        for inp in inputs:
            name_attr = await inp.get_attribute('name') or ""
            if pattern in name_attr:
                print(f"   🎯 {field_name}")
                
                # Кликаем и вводим
                await inp.click()
                await page.wait_for_timeout(50)
                await inp.fill(country)
                await page.wait_for_timeout(100)
                
                # Ждем появления опций
                try:
                    await page.wait_for_selector('li[role="option"]', state='visible', timeout=800)
                    await page.locator('li[role="option"]').first.click()
                    print(f"   ✅ {field_name}")
                    return True
                except:
                    # Если опции не появились, жмем Enter
                    await page.keyboard.press('Enter')
                    await page.wait_for_timeout(30)
                    print(f"   ✅ {field_name} (Enter)")
                    return True
        
        print(f"   ⚠️ {field_name}: не найдено")
        return False
    except Exception as e:
        print(f"   ⚠️ {field_name}: ошибка - {e}")
        return False


async def fill_all_fields_parallel(page, card_number: str, owner_name: str):
    """Заполняет ВСЕ поля параллельно - МАКСИМАЛЬНАЯ СКОРОСТЬ"""
    print("🚀 Заполняю ВСЕ поля ПАРАЛЛЕЛЬНО...")
    start = time.time()
    
    # Ждем загрузки формы
    await page.wait_for_selector('input', state='visible', timeout=10000)
    await page.wait_for_timeout(500)  # Даем время на полную загрузку React
    
    # Разбиваем имя владельца
    owner_parts = owner_name.split()
    first_name = owner_parts[0] if len(owner_parts) > 0 else ""
    last_name = owner_parts[1] if len(owner_parts) > 1 else ""
    
    # Запускаем заполнение ТЕКСТОВЫХ полей ПАРАЛЛЕЛЬНО
    await asyncio.gather(
        # Получатель - используем правильные селекторы
        fill_field_async(page, "transfer_beneficiaryaccountnumber", card_number, "Номер карты"),
        fill_field_async(page, "transfer_beneficiary_firstname", first_name, "Имя получателя"),
        fill_field_async(page, "transfer_beneficiary_lastname", last_name, "Фамилия получателя"),
        fill_field_async(page, "beneficiary_firstname", first_name, "Имя получателя 2"),
        fill_field_async(page, "beneficiary_lastname", last_name, "Фамилия получателя 2"),
        
        # Паспорт
        fill_field_async(page, "sender_documents_series", SENDER_DATA["passport_series"], "Серия паспорта"),
        fill_field_async(page, "sender_documents_number", SENDER_DATA["passport_number"], "Номер паспорта"),
        fill_field_async(page, "issuedate", SENDER_DATA["passport_issue_date"], "Дата выдачи"),
        
        # Отправитель
        fill_field_async(page, "sender_middlename", SENDER_DATA["middle_name"], "Отчество"),
        fill_field_async(page, "sender_firstname", SENDER_DATA["first_name"], "Имя отправителя"),
        fill_field_async(page, "sender_lastname", SENDER_DATA["last_name"], "Фамилия отправителя"),
        fill_field_async(page, "birthdate", SENDER_DATA["birth_date"], "Дата рождения"),
        fill_field_async(page, "phonenumber", SENDER_DATA["phone"], "Телефон"),
        
        # Места
        fill_field_async(page, "birthPlaceAddress_full", SENDER_DATA["birth_place"], "Место рождения"),
        fill_field_async(page, "registrationAddress_full", SENDER_DATA["registration_place"], "Место регистрации"),
    )
    
    # Страны заполняем ПОСЛЕДОВАТЕЛЬНО (автокомплит не работает параллельно)
    print("\n🌍 Заполняю страны...")
    await select_country_async(page, "birthPlaceAddress_countryCode", SENDER_DATA["birth_country"], "Страна рождения")
    await select_country_async(page, "registrationAddress_countryCode", SENDER_DATA["registration_country"], "Страна регистрации")
    
    elapsed = time.time() - start
    print(f"\n✅ ВСЕ поля заполнены за {elapsed:.2f}s!")
    return True


async def test_full_payment_async():
    """Полный асинхронный тест"""
    start_time = time.time()
    amount = 110
    card_number = "9860080323894719"
    owner_name = "Nodir Asadullayev"
    
    print(f"🚀 ПОЛНЫЙ ASYNC ТЕСТ: ОБА ЭТАПА")
    print("="*70)
    print(f"💰 Сумма: {amount} RUB")
    print(f"💳 Карта: {card_number}")
    print(f"👤 Владелец: {owner_name}")
    print("="*70)
    
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
        
        # QR ссылка
        qr_link = None
        
        async def handle_response(response):
            nonlocal qr_link
            if '/anonymous/confirm' in response.url:
                try:
                    data = await response.json()
                    if 'externalData' in data and 'payload' in data['externalData']:
                        qr_link = data['externalData']['payload']
                        print(f"\n🎯 QR ссылка получена!")
                except:
                    pass
        
        page.on('response', handle_response)
        
        try:
            # Автозакрыватель модалок
            await page.evaluate("""
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
            
            # ЭТАП 1 - СТАБИЛЬНАЯ ВЕРСИЯ
            print(f"\n{'='*70}")
            print("ЭТАП 1: ВВОД СУММЫ")
            print(f"{'='*70}")
            
            await page.goto("https://multitransfer.ru/transfer/uzbekistan", wait_until='domcontentloaded')
            
            # Ждем поле
            amount_input = page.locator('input[placeholder="0 RUB"]')
            await amount_input.wait_for(state='visible', timeout=5000)
            
            # Ввод суммы с retry
            commission_ok = False
            for attempt in range(5):
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
                    await page.wait_for_timeout(50)
                
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(300)
                
                # Проверяем комиссию
                try:
                    await page.wait_for_function("""
                        () => {
                            const input = document.querySelector('input[placeholder*="UZS"]');
                            return input && input.value && input.value !== '0 UZS' && input.value !== '';
                        }
                    """, timeout=3000)
                    print("✅ Комиссия")
                    commission_ok = True
                    break
                except:
                    if attempt < 4:
                        await page.wait_for_timeout(500)
            
            if not commission_ok:
                raise Exception("Не удалось рассчитать комиссию за 5 попыток")
            
            # Выбор способа платежа
            transfer_selectors = [
                'div.css-c8d8yl:has-text("Способ перевода")',
                'div:has-text("Способ перевода")',
            ]
            
            for selector in transfer_selectors:
                try:
                    transfer_block = page.locator(selector).first
                    if await transfer_block.is_visible(timeout=300):
                        await transfer_block.click()
                        print("✅ Способ платежа")
                        break
                except:
                    continue
            
            await page.wait_for_timeout(300)
            
            # Выбор Uzcard
            bank_selectors = [
                'text=Uzcard',
                '[role="button"]:has-text("Uzcard")',
            ]
            
            for selector in bank_selectors:
                try:
                    bank_option = page.locator(selector).first
                    await bank_option.wait_for(state='visible', timeout=2000)
                    await bank_option.click()
                    print("✅ Uzcard")
                    break
                except:
                    continue
            
            # Ждем активации кнопки
            await page.wait_for_timeout(1000)
            
            try:
                await page.wait_for_function("""
                    () => {
                        const btn = document.getElementById('pay');
                        return btn && !btn.disabled;
                    }
                """, timeout=10000)
            except:
                # Повторный клик по Uzcard
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
            
            await page.locator('#pay').evaluate('el => el.click()')
            await page.wait_for_url('**/sender-details**', timeout=10000)
            print("✅ Переход")
            
            step1_time = time.time() - start_time
            
            # ЭТАП 2
            print(f"\n{'='*70}")
            print("ЭТАП 2: ПАРАЛЛЕЛЬНОЕ ЗАПОЛНЕНИЕ")
            print(f"{'='*70}")
            
            step2_start = time.time()
            
            # ПАРАЛЛЕЛЬНОЕ заполнение всех полей
            await fill_all_fields_parallel(page, card_number, owner_name)
            
            # Галочка
            try:
                checkbox = page.locator('input[type="checkbox"]').first
                if not await checkbox.is_checked():
                    await checkbox.click(force=True)
                print("✅ Галочка")
            except Exception as e:
                print(f"⚠️ Галочка: {e}")
            
            # Кнопка "Продолжить"
            print("📌 Нажимаю 'Продолжить'...")
            try:
                await page.locator('#pay').evaluate('el => el.click()')
                print("✅ Кнопка нажата")
            except Exception as e:
                print(f"⚠️ Кнопка: {e}")
            
            await page.wait_for_timeout(500)
            
            # Капча
            print("📌 Проверяю капчу...")
            try:
                captcha_frame = page.frame_locator('iframe[src*="smartcaptcha"]')
                await captcha_frame.locator('#js-button').click(timeout=3000)
                await page.wait_for_timeout(500)
                print("✅ Капча пройдена")
                
                # После капчи снова жмем кнопку
                await page.locator('#pay').evaluate('el => el.click()')
                print("✅ Кнопка после капчи")
            except Exception as e:
                print(f"⚠️ Капча не найдена или ошибка: {str(e)[:50]}")
            
            await page.wait_for_timeout(1000)
            
            # Модалка подтверждения
            print("📌 Ищу модалку подтверждения...")
            try:
                buttons = await page.locator('button').all()
                continue_buttons = []
                
                for btn in buttons:
                    try:
                        text = await btn.inner_text(timeout=100)
                        if "Продолжить" in text:
                            continue_buttons.append(btn)
                    except:
                        pass
                
                if len(continue_buttons) > 1:
                    # Кликаем по последней кнопке (в модалке)
                    await continue_buttons[-1].evaluate('el => el.click()')
                    print(f"✅ Модалка: нажата кнопка ({len(continue_buttons)} найдено)")
                else:
                    print(f"⚠️ Модалка: найдено {len(continue_buttons)} кнопок")
            except Exception as e:
                print(f"⚠️ Модалка: {e}")
            
            # Ждем QR ссылку
            print("📌 Ожидаю QR ссылку...")
            for i in range(20):
                if qr_link:
                    print(f"✅ QR получена!")
                    break
                await page.wait_for_timeout(500)
                if i % 2 == 0:
                    print(f"   ⏳ {i//2}s...")
            
            step2_time = time.time() - step2_start
            total_time = time.time() - start_time
            
            print(f"\n{'='*70}")
            print(f"⏱️  СТАТИСТИКА:")
            print(f"{'='*70}")
            print(f"⚡ Этап 1: {step1_time:.2f}s")
            print(f"⚡ Этап 2: {step2_time:.2f}s")
            print(f"✅ ОБЩЕЕ ВРЕМЯ: {total_time:.2f}s")
            
            if qr_link:
                print(f"\n{'='*70}")
                print(f"🎉 QR ССЫЛКА:")
                print(f"{'='*70}")
                print(f"{qr_link}")
                print(f"{'='*70}")
            
            print(f"\n📍 URL: {page.url}")
            
            input("\n⏸️  Enter для закрытия...")
            await browser.close()
            
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            
            input("\n⏸️  Enter для закрытия...")
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_full_payment_async())
