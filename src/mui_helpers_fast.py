# -*- coding: utf-8 -*-
"""
БЫСТРЫЕ helpers для работы с MUI (Material-UI) controlled inputs
Оптимизировано для скорости: 10-15 секунд вместо 37
"""

def fast_mui_input(driver, element, value):
    """
    БЫСТРАЯ установка значения в MUI controlled input через React events
    
    Args:
        driver: Selenium WebDriver
        element: WebElement (MUI input)
        value: Значение для установки
        
    Returns:
        bool: True если успешно
    """
    try:
        # Прямая установка через React без посимвольного ввода
        driver.execute_script("""
            const input = arguments[0];
            const value = arguments[1];
            
            // Устанавливаем значение напрямую
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;
            nativeInputValueSetter.call(input, value);
            
            // Триггерим все необходимые React события
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            input.dispatchEvent(new Event('blur', { bubbles: true }));
        """, element, str(value))
        
        return True
    except Exception as e:
        print(f"   ⚠️ Ошибка fast_mui_input: {e}")
        return False


def fast_click(driver, element):
    """
    БЫСТРЫЙ клик по элементу через JS
    
    Args:
        driver: Selenium WebDriver
        element: WebElement
        
    Returns:
        bool: True если успешно
    """
    try:
        # JS клик без прокрутки и ожиданий
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as e:
        print(f"   ⚠️ Ошибка fast_click: {e}")
        return False


def wait_for_react_ready(driver, timeout=2):
    """
    Ждет готовности React (вместо time.sleep)
    
    Args:
        driver: Selenium WebDriver
        timeout: Таймаут в секундах
        
    Returns:
        bool: True если готов
    """
    try:
        from selenium.webdriver.support.ui import WebDriverWait
        
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return True
    except:
        return False


def fast_fill_field(driver, element, value):
    """
    Универсальное быстрое заполнение поля
    Пробует fast_mui_input, если не работает - fallback на обычный ввод
    
    Args:
        driver: Selenium WebDriver
        element: WebElement
        value: Значение
        
    Returns:
        bool: True если успешно
    """
    # Сначала пробуем быстрый способ
    if fast_mui_input(driver, element, value):
        return True
    
    # Fallback: обычный ввод но без задержек
    try:
        element.clear()
        element.send_keys(str(value))
        return True
    except:
        return False
