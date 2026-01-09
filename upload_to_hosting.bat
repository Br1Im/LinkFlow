@echo off
echo ========================================
echo Загрузка файлов на хостинг
echo ========================================
echo.

echo Загружаю webhook_server_production.py...
scp webhook_server_production.py root@85.192.56.74:/root/

echo.
echo Загружаю deploy_production_fix.sh...
scp deploy_production_fix.sh root@85.192.56.74:/root/

echo.
echo ========================================
echo Файлы загружены!
echo ========================================
echo.
echo Теперь подключитесь к хостингу и выполните:
echo   ssh root@85.192.56.74
echo   chmod +x deploy_production_fix.sh
echo   ./deploy_production_fix.sh
echo.
pause
