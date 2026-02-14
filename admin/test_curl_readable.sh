#!/bin/bash
# Тест API с читаемым выводом на русском

curl -X POST http://85.192.56.74/api/create-payment \
  -H "Content-Type: application/json" \
  -d '{"amount":300}' \
  --max-time 60 \
  -s | python3 -c "import sys, json; print(json.dumps(json.loads(sys.stdin.read()), indent=2, ensure_ascii=False))"
