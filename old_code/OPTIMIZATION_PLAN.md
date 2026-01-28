# План оптимизации (37s → 10-15s)

## Текущие узкие места:

### 1. **Ввод данных в MUI поля** (~5-7s)
- Сейчас: посимвольный ввод с `time.sleep(0.05)` на каждый символ
- Оптимизация: использовать `executeScript` для прямой установки значения React state
- Экономия: **~4-5s**

### 2. **Множественные sleep между действиями** (~8-10s)
```python
time.sleep(0.5)  # После ввода суммы
time.sleep(0.3)  # После клика
time.sleep(0.2)  # Между полями
time.sleep(1.0)  # После капчи
time.sleep(2.0)  # Ожидание QR
```
- Оптимизация: заменить на умные ожидания (WebDriverWait с условиями)
- Экономия: **~6-8s**

### 3. **Ожидание активации кнопок** (~3-5s)
- Сейчас: фиксированные таймауты 10-20s
- Оптимизация: уменьшить до 3-5s + проверка состояния
- Экономия: **~2-3s**

### 4. **Выбор способа перевода** (~2-3s)
- Сейчас: открытие модалки + выбор + закрытие
- Оптимизация: прямой клик через JS без анимаций
- Экономия: **~1-2s**

### 5. **Прогрев браузера** (первый запуск)
- Сейчас: каждый раз выбирается способ перевода
- Оптимизация: держать браузер открытым между запросами
- Экономия: **~3-4s** на повторных запросах

## Итоговая оптимизация:

### Быстрый ввод в MUI:
```python
def fast_mui_input(driver, element, value):
    """Быстрая установка значения в React controlled input"""
    driver.execute_script("""
        const input = arguments[0];
        const value = arguments[1];
        
        // Устанавливаем значение напрямую
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value'
        ).set;
        nativeInputValueSetter.call(input, value);
        
        // Триггерим React события
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.dispatchEvent(new Event('blur', { bubbles: true }));
    """, element, str(value))
```

### Умные ожидания:
```python
# Вместо time.sleep(0.5)
WebDriverWait(driver, 2).until(
    lambda d: d.execute_script("return document.readyState") == "complete"
)

# Вместо time.sleep после клика
WebDriverWait(driver, 2).until(
    EC.staleness_of(old_element)
)
```

### Параллельные проверки:
```python
# Вместо последовательных попыток
selectors = [selector1, selector2, selector3]
for selector in selectors:
    try:
        element = driver.find_element(By.XPATH, selector)
        if element.is_displayed():
            return element
    except:
        continue
```

## Ожидаемый результат:
- **Первый запуск**: 15-18s (с выбором способа)
- **Повторные запуски**: 10-12s (без выбора способа)
- **С прогретым браузером**: 8-10s

## Критические моменты (нельзя ускорять):
1. Ожидание капчи (~1-2s) - нужно для загрузки iframe
2. Ожидание QR-кода (~1-2s) - нужно для рендеринга SVG
3. Переход между страницами (~0.5-1s) - сетевые запросы
