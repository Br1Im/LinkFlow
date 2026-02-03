#!/usr/bin/env python3
"""
Отладочный скрипт для пошагового заполнения полей
Показывает детальную информацию о каждом поле
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from playwright.async_api import async_playwright
from src.sender_data import SENDER_DATA


async def debug_field(page, field_name, field_value, label="Поле"):
    """Отладка заполнения одного поля"""
    print(f"\n{'='*60}")
    print(f"🔍 Проверка: {label}")
    print(f"{'='*60}")
    print(f"Имя поля: {field_name}")
    print(f"Значение: {field_value}")
    print()
    
    try:
        # Ищем поле
        field = page.locator(f'input[name="{field_name}"]').first
        
        # Проверяем существование
        count = await field.count()
        if count == 0:
            print("❌ Поле не найдено на странице")
            return False
        
        print(f"✅ Поле найдено (count={count})")
        
        # Получаем атрибуты
        placeholder = await field.get_attribute('placeholder')
        field_type = await field.get_attribute('type')
        required = await field.get_attribute('required')
        aria_invalid = await field.get_attribute('aria-invalid')
        
        print(f"   Placeholder: {placeholder}")
        print(f"   Type: {field_type}")
        print(f"   Required: {required}")
        print(f"   Aria-invalid: {aria_invalid}")
        
        # Текущее значение
        current_value = await field.input_value()
        print(f"   Текущее значение: '{current_value}'")
        
        # Пробуем заполнить
        print(f"\n⏳ Заполняю поле...")
        await field.click()
        await page.wait_for_timeout(100)
        
        # Очищаем
        await field.fill('')
        await page.wait_for_timeout(50)
        
        # Вводим значение
        if field_value:
            await field.type(str(field_value), delay=20)
            await page.wait_for_timeout(200)
        
        # Убираем фокус
        await field.blur()
        await page.wait_for_timeout(300)
        
        # Проверяем результат
        new_value = await field.input_value()
        print(f"✅ Новое значение: '{new_value}'")
        
        # Проверяем ошибку
        error_info = await field.evaluate("""
            (element) => {
                const parent = element.closest('div');
                if (!parent) return null;
                
                // Ищем текст ошибки
                const errorText = parent.querySelector('p.Mui-error, p[class*="error"], p[id*="error"]');
                if (errorText) {
                    return {
                        hasError: true,
                        errorText: errorText.textContent,
                        errorClass: errorText.className
                    };
                }
                
                // Проверяем красную границу
                const styles = window.getComputedStyle(element);
                const borderColor = styles.borderColor;
                const hasRedBorder = borderColor.includes('rgb(244, 67, 54)') || 
                                   borderColor.includes('rgb(211, 47, 47)') ||
                                   borderColor.includes('rgb(233, 53, 68)');
                
                return {
                    hasError: hasRedBorder,
                    errorText: hasRedBorder ? 'Красная граница' : null,
                    borderColor: borderColor
                };
            }
        """)
        
        if error_info and error_info.get('hasError'):
            print(f"❌ ОШИБКА ВАЛИДАЦИИ: {error_info.get('errorText')}")
            if error_info.get('borderColor'):
                print(f"   Border color: {error_info.get('borderColor')}")
            return False
        else:
            print(f"✅ Валидация пройдена")
            return True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Главная функция"""
    print("\n" + "="*60)
    print("🐛 ОТЛАДКА ЗАПОЛНЕНИЯ ПОЛЕЙ")
    print("="*60)
    print()
    
    # Запуск браузера
    print("🚀 Запуск браузера (визуальный режим)...")
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    print("✅ Браузер запущен\n")
    
    try:
        # Открываем страницу
        print("📄 Открываю страницу...")
        await page.goto('https://multitransfer.ru/transfer/uzbekistan')
        await page.wait_for_load_state('networkidle')
        print("✅ Страница загружена\n")
        
        # Вводим сумму
        print("💰 Ввожу сумму...")
        amount_input = page.locator('input[name="amount"]').first
        await amount_input.click()
        await amount_input.fill('1000')
        await page.wait_for_timeout(1000)
        print("✅ Сумма введена\n")
        
        # Выбираем Uzcard
        print("💳 Выбираю Uzcard...")
        await page.locator('text=Uzcard').first.click()
        await page.wait_for_timeout(500)
        print("✅ Uzcard выбран\n")
        
        # Нажимаем Продолжить
        print("➡️  Нажимаю Продолжить...")
        continue_button = page.locator('button:has-text("Продолжить")').first
        await continue_button.click()
        await page.wait_for_timeout(2000)
        print("✅ Переход на страницу заполнения\n")
        
        # Список полей для проверки
        fields_to_test = [
            # Получатель
            ('transfer_beneficiaryAccountNumber', '9860606753188378', 'Номер карты получателя'),
            ('beneficiary_firstName', 'ASIYA', 'Имя получателя'),
            ('beneficiary_lastName', 'Asadullayev', 'Фамилия получателя'),
            
            # Отправитель
            ('sender_firstName', SENDER_DATA.get('first_name', 'Дмитрий'), 'Имя отправителя'),
            ('sender_lastName', SENDER_DATA.get('last_name', 'Непокрытый'), 'Фамилия отправителя'),
            ('sender_middleName', SENDER_DATA.get('middle_name', 'Александрович'), 'Отчество отправителя'),
            ('sender_birthDate', SENDER_DATA.get('birth_date', '2000-07-03'), 'Дата рождения'),
            ('sender_birthPlace', SENDER_DATA.get('birth_place', 'камышин'), 'Место рождения'),
            
            # Документы
            ('sender_documents_0_series', SENDER_DATA.get('passport_series', '1820'), 'Серия паспорта'),
            ('sender_documents_0_number', SENDER_DATA.get('passport_number', '657875'), 'Номер паспорта'),
            ('sender_documents_0_issueDate', SENDER_DATA.get('passport_issue_date', '2020-07-22'), 'Дата выдачи'),
            
            # Контакты
            ('sender_phone', SENDER_DATA.get('phone', '+79880260334'), 'Телефон'),
        ]
        
        results = []
        
        # Проверяем каждое поле
        for field_name, field_value, label in fields_to_test:
            success = await debug_field(page, field_name, field_value, label)
            results.append({
                'field': label,
                'name': field_name,
                'value': field_value,
                'success': success
            })
            
            # Небольшая пауза между полями
            await page.wait_for_timeout(500)
        
        # Итоги
        print("\n" + "="*60)
        print("📊 ИТОГИ ОТЛАДКИ")
        print("="*60)
        print()
        
        success_count = sum(1 for r in results if r['success'])
        fail_count = len(results) - success_count
        
        print(f"✅ Успешно заполнено: {success_count}/{len(results)}")
        print(f"❌ Ошибок: {fail_count}/{len(results)}")
        print()
        
        if fail_count > 0:
            print("❌ ПОЛЯ С ОШИБКАМИ:")
            for r in results:
                if not r['success']:
                    print(f"  - {r['field']} ({r['name']})")
            print()
        
        # Сохраняем скриншот
        from datetime import datetime
        timestamp = int(datetime.now().timestamp())
        screenshot_path = f'screenshots/debug_{timestamp}.png'
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"📸 Скриншот сохранен: {screenshot_path}")
        
        # Ждем чтобы посмотреть
        print("\n⏳ Ожидание 10 секунд (можно посмотреть форму)...")
        await page.wait_for_timeout(10000)
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await browser.close()
        print("\n✅ Браузер закрыт")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Отладка прервана пользователем")
        sys.exit(130)
