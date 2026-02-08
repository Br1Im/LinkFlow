#!/usr/bin/env python3
import database

beneficiaries = database.get_all_beneficiaries()
print("Реквизиты в БД:")
for b in beneficiaries:
    print(f"{b['id']}: {b['card_owner']} - {b['card_number']} (active={b['is_active']})")
