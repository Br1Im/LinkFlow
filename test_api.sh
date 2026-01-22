#!/bin/bash

echo "🧪 Тестирование LinkFlow API"
echo ""

BASE_URL="http://localhost:5000"

# Проверка доступности
echo "1️⃣ Проверка доступности админки..."
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL" | grep -q "200"; then
    echo "✅ Админка доступна"
else
    echo "❌ Админка недоступна. Запустите: ./start.sh"
    exit 1
fi

echo ""
echo "2️⃣ Создание тестового платежа..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/create-payment" \
  -H "Content-Type: application/json" \
  -d '{
    "card_number": "9860080323894719",
    "owner_name": "Test User",
    "amount": 500,
    "payment_mode": "test",
    "payment_system": "multitransfer"
  }')

echo "$RESPONSE" | python3 -m json.tool

PAYMENT_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('payment_id', ''))")

if [ -n "$PAYMENT_ID" ]; then
    echo ""
    echo "✅ Платеж создан с ID: $PAYMENT_ID"
    echo ""
    echo "3️⃣ Проверка статуса платежа..."
    
    for i in {1..20}; do
        sleep 3
        STATUS_RESPONSE=$(curl -s "$BASE_URL/api/payment/$PAYMENT_ID")
        STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))")
        
        echo "   Попытка $i/20: статус = $STATUS"
        
        if [ "$STATUS" = "completed" ]; then
            echo ""
            echo "✅ Платеж успешно создан!"
            echo "$STATUS_RESPONSE" | python3 -m json.tool
            exit 0
        elif [ "$STATUS" = "failed" ]; then
            echo ""
            echo "❌ Платеж завершился с ошибкой"
            echo "$STATUS_RESPONSE" | python3 -m json.tool
            exit 1
        fi
    done
    
    echo ""
    echo "⏱️ Таймаут ожидания (60 секунд)"
else
    echo "❌ Не удалось создать платеж"
    exit 1
fi
