#!/usr/bin/env python3
"""
Патч для browser_manager.py - умные опции для стабильности без отключения JS
"""

def fix_browser_manager():
    with open('browser_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Найдем место где создаются опции Chrome
    old_options_start = """        options.add_argument('--headless')  # Для сервера"""
    
    if old_options_start in content:
        # Найдем весь блок опций
        lines = content.split('\n')
        new_lines = []
        in_options_block = False
        
        for line in lines:
            if '--headless' in line and 'Для сервера' in line:
                in_options_block = True
                # Заменяем весь блок опций
                new_lines.extend([
                    "        options.add_argument('--headless')",
                    "        options.add_argument('--remote-debugging-port=9222')",
                    "        options.add_argument('--disable-crash-reporter')",
                    "        options.add_argument('--disable-logging')",
                    "        options.add_argument('--disable-plugins')",
                    "        options.add_argument('--disable-plugins-discovery')",
                    "        options.add_argument('--disable-translate')",
                    "        options.add_argument('--hide-scrollbars')",
                    "        options.add_argument('--mute-audio')",
                    "        options.add_argument('--disable-in-process-stack-traces')",
                    "        options.add_argument('--disable-dev-tools')",
                    "        options.add_argument('--memory-pressure-off')",
                    "        options.add_argument('--disable-features=VizDisplayCompositor')",
                    "        options.add_argument('--disable-background-timer-throttling')",
                    "        options.add_argument('--disable-backgrounding-occluded-windows')",
                    "        options.add_argument('--disable-renderer-backgrounding')",
                    "        options.add_argument('--disable-ipc-flooding-protection')"
                ])
                continue
            elif in_options_block and line.strip().startswith('options.add_argument'):
                continue  # Пропускаем старые опции
            elif in_options_block and not line.strip().startswith('options.add_argument'):
                in_options_block = False
                new_lines.append(line)
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
        
        with open('browser_manager.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ browser_manager.py обновлен с умными опциями")
        return True
    else:
        print("❌ Не найдено место для патча")
        return False

if __name__ == '__main__':
    fix_browser_manager()