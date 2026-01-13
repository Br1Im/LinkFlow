# Simple deployment script
Write-Host "Deploying optimized payment system..." -ForegroundColor Green

$SERVER = "root@85.192.56.74"
$SSH_KEY = "$env:USERPROFILE\.ssh\linkflow_server_key"

# Check SSH key exists
if (!(Test-Path $SSH_KEY)) {
    Write-Host "SSH key not found: $SSH_KEY" -ForegroundColor Red
    exit 1
}

Write-Host "1. Copying files to server..." -ForegroundColor Cyan
scp -i $SSH_KEY -o StrictHostKeyChecking=no bot/payment_service_ultra.py "${SERVER}:/app/bot/"
scp -i $SSH_KEY -o StrictHostKeyChecking=no bot/admin_panel_optimized.py "${SERVER}:/app/bot/"

Write-Host "2. Stopping container..." -ForegroundColor Cyan
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER "docker stop linkflow-payment-prod"

Write-Host "3. Backing up current version..." -ForegroundColor Cyan
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER "cp /app/bot/admin_panel.py /app/bot/admin_panel_backup.py"

Write-Host "4. Replacing with optimized version..." -ForegroundColor Cyan
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER "cp /app/bot/admin_panel_optimized.py /app/bot/admin_panel.py"

Write-Host "5. Starting optimized container..." -ForegroundColor Cyan
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER "cd /app && docker-compose up -d"

Write-Host "6. Waiting for startup..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "7. Checking status..." -ForegroundColor Cyan
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER "docker ps | grep linkflow"
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER "docker logs --tail 5 linkflow-payment-prod"

Write-Host "Deployment completed!" -ForegroundColor Green
Write-Host "Next step: Run test_high_frequency.py" -ForegroundColor Cyan