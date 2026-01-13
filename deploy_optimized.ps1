# Развертывание оптимизированной системы платежей
# PowerShell версия с использованием SSH ключа

Write-Host "🚀 РАЗВЕРТЫВАНИЕ ОПТИМИЗИРОВАННОЙ СИСТЕМЫ ПЛАТЕЖЕЙ" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "Цель: Ускорение до 8-12 секунд + поддержка частых запросов" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Green

$SERVER = "root@85.192.56.74"
$SSH_KEY = "$env:USERPROFILE\.ssh\linkflow_server_key"

# Проверяем наличие SSH ключа
if (!(Test-Path $SSH_KEY)) {
    Write-Host "❌ SSH ключ не найден: $SSH_KEY" -ForegroundColor Red
    Write-Host "Запустите сначала: .\setup_ssh_key_simple.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "📦 1. Копирование оптимизированных файлов на сервер..." -ForegroundColor Cyan

# Копируем файлы
scp -i $SSH_KEY -o StrictHostKeyChecking=no bot/payment_service_ultra.py "${SERVER}:/app/bot/"
scp -i $SSH_KEY -o StrictHostKeyChecking=no bot/admin_panel_optimized.py "${SERVER}:/app/bot/"
scp -i $SSH_KEY -o StrictHostKeyChecking=no bot/optimized_browser_pool.py "${SERVER}:/app/bot/"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка копирования файлов" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Файлы скопированы" -ForegroundColor Green

Write-Host "🔄 2. Остановка текущего контейнера..." -ForegroundColor Cyan
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER "docker stop linkflow-payment-prod || true"

Write-Host "⏳ 3. Пауза 5 секунд для корректного завершения..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "🏗️ 4. Создание бэкапа текущей версии..." -ForegroundColor Cyan
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER @"
if [ -f /app/bot/admin_panel.py ]; then
    cp /app/bot/admin_panel.py /app/bot/admin_panel_backup_`$(date +%Y%m%d_%H%M%S).py
    echo 'Бэкап создан'
fi
"@

Write-Host "🔧 5. Замена файлов на оптимизированные версии..." -ForegroundColor Cyan
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER @"
# Заменяем admin_panel на оптимизированную версию
cp /app/bot/admin_panel_optimized.py /app/bot/admin_panel.py
echo 'admin_panel.py заменен на оптимизированную версию'

# Проверяем что файлы на месте
ls -la /app/bot/payment_service_ultra.py
ls -la /app/bot/admin_panel.py
ls -la /app/bot/optimized_browser_pool.py
"@

Write-Host "🚀 6. Запуск оптимизированного контейнера..." -ForegroundColor Cyan
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER @"
cd /app
docker-compose up -d
"@

Write-Host "⏳ 7. Ожидание запуска (15 секунд)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "🔍 8. Проверка статуса контейнера..." -ForegroundColor Cyan
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER @"
docker ps | grep linkflow-payment-prod
echo ''
echo 'Последние логи:'
docker logs --tail 10 linkflow-payment-prod
"@

Write-Host "✅ 9. Проверка API..." -ForegroundColor Cyan
Write-Host "🌐 Тестирую health endpoint..." -ForegroundColor Yellow

# Тестируем health endpoint
try {
    $healthResponse = Invoke-WebRequest -Uri "http://85.192.56.74:5001/api/health" -Headers @{"Authorization"="Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"} -TimeoutSec 10
    $healthData = $healthResponse.Content | ConvertFrom-Json
    Write-Host "Health Status: $($healthData.status)" -ForegroundColor Green
} catch {
    Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "🌐 Тестирую stats endpoint..." -ForegroundColor Yellow

# Тестируем stats endpoint
try {
    $statsResponse = Invoke-WebRequest -Uri "http://85.192.56.74:5001/api/stats" -Headers @{"Authorization"="Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"} -TimeoutSec 10
    $statsData = $statsResponse.Content | ConvertFrom-Json
    Write-Host "Total Requests: $($statsData.total_requests)" -ForegroundColor Green
    Write-Host "Success Rate: $($statsData.success_rate)%" -ForegroundColor Green
    Write-Host "Avg Response Time: $($statsData.avg_response_time)s" -ForegroundColor Green
} catch {
    Write-Host "Stats check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "📊 Изменения:" -ForegroundColor Cyan
Write-Host "   • Ускорены все таймауты в 2 раза" -ForegroundColor White
Write-Host "   • Убрана система очередей" -ForegroundColor White
Write-Host "   • Добавлена параллельная обработка" -ForegroundColor White
Write-Host "   • Уменьшен API таймаут до 15 секунд" -ForegroundColor White
Write-Host "   • Добавлена статистика в реальном времени" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Ожидаемые результаты:" -ForegroundColor Cyan
Write-Host "   • Время ответа: 8-12 секунд (было 20-22)" -ForegroundColor White
Write-Host "   • Поддержка частых запросов (1-3s интервал)" -ForegroundColor White
Write-Host "   • Параллельная обработка до 5 запросов" -ForegroundColor White
Write-Host ""
Write-Host "📋 Следующий шаг: Запустить тест частых запросов" -ForegroundColor Cyan
Write-Host "   python test_high_frequency.py" -ForegroundColor White