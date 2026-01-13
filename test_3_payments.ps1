# Тест 3 платежей с локального ПК на сервер
Write-Host "🧪 Тестирование 3 платежей с агрессивной логикой нажатия кнопки" -ForegroundColor Green
Write-Host "🌐 Сервер: 85.192.56.74:5001" -ForegroundColor Cyan
Write-Host "⏰ Время начала: $(Get-Date)" -ForegroundColor Yellow
Write-Host ""

$headers = @{
    "Authorization" = "Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"
    "Content-Type" = "application/json"
}

$baseUrl = "http://85.192.56.74:5001/api/payment"

for ($i = 1; $i -le 3; $i++) {
    $timestamp = [int][double]::Parse((Get-Date -UFormat %s))
    $orderId = "local-test-$i-$timestamp"
    
    $body = @{
        amount = 1000 + ($i * 100)  # 1100, 1200, 1300
        orderId = $orderId
    } | ConvertTo-Json
    
    Write-Host "🚀 Платеж #$i - Сумма: $($1000 + ($i * 100)) сум, OrderId: $orderId" -ForegroundColor White
    Write-Host "⏰ Время отправки: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
    
    $startTime = Get-Date
    
    try {
        $response = Invoke-RestMethod -Uri $baseUrl -Method POST -Headers $headers -Body $body -TimeoutSec 35
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        if ($response.success) {
            Write-Host "✅ Платеж #$i УСПЕШЕН за $([math]::Round($duration, 1)) сек" -ForegroundColor Green
            Write-Host "   💳 PaymentId: $($response.paymentId)" -ForegroundColor Gray
            Write-Host "   🔗 URL: $($response.paymentUrl.Substring(0, [Math]::Min(60, $response.paymentUrl.Length)))..." -ForegroundColor Gray
            Write-Host "   ⚡ Время обработки: $([math]::Round($response.elapsedTime, 1)) сек" -ForegroundColor Gray
        } else {
            Write-Host "❌ Платеж #$i НЕУДАЧЕН за $([math]::Round($duration, 1)) сек" -ForegroundColor Red
            Write-Host "   🚫 Ошибка: $($response.error)" -ForegroundColor Red
            Write-Host "   📝 Сообщение: $($response.message)" -ForegroundColor Red
        }
    }
    catch {
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        Write-Host "❌ Платеж #$i ОШИБКА за $([math]::Round($duration, 1)) сек" -ForegroundColor Red
        Write-Host "   🚫 Исключение: $($_.Exception.Message)" -ForegroundColor Red
    }
    }
    
    Write-Host ""
    
    # Пауза между запросами (кроме последнего)
    if ($i -lt 3) {
        Write-Host "⏳ Пауза 10 секунд перед следующим платежом..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
}

Write-Host "🏁 Тестирование завершено в $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green