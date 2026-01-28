# -*- coding: utf-8 -*-
"""
Helpers для работы с MUI (Material-UI) controlled inputs
"""

def set_mui_input_value(driver, element, value):
    """
    React-safe установка значения в MUI controlled input
    
    Args:
        driver: Selenium WebDriver
        element: WebElement (MUI input)
        value: Значение для установки
        
    Returns:
        bool: True если успешно
    """
    try:
        import time
        
        # Фокус на элементе
        element.click()
        time.sleep(0.1)
        
        # Очистка поля
        element.clear()
        time.sleep(0.1)
        
        # Ввод посимвольно (React ловит каждый символ)
        for char in str(value):
            element.send_keys(char)
            time.sleep(0.05)  # Минимальная пауза
        
        # Клик вне поля для trigger blur
        driver.execute_script("document.body.click()")
        time.sleep(0.1)
        
        return True
    except Exception as e:
        print(f"   ⚠️ Ошибка set_mui_input_value: {e}")
        return False


def click_mui_element(driver, element):
    """
    React-safe клик по MUI элементу
    
    Args:
        driver: Selenium WebDriver
        element: WebElement
        
    Returns:
        bool: True если успешно
    """
    try:
        # Прокрутка к элементу
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center', behavior:'instant'});",
            element
        )
        
        # Минимальная пауза
        import time
        time.sleep(0.1)
        
        # JS клик (надёжнее для React)
        driver.execute_script("arguments[0].click();", element)
        
        return True
    except Exception as e:
        print(f"   ⚠️ Ошибка click_mui_element: {e}")
        return False


def wait_for_mui_button_enabled(driver, button_id, timeout=10):
    """
    Ждёт активации MUI кнопки (disabled=null)
    
    Args:
        driver: Selenium WebDriver
        button_id: ID кнопки
        timeout: Таймаут в секундах
        
    Returns:
        bool: True если кнопка активна
    """
    import time
    from selenium.webdriver.common.by import By
    
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            button = driver.find_element(By.ID, button_id)
            if button.get_attribute("disabled") is None:
                return True
        except:
            pass
        
        time.sleep(0.2)
    
    return False
