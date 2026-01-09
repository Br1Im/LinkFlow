#!/bin/bash
echo "🚀 Развертывание на хостинге..."
cd /root/LinkFlow
pkill -f "python.*webhook_server" || true
pkill -f chrome || true
sleep 2
cp bot/webhook_server.py bot/webhook_server_backup_$(date +%Y%m%d_%H%M%S).py
cp bot/webhook_server_balanced_fast.py bot/webhook_server.py
sed -i "s/taskkill.*chrome.exe/pkill -f chrome/g" bot/webhook_server.py
sed -i "s/taskkill.*chromedriver.exe/pkill -f chromedriver/g" bot/webhook_server.py
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
sleep 2
cd bot
nohup python3 webhook_server.py > webhook.log 2>&1 &
sleep 10
curl -s -H "Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo" http://localhost:5000/api/health
echo "✅ Развертывание завершено!"