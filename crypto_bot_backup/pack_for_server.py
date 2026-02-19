"""
Скрипт для упаковки файлов crypto-bot для загрузки на сервер
"""
import os
import shutil
from pathlib import Path

# Файлы и папки для включения
include_patterns = [
    '*.py',
    '.env',
    'requirements.txt',
    'subscriptions.db',
    '*.json',
    '*.md',
]

include_dirs = [
    'payments',
]

# Исключить
exclude_patterns = [
    '__pycache__',
    '*.pyc',
    'venv',
    'bot.log',
    'pack_for_server.py',
    'enable_payments.py',
]

def should_include(path):
    """Проверяет, нужно ли включать файл"""
    path_str = str(path)
    
    # Исключаем
    for pattern in exclude_patterns:
        if pattern in path_str:
            return False
    
    return True

def main():
    print("📦 Упаковка crypto-bot для сервера...")
    
    # Создаём временную папку
    temp_dir = Path('crypto_bot_deploy')
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # Копируем файлы
    copied_files = []
    
    # Python файлы
    for py_file in Path('.').glob('*.py'):
        if should_include(py_file) and py_file.name != 'pack_for_server.py':
            shutil.copy2(py_file, temp_dir / py_file.name)
            copied_files.append(py_file.name)
    
    # Другие файлы
    for pattern in ['.env', 'requirements.txt', 'subscriptions.db', '*.json', '*.md']:
        for file in Path('.').glob(pattern):
            if should_include(file):
                shutil.copy2(file, temp_dir / file.name)
                copied_files.append(file.name)
    
    # Папки
    for dir_name in include_dirs:
        src_dir = Path(dir_name)
        if src_dir.exists():
            dst_dir = temp_dir / dir_name
            shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            copied_files.append(f"{dir_name}/")
    
    print(f"\n✅ Скопировано {len(copied_files)} файлов/папок:")
    for f in sorted(copied_files):
        print(f"  - {f}")
    
    print(f"\n📁 Файлы готовы в папке: {temp_dir.absolute()}")
    print("\n📋 Следующие шаги:")
    print("1. Создайте архив:")
    print(f"   tar -czf crypto_bot.tar.gz -C {temp_dir} .")
    print("2. Загрузите на сервер:")
    print("   scp crypto_bot.tar.gz root@85.192.56.74:/root/")
    print("3. Следуйте инструкциям в DEPLOY_TO_SERVER.md")

if __name__ == '__main__':
    main()
