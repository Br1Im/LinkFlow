#!/usr/bin/env python3
"""
Анализ HTML страницы для поиска проблемы с отправкой формы
"""

from bs4 import BeautifulSoup

with open('debug_page.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=" * 70)
print("АНАЛИЗ HTML СТРАНИЦЫ")
print("=" * 70)

# Проверяем кнопку Продолжить
pay_button = soup.find('button', {'id': 'pay'})
if pay_button:
    print("\n✅ Кнопка 'Продолжить' найдена:")
    print(f"   - disabled: {pay_button.get('disabled', 'нет')}")
    print(f"   - type: {pay_button.get('type')}")
    print(f"   - class: {pay_button.get('class')}")
else:
    print("\n❌ Кнопка 'Продолжить' НЕ найдена!")

# Проверяем поля с ошибками
error_fields = soup.find_all(attrs={'aria-invalid': 'true'})
print(f"\n📊 Полей с aria-invalid='true': {len(error_fields)}")
if error_fields:
    for field in error_fields[:5]:
        name = field.get('name', 'unknown')
        value = field.get('value', '')
        print(f"   - {name}: {value[:50]}")

# Проверяем текст ошибок
error_texts = soup.find_all('p', class_='Mui-error')
print(f"\n📊 Текстов ошибок (Mui-error): {len(error_texts)}")
if error_texts:
    for error in error_texts[:5]:
        text = error.get_text(strip=True)
        if text:
            print(f"   - {text}")

# Проверяем все input поля
all_inputs = soup.find_all('input', {'type': ['text', 'tel']})
print(f"\n📊 Всего input полей: {len(all_inputs)}")

filled_inputs = [inp for inp in all_inputs if inp.get('value')]
print(f"📊 Заполненных полей: {len(filled_inputs)}")

empty_inputs = [inp for inp in all_inputs if not inp.get('value')]
print(f"📊 Пустых полей: {len(empty_inputs)}")
if empty_inputs:
    print("\nПустые поля:")
    for inp in empty_inputs[:10]:
        name = inp.get('name', 'unknown')
        placeholder = inp.get('placeholder', '')
        print(f"   - {name} (placeholder: {placeholder})")

# Проверяем форму
form = soup.find('form')
if form:
    print("\n✅ Форма найдена")
    print(f"   - action: {form.get('action', 'не указан')}")
    print(f"   - method: {form.get('method', 'не указан')}")
else:
    print("\n❌ Форма НЕ найдена!")

# Проверяем модалки
modals = soup.find_all(text=lambda text: text and ('Проверка данных' in text or 'Ошибка' in text or 'некорректна' in text))
if modals:
    print(f"\n⚠️ Найдено модалок/сообщений: {len(modals)}")
    for modal in modals[:3]:
        print(f"   - {modal[:100]}")

print("\n" + "=" * 70)
