#!/bin/bash
# Тест React-safe версии

echo "🧪 Тестирование React-safe версии multitransfer.ru"
echo ""

cd "$(dirname "$0")/.."

python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

from multitransfer_payment import MultitransferPayment
from recipient_data import RECIPIENT_DATA

# Данные из recipient_data.py
TEST_CARD = RECIPIENT_DATA["card_number"]
TEST_NAME = RECIPIENT_DATA["owner_name"]
TEST_AMOUNT = RECIPIENT_DATA["default_amount"]

print("=" * 60)
print("🔧 Инициализация...")
payment = MultitransferPayment()

try:
    # Логин (инициализация)
    if payment.login():
        print("✅ Инициализация успешна")
        
        # Создание платежа
        result = payment.create_payment(
            card_number=TEST_CARD,
            owner_name=TEST_NAME,
            amount=TEST_AMOUNT
        )
        
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТ:")
        print("=" * 60)
        
        if result.get("success"):
            print("✅ Платеж создан успешно!")
            print(f"⏱️  Время: {result.get('elapsed_time', 0):.1f} сек")
            print(f"🔗 Ссылка: {result.get('payment_link', 'N/A')}")
            print(f"📱 QR: {'Да' if result.get('qr_code') else 'Нет'}")
            
            # Показываем детали платежа
            payment_data = result.get('payment_data', {})
            if payment_data:
                print("\n💰 Детали платежа:")
                for key, value in payment_data.items():
                    print(f"   • {key}: {value}")
        else:
            print("❌ Ошибка создания платежа")
            print(f"⚠️  {result.get('error', 'Unknown error')}")
            
    else:
        print("❌ Ошибка инициализации")
        
finally:
    payment.close()
    print("\n✅ Тест завершён")

EOF
