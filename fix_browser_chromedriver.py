#!/usr/bin/env python3
"""
Патч для browser_manager.py - исправляет путь к chromedriver
"""

def fix_browser_manager():
    with open('browser_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Найдем место где создается драйвер
    old_driver_creation = """        driver = webdriver.Chrome(options=options)"""
    
    new_driver_creation = """        # Для сервера нужно указать путь к chromedriver
        from selenium.webdriver.chrome.service import Service
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)"""
    
    if old_driver_creation in content:
        content = content.replace(old_driver_creation, new_driver_creation)
        
        with open('browser_manager.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ browser_manager.py обновлен с правильным путем к chromedriver")
        return True
    else:
        print("❌ Не найдено место для патча")
        return False

if __name__ == '__main__':
    fix_browser_manager()