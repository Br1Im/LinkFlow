# Deploy optimized version to server 85.192.56.74

$SERVER = "root@85.192.56.74"
$REMOTE_PATH = "/root/LinkFlow"

Write-Host "Deploy OPTIMIZED version (target less than 10 sec)" -ForegroundColor Green
Write-Host ("=" * 80)

# 1. Copy updated files
Write-Host "`nCopying optimized files..." -ForegroundColor Cyan

Write-Host "  - bot/payment_service.py (OPTIMIZED)" -ForegroundColor Yellow
scp bot/payment_service.py "$SERVER`:$REMOTE_PATH/bot/"

Write-Host "  - bot/browser_manager.py (OPTIMIZED)" -ForegroundColor Yellow
scp bot/browser_manager.py "$SERVER`:$REMOTE_PATH/bot/"

Write-Host "  - bot/admin_panel.py" -ForegroundColor Yellow
scp bot/admin_panel.py "$SERVER`:$REMOTE_PATH/bot/"

Write-Host "`nFiles copied successfully" -ForegroundColor Green

# 2. Restart Docker on server
Write-Host "`nRestarting Docker container..." -ForegroundColor Cyan

ssh $SERVER "cd /root/LinkFlow && docker-compose down && docker-compose build --no-cache && docker-compose up -d && sleep 20 && docker ps | grep linkflow && docker logs linkflow-payment-admin-1 --tail 50"

Write-Host "`n"
Write-Host ("=" * 80)
Write-Host "OPTIMIZED VERSION DEPLOYED!" -ForegroundColor Green
Write-Host "Expected speed: less than 10 seconds per payment" -ForegroundColor Yellow
Write-Host "API: http://85.192.56.74:5001/api/payment" -ForegroundColor Cyan

Write-Host "`nFor testing:" -ForegroundColor Cyan
Write-Host "curl -X POST http://85.192.56.74:5001/api/payment -H 'Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo' -H 'Content-Type: application/json' -d '{`"amount`": 1000, `"orderId`": `"test-speed-123`"}'"

Write-Host "`nFor logs:" -ForegroundColor Cyan
Write-Host "ssh $SERVER 'docker logs -f linkflow-payment-admin-1'"
