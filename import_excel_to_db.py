#!/usr/bin/env python3
"""
Импорт данных отправителей из Excel в БД
"""

import sys
import os

# Добавляем путь к модулю database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'admin'))

import database as db

def main():
    excel_file = '100.xlsx'
    
    if not os.path.exists(excel_file):
        print(f"❌ Файл {excel_file} не найден!")
        return
    
    print(f"📥 Импорт данных из {excel_file}...")
    
    # Инициализируем БД
    db.init_database()
    
    # Импортируем данные
    try:
        count = db.import_sender_data_from_excel(excel_file)
        print(f"✅ Импортировано {count} записей")
        
        # Показываем статистику
        all_senders = db.get_all_sender_data()
        print(f"\n📊 Всего в БД: {len(all_senders)} записей")
        print(f"   Активных: {sum(1 for s in all_senders if s['is_active'])}")
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
