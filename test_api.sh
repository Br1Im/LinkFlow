#!/bin/bash
curl -X POST 'http://localhost:5001/api/payment' \
  -H 'Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo' \
  -H 'Content-Type: application/json' \
  -d '{"amount": 1000, "orderId": "test-fix-'$(date +%s)'"}'