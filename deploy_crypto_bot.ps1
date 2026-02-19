# Скрипт для автоматического деплоя crypto_vip_robot на сервер

$SERVER = "root@85.192.56.74"
$LOCAL_ZIP = "crypto_bot_backup\crypto_bot.zip"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Деплой crypto_vip_robot на сервер" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Шаг 1: Загрузка файла
Write-Host "Шаг 1: Загрузка файла на сервер..." -ForegroundColor Yellow
scp $LOCAL_ZIP "${SERVER}:/root/"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Ошибка загрузки файла!" -ForegroundColor Red
    exit 1
}

Write-Host "Файл загружен успешно!" -ForegroundColor Green
Write-Host ""

# Шаг 2: Установка на сервере
Write-Host "Шаг 2: Установка на сервере..." -ForegroundColor Yellow

$INSTALL_SCRIPT = @"
pm2 stop crypto-bot 2>/dev/null || true
pm2 delete crypto-bot 2>/dev/null || true
cd /root
if [ -d 'Cryptoliqbez' ]; then
    mv Cryptoliqbez Cryptoliqbez_backup_\$(date +%Y%m%d_%H%M%S)
fi
mkdir -p Cryptoliqbez
cd Cryptoliqbez
unzip -o ../crypto_bot.zip
pip3.11 install -r requirements.txt
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name '*.pyc' -delete
pm2 start --name crypto-bot --interpreter python3.11 run.py
pm2 save
echo ''
echo '========================================='
echo 'Установка завершена!'
echo '========================================='
pm2 status
"@

ssh $SERVER $INSTALL_SCRIPT

if ($LASTEXITCODE -ne 0) {
    Write-Host "Ошибка установки!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Деплой завершён успешно!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Проверьте бота: @crypto_vip_robot" -ForegroundColor Cyan
Write-Host ""
Write-Host "Для просмотра логов выполните:" -ForegroundColor Yellow
Write-Host "ssh $SERVER 'pm2 logs crypto-bot'" -ForegroundColor White
