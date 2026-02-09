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

# Добавляем новый реквизит
cursor.execute("""
    INSERT INTO beneficiaries (card_number, card_owner, is_active, is_verified)
    VALUES (?, ?, 1, 1)
""", ("5614682115648125", "ABDUGANIJON HUSENBAYEV"))

print("✅ Добавлен новый реквизит: ABDUGANIJON HUSENBAYEV (5614682115648125)")

# Сохраняем изменения
conn.commit()
conn.close()

print("\n✅ База данных обновлена!")
