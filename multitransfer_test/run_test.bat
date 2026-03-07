@echo off
echo ========================================
echo Тест multitransfer.ru
echo ========================================
echo.

echo Установка зависимостей...
pip install -r requirements.txt
echo.

echo Установка браузеров Playwright...
playwright install chromium
echo.

echo Запуск теста...
python test_multitransfer.py

echo.
echo Тест завершен!
pause