# Скрипт для деплоя на сервер 85.192.56.74

$SERVER = "root@85.192.56.74"
$REMOTE_PATH = "/root/LinkFlow"

Write-Host "🚀 Начинаю деплой на сервер $SERVER" -ForegroundColor Green
Write-Host ("=" * 80)

# 1. Копируем обновленные файлы
Write-Host "`n📦 Копирование файлов..." -ForegroundColor Cyan

Write-Host "  - bot/admin_panel.py"
scp bot/admin_panel.py "${SERVER}:${REMOTE_PATH}/bot/"

Write-Host "  - bot/templates/admin.html"
scp bot/templates/admin.html "${SERVER}:${REMOTE_PATH}/bot/templates/"

Write-Host "  - docker-compose.yml"
scp docker-compose.yml "${SERVER}:${REMOTE_PATH}/"

Write-Host "  - Dockerfile"
scp Dockerfile "${SERVER}:${REMOTE_PATH}/"

Write-Host "`n✅ Файлы скопированы" -ForegroundColor Green

# 2. Перезапускаем Docker на сервере
Write-Host "`n🔄 Перезапуск Docker контейнера на сервере..." -ForegroundColor Cyan

$commands = @"
cd /root/LinkFlow
echo 'Останавливаем контейнер...'
docker-compose down
echo 'Пересобираем образ...'
docker-compose build --no-cache
echo 'Запускаем контейнер...'
docker-compose up -d
echo 'Ожидание запуска (20 секунд)...'
sleep 20
echo 'Проверка статуса...'
docker ps | grep linkflow
echo 'Последние логи:'
docker logs linkflow-payment-admin-1 --tail 30
"@

ssh $SERVER $commands

Write-Host "`n"
Write-Host ("=" * 80)
Write-Host "✅ Деплой завершен!" -ForegroundColor Green
Write-Host "🌐 Админка доступна на: http://85.192.56.74:5001" -ForegroundColor Yellow
Write-Host "`nДля просмотра логов используйте SSH"
