#!/usr/bin/env python3
import database

# Инициализируем БД
database.init_database()

# Добавляем тестовые реквизиты
beneficiary_id = database.add_beneficiary(
    card_number="2200700812345678",
    card_owner="IVAN IVANOV"
)

# Делаем реквизиты активными и верифицированными
database.update_beneficiary_verification(beneficiary_id, is_verified=True)
database.update_beneficiary_status(beneficiary_id, is_active=True)

print(f"✅ Добавлены тестовые реквизиты (ID: {beneficiary_id})")

# Проверяем
beneficiaries = database.get_all_beneficiaries()
print("\nРеквизиты в БД:")
for b in beneficiaries:
    print(f"{b['id']}: {b['card_owner']} - {b['card_number']} (active={b['is_active']}, verified={b['is_verified']})")
