@echo off
echo 🧪 Тест 3 платежей с локального ПК
echo 🌐 Сервер: 85.192.56.74:5001
echo.

echo 🚀 Платеж #1 - 1100 сум
curl -X POST "http://85.192.56.74:5001/api/payment" ^
  -H "Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo" ^
  -H "Content-Type: application/json" ^
  -d "{\"amount\": 1100, \"orderId\": \"local-test-1-%RANDOM%\"}" ^
  -w "\nВремя: %%{time_total}s\n\n"

echo.
echo ⏳ Пауза 10 секунд...
timeout /t 10 /nobreak > nul

echo 🚀 Платеж #2 - 1200 сум
curl -X POST "http://85.192.56.74:5001/api/payment" ^
  -H "Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo" ^
  -H "Content-Type: application/json" ^
  -d "{\"amount\": 1200, \"orderId\": \"local-test-2-%RANDOM%\"}" ^
  -w "\nВремя: %%{time_total}s\n\n"

echo.
echo ⏳ Пауза 10 секунд...
timeout /t 10 /nobreak > nul

echo 🚀 Платеж #3 - 1300 сум
curl -X POST "http://85.192.56.74:5001/api/payment" ^
  -H "Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo" ^
  -H "Content-Type: application/json" ^
  -d "{\"amount\": 1300, \"orderId\": \"local-test-3-%RANDOM%\"}" ^
  -w "\nВремя: %%{time_total}s\n\n"

echo.
echo 🏁 Тестирование завершено!