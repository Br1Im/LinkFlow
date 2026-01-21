# React + MUI Fix для multitransfer.ru

## Проблема

Сайт multitransfer.ru использует React + Material-UI (MUI) с controlled inputs. Стандартные методы Selenium (`send_keys`, `clear`) не работают, потому что:

1. **MUI Controlled Input** — значение контролируется React state, а не DOM
2. **React откатывает изменения** — если не было правильных событий (input/change/blur)
3. **Банки не появляются** — пока React не примет сумму и не обновит state

## Решение

### 1. React-safe ввод суммы

```python
# ❌ НЕ РАБОТАЕТ
amount_input.clear()
amount_input.send_keys(str(amount))

# ✅ РАБОТАЕТ
self.driver.execute_script("""
    const input = arguments[0];
    input.focus();
    input.value = '';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    
    input.value = arguments[1];
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    input.dispatchEvent(new Event('blur', { bubbles: true }));
""", amount_input, str(amount))
```

### 2. Ожидание подтверждения React

Вместо ожидания банков напрямую, ждём активации кнопки "Продолжить":

```python
# ✅ Надёжный индикатор
wait.until(
    lambda d: d.find_element(By.ID, "pay").get_attribute("disabled") is None
)
```

### 3. Открытие блока "Способ перевода"

Обязательно кликнуть по блоку, иначе банки не появятся:

```python
transfer_block = wait.until(
    EC.element_to_be_clickable((
        By.XPATH,
        "//div[contains(text(),'Способ перевода')]/ancestor::div[contains(@class,'variant-alternative')]"
    ))
)
click_mui_element(driver, transfer_block)
```

### 4. Выбор банка по тексту

Забываем про `aria-label` и CSS классы:

```python
# ✅ Универсальный способ
bank_option = wait.until(
    EC.element_to_be_clickable((
        By.XPATH,
        "//*[contains(text(),'Uzcard') or contains(text(),'Humo')]"
    ))
)
```

## Архитектура

### Модули

1. **multitransfer_payment.py** — основная логика
2. **mui_helpers.py** — универсальные helpers для MUI
3. **debug_helpers.py** — отладочные утилиты

### Helpers

#### `set_mui_input_value(driver, element, value)`
React-safe установка значения в MUI input

#### `click_mui_element(driver, element)`
React-safe клик с прокруткой

#### `wait_for_mui_button_enabled(driver, button_id, timeout)`
Ожидание активации MUI кнопки

#### `dump_dom_state(driver, step_name)`
Сохранение скриншота + HTML для отладки

## Правильная цепочка действий

1. ✅ Выбор страны (Узбекистан)
2. ✅ JS-ввод суммы (input/change/blur события)
3. ✅ Ожидание активации кнопки "Продолжить"
4. ✅ Клик по блоку "Способ перевода"
5. ✅ Клик по Uzcard / Humo
6. ✅ Заполнение формы карты
7. ✅ Отправка формы

## Что удалено

❌ Циклы ожидания банков по CSS классам  
❌ Поиск по `aria-label`  
❌ Повторные попытки выбора банка  
❌ `send_keys` для MUI inputs  

## Тестирование

### Локально
```bash
./scripts/test_react_safe.sh
```

### Docker
```bash
docker-compose up --build
```

## Debug

При проблемах проверяйте файлы в `/tmp/`:
- `debug_*_*.png` — скриншоты
- `debug_*_*.html` — HTML страницы

## Важно для headless

Добавлена строка для триггера React в headless режиме:
```python
self.driver.execute_script("document.body.click()")
```

Без неё React иногда не обрабатывает события.
