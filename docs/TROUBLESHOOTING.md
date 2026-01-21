# Troubleshooting Guide

## Проблема: Кнопка "Продолжить" не активируется

### Симптомы
- ⚠️ Кнопка 'Продолжить' не активировалась
- ❌ Банк Uzcard/Humo не находится
- React не принимает введённую сумму

### Причины

1. **React не получил события**
   - MUI controlled input требует специфичных событий
   - События должны быть в правильном порядке: focus → input → change → blur

2. **Headless режим**
   - В headless режиме React иногда не обрабатывает события
   - Нужен дополнительный клик вне поля

3. **Timing проблемы**
   - React нужно время на обработку
   - Слишком быстрое выполнение может пропустить обновление state

### Решения

#### 1. Увеличить паузы

```python
# После ввода суммы
time.sleep(2)  # Вместо 1 секунды
```

#### 2. Попробовать несколько раз

```python
# Retry логика
for attempt in range(3):
    set_mui_input_value(driver, amount_input, amount)
    time.sleep(1)
    
    if wait_for_mui_button_enabled(driver, "pay", timeout=5):
        break
```

#### 3. Отключить headless для отладки

```python
# В _create_driver()
# options.add_argument('--headless=new')  # Закомментировать
```

#### 4. Проверить скриншоты

```bash
ls -lh /tmp/debug_*.png
```

Откройте скриншот и проверьте:
- Введена ли сумма в поле?
- Активна ли кнопка "Продолжить"?
- Видны ли способы перевода?

### Debug команды

```bash
# Посмотреть последние debug файлы
ls -lt /tmp/debug_* | head -10

# Проверить HTML на наличие банков
grep -i "uzcard\|humo" /tmp/debug_*.html | head -5

# Проверить состояние кнопки
grep 'id="pay"' /tmp/debug_*.html
```

### Известные ограничения

1. **Сайт может измениться**
   - Селекторы могут устареть
   - React логика может обновиться

2. **Headless нестабильность**
   - Некоторые сайты блокируют headless
   - Может потребоваться user-agent

3. **Captcha**
   - Сайт может показать captcha
   - Нужна ручная проверка

### Следующие шаги

Если проблема не решается:

1. Запустите с отключённым headless
2. Проверьте скриншоты
3. Увеличьте таймауты
4. Добавьте retry логику
5. Проверьте, не изменился ли сайт

## Проблема: TimeoutException при поиске банка

### Причина
Банки не появляются, потому что React не принял сумму.

### Решение
Сначала решите проблему с кнопкой "Продолжить" (см. выше).

## Проблема: Импорты не работают

### Симптом
```
ImportError: attempted relative import with no known parent package
```

### Решение
Используйте try/except в импортах:

```python
try:
    from .mui_helpers import ...
except ImportError:
    from mui_helpers import ...
```

## Полезные ссылки

- [REACT_MUI_FIX.md](REACT_MUI_FIX.md) — подробное решение
- [ARCHITECTURE_V2.md](ARCHITECTURE_V2.md) — архитектура
- [NEXT_STEPS.md](../NEXT_STEPS.md) — что делать дальше
