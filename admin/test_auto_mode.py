#!/usr/bin/env python3
"""
Тест режима AUTO: H2H → PayzTeam fallback
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

from requisite_config import set_requisite_service, get_requisite_service
from payzteam_api import get_payzteam_requisite
import json

print("="*70)
print("ТЕСТ РЕЖИМА AUTO")
print("="*70)

# Устанавливаем режим AUTO
set_requisite_service('auto')
print(f"\nТекущий режим: {get_requisite_service()}")

# Тестируем с суммой 300 RUB (обычно H2H не возвращает)
print(f"\n{'='*70}")
print("Тест 1: Сумма 300 RUB (H2H обычно не возвращает)")
print(f"{'='*70}")

result = get_payzteam_requisite(300)

if result:
    print(f"\n✅ Реквизиты получены!")
    print(f"  Источник: {result.get('source', 'unknown')}")
    print(f"  Карта: {result.get('card_number')}")
    print(f"  Владелец: {result.get('card_owner')}")
    print(f"  Банк: {result.get('bank', 'N/A')}")
else:
    print(f"\n❌ Реквизиты не получены")

# Тестируем с суммой 2000 RUB (H2H обычно возвращает)
print(f"\n{'='*70}")
print("Тест 2: Сумма 2000 RUB (H2H обычно возвращает)")
print(f"{'='*70}")

result = get_payzteam_requisite(2000)

if result:
    print(f"\n✅ Реквизиты получены!")
    print(f"  Источник: {result.get('source', 'unknown')}")
    print(f"  Карта: {result.get('card_number')}")
    print(f"  Владелец: {result.get('card_owner')}")
    print(f"  Банк: {result.get('bank', 'N/A')}")
else:
    print(f"\n❌ Реквизиты не получены")

print(f"\n{'='*70}")
