#!/usr/bin/env python3
"""
Патч для browser_manager.py - убираем профили пользователя для сервера
"""

def fix_browser_manager():
    with open('browser_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Комментируем строку с профилем пользователя
    if '--user-data-dir=' in content:
        content = content.replace(
            "options.add_argument(f'--user-data-dir={profile_path}')",
            "# options.add_argument(f'--user-data-dir={profile_path}')  # Отключено для сервера"
        )
        print("✅ Отключен user-data-dir")
    
    # Добавляем опции для работы без профиля
    if '--disable-web-security' in content and '--disable-features=VizDisplayCompositor' not in content:
        content = content.replace(
            "options.add_argument('--disable-web-security')",
            """options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--no-first-run')
        options.add_argument('--no-default-browser-check')"""
        )
        print("✅ Добавлены опции для работы без профиля")
    
    with open('browser_manager.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Патч для работы без профиля применен")
    return True

if __name__ == '__main__':
    fix_browser_manager()