import sqlite3

conn = sqlite3.connect('linkflow.db')
cursor = conn.cursor()

cursor.execute('DELETE FROM beneficiaries')
conn.commit()

print(f'Удалено записей: {cursor.rowcount}')

cursor.execute('SELECT COUNT(*) FROM beneficiaries')
print(f'Осталось записей: {cursor.fetchone()[0]}')

conn.close()
