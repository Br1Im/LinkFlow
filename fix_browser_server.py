#!/usr/bin/env python3
"""
Патч для browser_manager.py - добавляет опции для работы на сервере
"""

def fix_browser_manager():
    with open('browser_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Найдем место где создаются опции Chrome
    old_options = """        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')"""
    
    new_options = """        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')  # Для сервера
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--single-process')  # Для стабильности на сервере"""
    
    if old_options in content:
        content = content.replace(old_options, new_options)
        
        with open('browser_manager.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ browser_manager.py обновлен для работы на сервере")
        return True
    else:
        print("❌ Не найдено место для патча")
        return False

if __name__ == '__main__':
    fix_browser_manager()