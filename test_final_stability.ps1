# Финальный тест стабильности системы после исправлений
# Автор: Kiro AI Assistant
# Дата: 13 января 2026

Write-Host "🔧 ФИНАЛЬНЫЙ ТЕСТ СТАБИЛЬНОСТИ СИСТЕМЫ" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

$server = "http://85.192.56.74:5001"
$headers = @{
    "Authorization" = "Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"
    "Content-Type" = "application/json"
}

$results = @()
$totalTests = 0
$successfulTests = 0

# Тест 1: Одиночные запросы (должны работать стабильно)
Write-Host "📋 ТЕСТ 1: Одиночные запросы" -ForegroundColor Yellow
Write-Host "Ожидаемый результат: 100% успех, время 22-26 секунд" -ForegroundColor Gray
Write-Host ""

for ($i = 1; $i -le 3; $i++) {
    $totalTests++
    Write-Host "  Тест 1.$i - Одиночный запрос..." -NoNewline
    
    $body = @{
        amount = 1000
        orderId = "single-test-$i-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    } | ConvertTo-Json
    
    $start = Get-Date
    try {
        $result = Invoke-RestMethod -Uri "$server/api/payment" -Method POST -Headers $headers -Body $body -TimeoutSec 35
        $end = Get-Date
        $elapsed = ($end - $start).TotalSeconds
        
        Write-Host " ✅ SUCCESS ($([math]::Round($elapsed, 1))s)" -ForegroundColor Green
        $results += "Тест 1.$i: SUCCESS в $([math]::Round($elapsed, 1))s"
        $successfulTests++
        
    } catch {
        $end = Get-Date
        $elapsed = ($end - $start).TotalSeconds
        Write-Host " ❌ FAILED ($([math]::Round($elapsed, 1))s)" -ForegroundColor Red
        $results += "Тест 1.$i: FAILED в $([math]::Round($elapsed, 1))s"
    }
    
    if ($i -lt 3) { Start-Sleep -Seconds 15 }
}

Write-Host ""

# Тест 2: Множественные запросы с интервалом (должны работать с 67% успехом)
Write-Host "📋 ТЕСТ 2: Множественные запросы (интервал 10 сек)" -ForegroundColor Yellow
Write-Host "Ожидаемый результат: 67% успех после исправлений" -ForegroundColor Gray
Write-Host ""

for ($i = 1; $i -le 3; $i++) {
    $totalTests++
    Write-Host "  Тест 2.$i - Множественный запрос..." -NoNewline
    
    $body = @{
        amount = 1000
        orderId = "multiple-test-$i-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    } | ConvertTo-Json
    
    $start = Get-Date
    try {
        $result = Invoke-RestMethod -Uri "$server/api/payment" -Method POST -Headers $headers -Body $body -TimeoutSec 35
        $end = Get-Date
        $elapsed = ($end - $start).TotalSeconds
        
        Write-Host " ✅ SUCCESS ($([math]::Round($elapsed, 1))s)" -ForegroundColor Green
        $results += "Тест 2.$i: SUCCESS в $([math]::Round($elapsed, 1))s"
        $successfulTests++
        
    } catch {
        $end = Get-Date
        $elapsed = ($end - $start).TotalSeconds
        Write-Host " ❌ FAILED ($([math]::Round($elapsed, 1))s)" -ForegroundColor Red
        $results += "Тест 2.$i: FAILED в $([math]::Round($elapsed, 1))s"
    }
    
    if ($i -lt 3) { Start-Sleep -Seconds 10 }
}

Write-Host ""

# Тест 3: Стресс-тест (должен показать ограничения системы)
Write-Host "📋 ТЕСТ 3: Стресс-тест (интервал 5 сек)" -ForegroundColor Yellow
Write-Host "Ожидаемый результат: Покажет ограничения системы" -ForegroundColor Gray
Write-Host ""

for ($i = 1; $i -le 2; $i++) {
    $totalTests++
    Write-Host "  Тест 3.$i - Стресс-тест..." -NoNewline
    
    $body = @{
        amount = 1000
        orderId = "stress-test-$i-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    } | ConvertTo-Json
    
    $start = Get-Date
    try {
        $result = Invoke-RestMethod -Uri "$server/api/payment" -Method POST -Headers $headers -Body $body -TimeoutSec 35
        $end = Get-Date
        $elapsed = ($end - $start).TotalSeconds
        
        Write-Host " ✅ SUCCESS ($([math]::Round($elapsed, 1))s)" -ForegroundColor Green
        $results += "Тест 3.$i: SUCCESS в $([math]::Round($elapsed, 1))s"
        $successfulTests++
        
    } catch {
        $end = Get-Date
        $elapsed = ($end - $start).TotalSeconds
        Write-Host " ❌ FAILED ($([math]::Round($elapsed, 1))s)" -ForegroundColor Red
        $results += "Тест 3.$i: FAILED в $([math]::Round($elapsed, 1))s"
    }
    
    if ($i -lt 2) { Start-Sleep -Seconds 5 }
}

Write-Host ""
Write-Host "📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""

$successRate = [math]::Round(($successfulTests / $totalTests) * 100, 1)

foreach ($result in $results) {
    if ($result -like "*SUCCESS*") {
        Write-Host "  $result" -ForegroundColor Green
    } else {
        Write-Host "  $result" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📈 СТАТИСТИКА:" -ForegroundColor White
Write-Host "  Всего тестов: $totalTests" -ForegroundColor White
Write-Host "  Успешных: $successfulTests" -ForegroundColor Green
Write-Host "  Неудачных: $($totalTests - $successfulTests)" -ForegroundColor Red
Write-Host "  Успешность: $successRate%" -ForegroundColor $(if ($successRate -ge 70) { "Green" } elseif ($successRate -ge 50) { "Yellow" } else { "Red" })

Write-Host ""
Write-Host "🎯 ОЦЕНКА СИСТЕМЫ:" -ForegroundColor White

if ($successRate -ge 80) {
    Write-Host "  ✅ ОТЛИЧНО - Система готова к продакшену" -ForegroundColor Green
} elseif ($successRate -ge 60) {
    Write-Host "  ⚠️  ХОРОШО - Система работает с ограничениями" -ForegroundColor Yellow
} elseif ($successRate -ge 40) {
    Write-Host "  ⚠️  УДОВЛЕТВОРИТЕЛЬНО - Требуются дополнительные исправления" -ForegroundColor Yellow
} else {
    Write-Host "  ❌ НЕУДОВЛЕТВОРИТЕЛЬНО - Система нестабильна" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔧 РЕКОМЕНДАЦИИ:" -ForegroundColor White
if ($successRate -ge 70) {
    Write-Host "  • Система готова для умеренной нагрузки" -ForegroundColor Green
    Write-Host "  • Рекомендуется интервал между запросами 10+ секунд" -ForegroundColor Green
    Write-Host "  • Мониторить ресурсы Docker контейнера" -ForegroundColor Green
} else {
    Write-Host "  • Требуется дальнейшая оптимизация" -ForegroundColor Yellow
    Write-Host "  • Рассмотреть реализацию пула браузеров" -ForegroundColor Yellow
    Write-Host "  • Увеличить ресурсы сервера" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Тест завершен!" -ForegroundColor Cyan