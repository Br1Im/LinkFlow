# -*- coding: utf-8 -*-
"""
Helpers ╨┤╨╗╤П ╤А╨░╨▒╨╛╤В╤Л ╤Б MUI (Material-UI) controlled inputs
"""

def set_mui_input_value(driver, element, value):
    """
    React-safe ╤Г╤Б╤В╨░╨╜╨╛╨▓╨║╨░ ╨╖╨╜╨░╤З╨╡╨╜╨╕╤П ╨▓ MUI controlled input
    
    Args:
        driver: Selenium WebDriver
        element: WebElement (MUI input)
        value: ╨Ч╨╜╨░╤З╨╡╨╜╨╕╨╡ ╨┤╨╗╤П ╤Г╤Б╤В╨░╨╜╨╛╨▓╨║╨╕
        
    Returns:
        bool: True ╨╡╤Б╨╗╨╕ ╤Г╤Б╨┐╨╡╤И╨╜╨╛
    """
    try:
        import time
        
        # ╨д╨╛╨║╤Г╤Б ╨╜╨░ ╤Н╨╗╨╡╨╝╨╡╨╜╤В╨╡
        element.click()
        time.sleep(0.1)
        
        # ╨Ю╤З╨╕╤Б╤В╨║╨░ ╨┐╨╛╨╗╤П
        element.clear()
        time.sleep(0.1)
        
        # ╨Т╨▓╨╛╨┤ ╨┐╨╛╤Б╨╕╨╝╨▓╨╛╨╗╤М╨╜╨╛ (React ╨╗╨╛╨▓╨╕╤В ╨║╨░╨╢╨┤╤Л╨╣ ╤Б╨╕╨╝╨▓╨╛╨╗)
        for char in str(value):
            element.send_keys(char)
            time.sleep(0.05)  # ╨Ь╨╕╨╜╨╕╨╝╨░╨╗╤М╨╜╨░╤П ╨┐╨░╤Г╨╖╨░
        
        # ╨Ъ╨╗╨╕╨║ ╨▓╨╜╨╡ ╨┐╨╛╨╗╤П ╨┤╨╗╤П trigger blur
        driver.execute_script("document.body.click()")
        time.sleep(0.1)
        
        return True
    except Exception as e:
        print(f"   тЪая╕П ╨Ю╤И╨╕╨▒╨║╨░ set_mui_input_value: {e}")
        return False


def click_mui_element(driver, element):
    """
    React-safe ╨║╨╗╨╕╨║ ╨┐╨╛ MUI ╤Н╨╗╨╡╨╝╨╡╨╜╤В╤Г
    
    Args:
        driver: Selenium WebDriver
        element: WebElement
        
    Returns:
        bool: True ╨╡╤Б╨╗╨╕ ╤Г╤Б╨┐╨╡╤И╨╜╨╛
    """
    try:
        # ╨Я╤А╨╛╨║╤А╤Г╤В╨║╨░ ╨║ ╤Н╨╗╨╡╨╝╨╡╨╜╤В╤Г
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center', behavior:'instant'});",
            element
        )
        
        # ╨Ь╨╕╨╜╨╕╨╝╨░╨╗╤М╨╜╨░╤П ╨┐╨░╤Г╨╖╨░
        import time
        time.sleep(0.1)
        
        # JS ╨║╨╗╨╕╨║ (╨╜╨░╨┤╤С╨╢╨╜╨╡╨╡ ╨┤╨╗╤П React)
        driver.execute_script("arguments[0].click();", element)
        
        return True
    except Exception as e:
        print(f"   тЪая╕П ╨Ю╤И╨╕╨▒╨║╨░ click_mui_element: {e}")
        return False


def wait_for_mui_button_enabled(driver, button_id, timeout=10):
    """
    ╨Ц╨┤╤С╤В ╨░╨║╤В╨╕╨▓╨░╤Ж╨╕╨╕ MUI ╨║╨╜╨╛╨┐╨║╨╕ (disabled=null)
    
    Args:
        driver: Selenium WebDriver
        button_id: ID ╨║╨╜╨╛╨┐╨║╨╕
        timeout: ╨в╨░╨╣╨╝╨░╤Г╤В ╨▓ ╤Б╨╡╨║╤Г╨╜╨┤╨░╤Е
        
    Returns:
        bool: True ╨╡╤Б╨╗╨╕ ╨║╨╜╨╛╨┐╨║╨░ ╨░╨║╤В╨╕╨▓╨╜╨░
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
