# Final deployment script with correct paths
Write-Host "Deploying optimized payment system..." -ForegroundColor Green

$SERVER = "root@85.192.56.74"
$SSH_KEY = "$env:USERPROFILE\.ssh\linkflow_server_key"

Write-Host "1. Copying files to correct location..." -ForegroundColor Cyan
scp -i $SSH_KEY -o StrictHostKeyChecking=no bot/payment_service_ultra.py "${SERVER}:/root/LinkFlow/bot/"
scp -i $SSH_KEY -o StrictHostKeyChecking=no bot/admin_panel_optimized.py "${SERVER}:/root/LinkFlow/bot/"

Write-Host "2. Backing up and replacing admin_panel.py..." -ForegroundColor Cyan
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER "cd /root/LinkFlow/bot && cp admin_panel.py admin_panel_backup.py && cp admin_panel_optimized.py admin_panel.py"

Write-Host "3. Stopping container..." -ForegroundColor Cyan
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER "docker stop linkflow-payment-prod"

Write-Host "4. Starting optimized container..." -ForegroundColor Cyan
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER "cd /root/LinkFlow && docker run -d --name linkflow-payment-prod -p 5001:5001 -v /root/LinkFlow:/app linkflow-payment"

Write-Host "5. Checking status..." -ForegroundColor Cyan
Start-Sleep -Seconds 10
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SERVER "docker ps | grep linkflow && docker logs --tail 5 linkflow-payment-prod"

Write-Host "Deployment completed!" -ForegroundColor Green