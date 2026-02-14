#!/bin/bash
# Тест API через curl

echo "=========================================="
echo "ТЕСТ API /api/create-payment"
echo "=========================================="

# Создаем временный файл с JSON
cat > /tmp/payment_test.json <<EOF
{
  "amount": 2000,
  "orderId": "TEST-CURL-$(date +%s)"
}
EOF

echo ""
echo "Отправка запроса..."
echo "URL: http://85.192.56.74/api/create-payment"
echo "Payload:"
cat /tmp/payment_test.json
echo ""
echo "=========================================="
echo ""

# Отправляем запрос
curl -X POST http://85.192.56.74/api/create-payment \
  -H "Content-Type: application/json" \
  -d @/tmp/payment_test.json \
  --max-time 60 \
  -w "\n\nHTTP Status: %{http_code}\n" \
  2>&1 | python3 -m json.tool 2>/dev/null || cat

echo ""
echo "=========================================="

# Удаляем временный файл
rm -f /tmp/payment_test.json
