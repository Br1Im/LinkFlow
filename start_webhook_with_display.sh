#!/bin/bash
# Запуск webhook сервера с виртуальным дисплеем

echo "🖥️ Запуск виртуального дисплея..."
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!

# Ждем запуска Xvfb
sleep 2

echo "🚀 Запуск webhook сервера..."
cd /home
export PYTHONPATH=/home:/home/bot
python3 /home/webhook_server_simple_http.py

# Убиваем Xvfb при завершении
kill $XVFB_PID