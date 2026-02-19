import sqlite3

conn = sqlite3.connect('subscriptions.db')
cursor = conn.cursor()

# Включаем все способы оплаты
cursor.execute('UPDATE payment_methods SET enabled = 1')
conn.commit()

# Проверяем
cursor.execute('SELECT code, title, enabled FROM payment_methods')
methods = cursor.fetchall()

print("Способы оплаты:")
for code, title, enabled in methods:
    status = "✅ Включен" if enabled else "❌ Выключен"
    print(f"{code}: {title} - {status}")

conn.close()
print("\nВсе способы оплаты включены!")
