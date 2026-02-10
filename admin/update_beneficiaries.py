#!/usr/bin/env python3
"""
Скрипт для обновления реквизитов в БД
Удаляет все старые и добавляет новые
"""

import sqlite3

# Подключаемся к БД
conn = sqlite3.connect('linkflow.db')
cursor = conn.cursor()

# Удаляем все старые реквизиты
cursor.execute("DELETE FROM beneficiaries")
print("✅ Все старые реквизиты удалены")

# Добавляем новые реквизиты
cursor.execute("""
    INSERT INTO beneficiaries (card_number, card_owner, is_active, is_verified)
    VALUES (?, ?, 1, 1)
""", ("9860096601965088", "Azizbek Medetbaev"))

cursor.execute("""
    INSERT INTO beneficiaries (card_number, card_owner, is_active, is_verified)
    VALUES (?, ?, 1, 1)
""", ("5614686701465695", "Azizbek Medetbaev"))

print("✅ Добавлены новые реквизиты:")
print("   1. Azizbek Medetbaev (9860096601965088)")
print("   2. Azizbek Medetbaev (5614686701465695)")

# Сохраняем изменения
conn.commit()
conn.close()

print("\n✅ База данных обновлена!")
