@echo off
echo 🚀 Установка Webhook API сервера...

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден. Установите Python 3.8+
    pause
    exit /b 1
)

REM Установка зависимостей
echo 📚 Установка зависимостей...
pip install -r requirements.txt

REM Генерация токена если не задан
if not defined WEBHOOK_API_TOKEN (
    echo 🔑 Генерация токена...
    python -c "import secrets; print('WEBHOOK_API_TOKEN=' + secrets.token_urlsafe(32))" > .env
    echo Токен сохранен в .env файл
)

REM Тестирование
echo 🧪 Тестирование конфигурации...
python webhook_config.py

echo.
echo ============================================================
echo ✅ УСТАНОВКА ЗАВЕРШЕНА
echo ============================================================
echo 🚀 Запуск сервера: python webhook_server.py
echo 🧪 Тестирование: python test_webhook.py
echo 📋 Конфигурация: webhook_config.py
echo ============================================================
pause