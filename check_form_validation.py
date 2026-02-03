#!/usr/bin/env python3
"""
Скрипт для проверки заполнения полей формы
Выявляет проблемы с валидацией и показывает, какие поля не заполнены
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from playwright.async_api import async_playwright
from src.sender_data import SENDER_DATA


class FormValidator:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.errors = []
        self.warnings = []
        self.success = []
        
    async def start(self):
        """Запуск браузера"""
        print("🚀 Запуск браузера...")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)  # Визуальный режим
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        print("✅ Браузер запущен\n")
        
    async def stop(self):
        """Остановка браузера"""
        if self.browser:
            await self.browser.close()
            
    async def check_field_error(self, field_name, field_selector=None):
        """Проверка ошибки валидации для поля"""
        try:
            # Ищем поле
            if field_selector:
                field = self.page.locator(field_selector).first
            else:
                field = self.page.locator(f'input[name*="{field_name}"]').first
            
            if not await field.count():
                return None, "Поле не найдено"
            
            # Проверяем значение
            value = await field.input_value()
            
            # Проверяем ошибку валидации
            is_error = await field.evaluate("""
                (element) => {
                    const parent = element.closest('div');
                    if (!parent) return false;
                    
                    // Проверяем текст ошибки
                    const errorText = parent.querySelector('p.Mui-error, p[class*="error"]');
                    if (errorText && errorText.textContent) {
                        return errorText.textContent;
                    }
                    
                    // Проверяем красную границу
                    const styles = window.getComputedStyle(element);
                    const hasRedBorder = styles.borderColor.includes('rgb(244, 67, 54)') || 
                                       styles.borderColor.includes('rgb(211, 47, 47)') ||
                                       styles.borderColor.includes('rgb(233, 53, 68)');
                    
                    if (hasRedBorder) {
                        return 'Ошибка валидации (красная граница)';
                    }
                    
                    return false;
                }
            """)
            
            # Проверяем aria-invalid
            aria_invalid = await field.get_attribute('aria-invalid')
            
            return {
                'value': value,
                'error': is_error if is_error else None,
                'aria_invalid': aria_invalid == 'true',
                'filled': bool(value and len(value) > 0)
            }
            
        except Exception as e:
            return None, f"Ошибка проверки: {e}"
    
    async def get_all_errors(self):
        """Получить все ошибки на странице"""
        try:
            # Ищем блок с ошибками
            error_block = self.page.locator('.panel-danger.errors')
            if await error_block.count():
                error_items = await error_block.locator('li').all_text_contents()
                return error_items
            return []
        except:
            return []
    
    async def check_all_fields(self):
        """Проверка всех полей формы"""
        print("="*60)
        print("🔍 ПРОВЕРКА ВСЕХ ПОЛЕЙ ФОРМЫ")
        print("="*60)
        print()
        
        # Список полей для проверки
        fields_to_check = [
            # Получатель
            ('Номер карты получателя', 'transfer_beneficiaryAccountNumber'),
            ('Имя получателя', 'beneficiary_firstName'),
            ('Фамилия получателя', 'beneficiary_lastName'),
            
            # Отправитель
            ('Имя отправителя', 'sender_firstName'),
            ('Фамилия отправителя', 'sender_lastName'),
            ('Отчество отправителя', 'sender_middleName'),
            ('Дата рождения', 'sender_birthDate'),
            ('Место рождения', 'sender_birthPlace'),
            ('Страна рождения', 'sender_birthCountry'),
            
            # Документы
            ('Серия паспорта', 'sender_documents_0_series'),
            ('Номер паспорта', 'sender_documents_0_number'),
            ('Дата выдачи паспорта', 'sender_documents_0_issueDate'),
            
            # Адрес
            ('Страна регистрации', 'sender_registrationCountry'),
            ('Место регистрации', 'sender_registrationPlace'),
            
            # Контакты
            ('Телефон', 'sender_phone'),
        ]
        
        results = {}
        
        for field_label, field_name in fields_to_check:
            result, error = await self.check_field_error(field_name)
            
            if error:
                print(f"⚠️  {field_label}: {error}")
                self.warnings.append(f"{field_label}: {error}")
            elif result:
                status = "✅" if result['filled'] and not result['error'] else "❌"
                
                if result['filled'] and not result['error']:
                    print(f"{status} {field_label}: '{result['value']}'")
                    self.success.append(field_label)
                elif result['error']:
                    print(f"{status} {field_label}: ОШИБКА - {result['error']}")
                    self.errors.append(f"{field_label}: {result['error']}")
                else:
                    print(f"{status} {field_label}: НЕ ЗАПОЛНЕНО")
                    self.errors.append(f"{field_label}: не заполнено")
                
                results[field_name] = result
        
        print()
        return results
    
    async def run_full_check(self):
        """Полная проверка формы"""
        try:
            await self.start()
            
            # Шаг 1: Открываем страницу
            print("📄 Открываю страницу...")
            await self.page.goto('https://multitransfer.ru/transfer/uzbekistan')
            await self.page.wait_for_load_state('networkidle')
            print("✅ Страница загружена\n")
            
            # Шаг 2: Вводим сумму
            print("💰 Ввожу сумму 1000 RUB...")
            amount_input = self.page.locator('input[name="amount"]').first
            await amount_input.click()
            await amount_input.fill('')
            await amount_input.type('1000', delay=50)
            await self.page.wait_for_timeout(1000)
            print("✅ Сумма введена\n")
            
            # Шаг 3: Выбираем способ перевода
            print("💳 Выбираю Uzcard...")
            await self.page.locator('text=Uzcard').first.click()
            await self.page.wait_for_timeout(500)
            print("✅ Uzcard выбран\n")
            
            # Шаг 4: Нажимаем Продолжить
            print("➡️  Нажимаю Продолжить...")
            continue_button = self.page.locator('button:has-text("Продолжить")').first
            await continue_button.click()
            await self.page.wait_for_timeout(2000)
            print("✅ Переход на страницу заполнения\n")
            
            # Шаг 5: Заполняем номер карты
            print("💳 Заполняю номер карты...")
            card_input = self.page.locator('input[name="transfer_beneficiaryAccountNumber"]').first
            await card_input.click()
            await card_input.fill('')
            await card_input.type('9860080323894719', delay=20)
            await self.page.wait_for_timeout(500)
            print("✅ Номер карты заполнен\n")
            
            # Шаг 6: Заполняем имя и фамилию получателя
            print("👤 Заполняю имя получателя...")
            fname_input = self.page.locator('input[name="beneficiary_firstName"]').first
            await fname_input.click()
            await fname_input.fill('')
            await fname_input.type('Nodir', delay=20)
            await self.page.wait_for_timeout(300)
            print("✅ Имя заполнено\n")
            
            print("👤 Заполняю фамилию получателя...")
            lname_input = self.page.locator('input[name="beneficiary_lastName"]').first
            await lname_input.click()
            await lname_input.fill('')
            await lname_input.type('Asadullayev', delay=20)
            await self.page.wait_for_timeout(300)
            print("✅ Фамилия заполнена\n")
            
            # Шаг 7: Проверяем все поля
            await self.page.wait_for_timeout(1000)
            results = await self.check_all_fields()
            
            # Шаг 8: Получаем ошибки валидации
            print("="*60)
            print("🔍 ОШИБКИ ВАЛИДАЦИИ НА СТРАНИЦЕ")
            print("="*60)
            print()
            
            errors = await self.get_all_errors()
            if errors:
                for error in errors:
                    print(f"❌ {error}")
                    if error not in [e.split(': ')[1] if ': ' in e else e for e in self.errors]:
                        self.errors.append(f"Валидация: {error}")
            else:
                print("✅ Ошибок валидации не найдено")
            
            print()
            
            # Шаг 9: Итоги
            print("="*60)
            print("📊 ИТОГИ ПРОВЕРКИ")
            print("="*60)
            print()
            print(f"✅ Заполнено корректно: {len(self.success)}")
            print(f"❌ Ошибок: {len(self.errors)}")
            print(f"⚠️  Предупреждений: {len(self.warnings)}")
            print()
            
            if self.errors:
                print("❌ СПИСОК ОШИБОК:")
                for i, error in enumerate(self.errors, 1):
                    print(f"  {i}. {error}")
                print()
            
            if self.warnings:
                print("⚠️  ПРЕДУПРЕЖДЕНИЯ:")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"  {i}. {warning}")
                print()
            
            # Шаг 10: Сохраняем скриншот
            timestamp = int(datetime.now().timestamp())
            screenshot_path = f'screenshots/validation_check_{timestamp}.png'
            await self.page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 Скриншот сохранен: {screenshot_path}")
            
            # Шаг 11: Сохраняем HTML
            html_path = f'screenshots/validation_check_{timestamp}.html'
            html = await self.page.content()
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"📄 HTML сохранен: {html_path}")
            print()
            
            # Ждем 5 секунд чтобы посмотреть
            print("⏳ Ожидание 5 секунд (можно посмотреть форму)...")
            await self.page.wait_for_timeout(5000)
            
        except Exception as e:
            print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.stop()


async def main():
    """Главная функция"""
    print("\n" + "="*60)
    print("🔍 ПРОВЕРКА ВАЛИДАЦИИ ФОРМЫ ПЛАТЕЖА")
    print("="*60)
    print()
    print("Этот скрипт:")
    print("  1. Открывает форму в браузере (визуальный режим)")
    print("  2. Заполняет основные поля")
    print("  3. Проверяет все поля на ошибки валидации")
    print("  4. Показывает, какие поля не заполнены")
    print("  5. Сохраняет скриншот и HTML")
    print()
    print("="*60)
    print()
    
    validator = FormValidator()
    await validator.run_full_check()
    
    print("\n" + "="*60)
    print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
    print("="*60)
    print()
    
    if validator.errors:
        print("❌ Найдены ошибки! Смотрите список выше.")
        return 1
    else:
        print("✅ Все поля заполнены корректно!")
        return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Проверка прервана пользователем")
        sys.exit(130)
