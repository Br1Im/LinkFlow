#!/usr/bin/env python3
"""
Минимальный патч для browser_manager.py - только headless и chromedriver
"""

def fix_browser_manager():
    with open('browser_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Добавляем headless режим
    if '--no-sandbox' in content and '--headless' not in content:
        content = content.replace(
            "options.add_argument('--no-sandbox')",
            "options.add_argument('--no-sandbox')\n        options.add_argument('--headless')"
        )
        print("✅ Добавлен headless режим")
    
    # 2. Исправляем путь к chromedriver
    if 'driver = webdriver.Chrome(options=options)' in content:
        content = content.replace(
            'driver = webdriver.Chrome(options=options)',
            '''# Для сервера нужно указать путь к chromedriver
        from selenium.webdriver.chrome.service import Service
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)'''
        )
        print("✅ Исправлен путь к chromedriver")
    
    with open('browser_manager.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Минимальный патч применен успешно")
    return True

if __name__ == '__main__':
    fix_browser_manager()