Write-Host "🧪 Тест 3 платежей с локального ПК" -ForegroundColor Green
Write-Host "🌐 Сервер: 85.192.56.74:5001" -ForegroundColor Cyan
Write-Host ""

$headers = @{
    "Authorization" = "Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"
    "Content-Type" = "application/json"
}

$url = "http://85.192.56.74:5001/api/payment"

# Платеж 1
Write-Host "🚀 Платеж #1 - 1100 сум" -ForegroundColor White
$body1 = '{"amount": 1100, "orderId": "local-test-1-' + [int][double]::Parse((Get-Date -UFormat %s)) + '"}'
$start1 = Get-Date
try {
    $response1 = Invoke-RestMethod -Uri $url -Method POST -Headers $headers -Body $body1 -TimeoutSec 35
    $duration1 = ((Get-Date) - $start1).TotalSeconds
    if ($response1.success) {
        Write-Host "✅ Платеж #1 УСПЕШЕН за $([math]::Round($duration1, 1)) сек" -ForegroundColor Green
        Write-Host "   ⚡ Время обработки: $([math]::Round($response1.elapsedTime, 1)) сек" -ForegroundColor Gray
    } else {
        Write-Host "❌ Платеж #1 НЕУДАЧЕН: $($response1.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Платеж #1 ОШИБКА: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Start-Sleep -Seconds 10

# Платеж 2
Write-Host "🚀 Платеж #2 - 1200 сум" -ForegroundColor White
$body2 = '{"amount": 1200, "orderId": "local-test-2-' + [int][double]::Parse((Get-Date -UFormat %s)) + '"}'
$start2 = Get-Date
try {
    $response2 = Invoke-RestMethod -Uri $url -Method POST -Headers $headers -Body $body2 -TimeoutSec 35
    $duration2 = ((Get-Date) - $start2).TotalSeconds
    if ($response2.success) {
        Write-Host "✅ Платеж #2 УСПЕШЕН за $([math]::Round($duration2, 1)) сек" -ForegroundColor Green
        Write-Host "   ⚡ Время обработки: $([math]::Round($response2.elapsedTime, 1)) сек" -ForegroundColor Gray
    } else {
        Write-Host "❌ Платеж #2 НЕУДАЧЕН: $($response2.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Платеж #2 ОШИБКА: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Start-Sleep -Seconds 10

# Платеж 3
Write-Host "🚀 Платеж #3 - 1300 сум" -ForegroundColor White
$body3 = '{"amount": 1300, "orderId": "local-test-3-' + [int][double]::Parse((Get-Date -UFormat %s)) + '"}'
$start3 = Get-Date
try {
    $response3 = Invoke-RestMethod -Uri $url -Method POST -Headers $headers -Body $body3 -TimeoutSec 35
    $duration3 = ((Get-Date) - $start3).TotalSeconds
    if ($response3.success) {
        Write-Host "✅ Платеж #3 УСПЕШЕН за $([math]::Round($duration3, 1)) сек" -ForegroundColor Green
        Write-Host "   ⚡ Время обработки: $([math]::Round($response3.elapsedTime, 1)) сек" -ForegroundColor Gray
    } else {
        Write-Host "❌ Платеж #3 НЕУДАЧЕН: $($response3.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Платеж #3 ОШИБКА: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🏁 Тестирование завершено!" -ForegroundColor Green