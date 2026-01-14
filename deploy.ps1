$SERVER = "root@85.192.56.74"
$REMOTE_PATH = "/root/LinkFlow"

Write-Host "Deploying to server..." -ForegroundColor Green

Write-Host "Copying files..."
scp bot/admin_panel.py "${SERVER}:${REMOTE_PATH}/bot/"
scp bot/templates/admin.html "${SERVER}:${REMOTE_PATH}/bot/templates/"

Write-Host "Restarting Docker..."
ssh $SERVER "cd /root/LinkFlow && docker-compose down && docker-compose up -d --build"

Write-Host "Waiting for startup..."
Start-Sleep -Seconds 20

Write-Host "Checking logs..."
ssh $SERVER "docker logs linkflow-payment-admin-1 --tail 30"

Write-Host "Done! Admin panel: http://85.192.56.74:5001" -ForegroundColor Yellow
