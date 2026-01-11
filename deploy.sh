#!/bin/bash

# 🚀 Автоматическое развертывание LinkFlow Payment System
# Использование: ./deploy.sh [server_ip] [user]

set -e  # Остановка при ошибке

# Конфигурация
SERVER_IP=${1:-"85.192.56.74"}
SERVER_USER=${2:-"root"}
PROJECT_DIR="/opt/linkflow"
DOMAIN=${3:-$SERVER_IP}

echo "🚀 Развертывание LinkFlow Payment System"
echo "📡 Сервер: $SERVER_USER@$SERVER_IP"
echo "📁 Директория: $PROJECT_DIR"
echo "🌐 Домен: $DOMAIN"
echo "=================================="

# Функция для выполнения команд на сервере
run_remote() {
    echo "🔧 Выполнение на сервере: $1"
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "$1"
}

# Функция для копирования файлов
copy_files() {
    echo "📦 Копирование файлов на сервер..."
    
    # Создание архива проекта (исключая ненужные файлы)
    tar --exclude='*.git*' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='data' \
        --exclude='logs' \
        --exclude='bot/temp_qr/*' \
        --exclude='bot/profiles/*' \
        --exclude='bot/chrome_profile' \
        -czf linkflow-deploy.tar.gz .
    
    # Копирование архива на сервер
    scp -o StrictHostKeyChecking=no linkflow-deploy.tar.gz $SERVER_USER@$SERVER_IP:/tmp/
    
    # Распаковка на сервере
    run_remote "mkdir -p $PROJECT_DIR && cd $PROJECT_DIR && tar -xzf /tmp/linkflow-deploy.tar.gz && rm /tmp/linkflow-deploy.tar.gz"
    
    # Удаление локального архива
    rm linkflow-deploy.tar.gz
    
    echo "✅ Файлы скопированы"
}

# Проверка подключения к серверу
echo "🔍 Проверка подключения к серверу..."
if ! ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $SERVER_USER@$SERVER_IP "echo 'Подключение успешно'" 2>/dev/null; then
    echo "❌ Не удается подключиться к серверу $SERVER_USER@$SERVER_IP"
    echo "Проверьте:"
    echo "  - IP адрес сервера"
    echo "  - SSH ключи или пароль"
    echo "  - Доступность сервера"
    exit 1
fi
echo "✅ Подключение к серверу установлено"

# Установка Docker и зависимостей
echo "🐳 Установка Docker и зависимостей..."
run_remote "
    # Обновление системы
    apt update && apt upgrade -y
    
    # Установка Docker если не установлен
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
    fi
    
    # Установка Docker Compose если не установлен
    if ! command -v docker-compose &> /dev/null; then
        curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    # Установка дополнительных пакетов
    apt install -y nginx certbot python3-certbot-nginx htop curl wget
    
    # Проверка установки
    docker --version
    docker-compose --version
"
echo "✅ Docker и зависимости установлены"

# Копирование файлов проекта
copy_files

# Создание production конфигурации
echo "⚙️ Создание production конфигурации..."
run_remote "
cd $PROJECT_DIR

# Создание production docker-compose.yml
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  payment-admin:
    build: .
    container_name: linkflow-payment-prod
    ports:
      - \"127.0.0.1:5000:5000\"
    volumes:
      - ./data:/app/data
      - ./bot/bot_database.json:/app/bot/bot_database.json
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
      - DISPLAY=:99
      - FLASK_ENV=production
    restart: unless-stopped
    healthcheck:
      test: [\"CMD\", \"curl\", \"-f\", \"http://localhost:5000/api/health\"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    networks:
      - payment-network
    logging:
      driver: \"json-file\"
      options:
        max-size: \"10m\"
        max-file: \"3\"

networks:
  payment-network:
    driver: bridge
EOF

# Создание директорий
mkdir -p data logs
chmod 755 data logs
"
echo "✅ Production конфигурация создана"

# Настройка Nginx
echo "🌐 Настройка Nginx..."
run_remote "
# Создание конфигурации Nginx
cat > /etc/nginx/sites-available/linkflow << 'EOF'
server {
    listen 80;
    server_name $DOMAIN;
    
    client_max_body_size 10M;
    
    # Основное приложение
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # API эндпоинты с увеличенными таймаутами
    location /api/payment {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
    
    # QR коды
    location /qr/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        expires 1h;
        add_header Cache-Control \"public, immutable\";
    }
    
    access_log /var/log/nginx/linkflow_access.log;
    error_log /var/log/nginx/linkflow_error.log;
}
EOF

# Активация конфигурации
ln -sf /etc/nginx/sites-available/linkflow /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Проверка и перезапуск Nginx
nginx -t && systemctl restart nginx && systemctl enable nginx
"
echo "✅ Nginx настроен"

# Запуск приложения
echo "🚀 Запуск приложения..."
run_remote "
cd $PROJECT_DIR

# Остановка старых контейнеров если есть
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Сборка и запуск
docker-compose -f docker-compose.prod.yml up --build -d

# Ожидание запуска
echo '⏳ Ожидание запуска приложения...'
sleep 30

# Проверка статуса
docker-compose -f docker-compose.prod.yml ps
"
echo "✅ Приложение запущено"

# Настройка файрвола
echo "🛡️ Настройка файрвола..."
run_remote "
# UFW файрвол
if command -v ufw &> /dev/null; then
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 80
    ufw allow 443
    ufw --force enable
    ufw status
fi
"
echo "✅ Файрвол настроен"

# Создание скрипта бэкапа
echo "💾 Настройка бэкапов..."
run_remote "
cd $PROJECT_DIR

# Создание скрипта бэкапа
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=\"/opt/backups/linkflow\"
mkdir -p \$BACKUP_DIR

# Бэкап данных
tar -czf \$BACKUP_DIR/linkflow_data_\$DATE.tar.gz data/ bot/bot_database.json

# Удаление старых бэкапов (старше 7 дней)
find \$BACKUP_DIR -name \"*.tar.gz\" -mtime +7 -delete

echo \"Backup completed: linkflow_data_\$DATE.tar.gz\"
EOF

chmod +x backup.sh

# Добавление в cron (ежедневно в 2:00)
(crontab -l 2>/dev/null; echo '0 2 * * * $PROJECT_DIR/backup.sh') | crontab -
"
echo "✅ Бэкапы настроены"

# Финальная проверка
echo "🔍 Финальная проверка системы..."

# Проверка доступности
echo "Проверка веб-интерфейса..."
if run_remote "curl -s -o /dev/null -w '%{http_code}' http://localhost:5000/" | grep -q "200"; then
    echo "✅ Веб-интерфейс доступен"
else
    echo "⚠️ Веб-интерфейс недоступен, проверьте логи"
fi

# Проверка API здоровья
echo "Проверка API здоровья..."
if run_remote "curl -s http://localhost:5000/api/health | grep -q 'healthy\\|degraded'"; then
    echo "✅ API здоровья работает"
else
    echo "⚠️ API здоровья недоступен"
fi

# Показ логов
echo "📋 Последние логи приложения:"
run_remote "cd $PROJECT_DIR && docker-compose -f docker-compose.prod.yml logs --tail=10"

echo ""
echo "🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "=================================="
echo "🌐 Веб-интерфейс: http://$DOMAIN/"
echo "🔌 API: http://$DOMAIN/api/payment"
echo "📊 Мониторинг: http://$DOMAIN/api/health"
echo "📈 Статус очереди: http://$DOMAIN/api/queue/status"
echo ""
echo "🔧 Управление системой:"
echo "  ssh $SERVER_USER@$SERVER_IP"
echo "  cd $PROJECT_DIR"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "📞 API токен: -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"
echo ""
echo "✅ Система готова к работе!"