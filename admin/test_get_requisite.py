#!/usr/bin/env python3
import sys
sys.path.insert(0, 'payment_service')
from payzteam_api import get_payzteam_requisite
import json

print("Тест get_payzteam_requisite с суммой 2000 RUB:")
result = get_payzteam_requisite(2000)
print(json.dumps(result, indent=2, ensure_ascii=False))
