#!/bin/bash
# Скрипт для защиты сервера от атак ботнета
# Автор: Kiro AI Assistant

echo "🔒 НАСТРОЙКА ЗАЩИТЫ СЕРВЕРА ОТ АТАК"
echo "=================================="

# 1. Блокировка подозрительных запросов через iptables
echo "📛 Настройка iptables для блокировки атак..."

# Блокируем запросы к уязвимостям PHPUnit
iptables -I INPUT -p tcp --dport 5001 -m string --string "phpunit" --algo bm -j DROP
iptables -I INPUT -p tcp --dport 5001 -m string --string "eval-stdin.php" --algo bm -j DROP

# Блокируем запросы к уязвимостям ThinkPHP
iptables -I INPUT -p tcp --dport 5001 -m string --string "think\\app" --algo bm -j DROP
iptables -I INPUT -p tcp --dport 5001 -m string --string "invokefunction" --algo bm -j DROP

# Блокируем запросы к Docker API
iptables -I INPUT -p tcp --dport 5001 -m string --string "/containers/json" --algo bm -j DROP

# Блокируем запросы к бинарникам ботнета
iptables -I INPUT -p tcp --dport 5001 -m string --string "/bins/" --algo bm -j DROP
iptables -I INPUT -p tcp --dport 5001 -m string --string "/skid." --algo bm -j DROP
iptables -I INPUT -p tcp --dport 5001 -m string --string "harm" --algo bm -j DROP
iptables -I INPUT -p tcp --dport 5001 -m string --string "gmpsl" --algo bm -j DROP

echo "✅ iptables правила добавлены"

# 2. Создание nginx конфигурации с защитой
echo "🛡️ Создание защищенной nginx конфигурации..."

cat > /etc/nginx/sites-available/linkflow-secure << 'EOF'
# Защищенная конфигурация nginx для LinkFlow
server {
    listen 80;
    server_name 85.192.56.74;
    
    # Rate limiting - максимум 10 запросов в минуту с одного IP
    limit_req_zone $binary_remote_addr zone=payment_api:10m rate=10r/m;
    limit_req_zone $binary_remote_addr zone=general:10m rate=30r/m;
    
    # Блокировка подозрительных User-Agent
    if ($http_user_agent ~* (bot|crawler|spider|scanner|masscan|nmap)) {
        return 444;
    }
    
    # Блокировка подозрительных запросов
    location ~* (phpunit|eval-stdin|think|invokefunction|containers/json|/bins/|/skid\.|harm|gmpsl) {
        return 444;
    }
    
    # Блокировка попыток directory traversal
    location ~* \.\./\.\. {
        return 444;
    }
    
    # API эндпоинт с жестким rate limiting
    location /api/ {
        limit_req zone=payment_api burst=2 nodelay;
        
        # Увеличенные таймауты для платежей
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Основной сайт с умеренным rate limiting
    location / {
        limit_req zone=general burst=10 nodelay;
        
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Логирование подозрительных запросов
    access_log /var/log/nginx/linkflow_access.log;
    error_log /var/log/nginx/linkflow_error.log;
}
EOF

# 3. Активация защищенной конфигурации
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
fi

ln -sf /etc/nginx/sites-available/linkflow-secure /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo "✅ Nginx конфигурация обновлена"

# 4. Настройка fail2ban для дополнительной защиты
echo "🚫 Настройка fail2ban..."

apt-get update && apt-get install -y fail2ban

cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-req-limit]
enabled = true
filter = nginx-req-limit
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/linkflow_error.log
maxretry = 3
bantime = 7200

[nginx-attack]
enabled = true
filter = nginx-attack
action = iptables-multiport[name=Attack, port="http,https", protocol=tcp]
logpath = /var/log/nginx/linkflow_access.log
maxretry = 1
bantime = 86400
EOF

cat > /etc/fail2ban/filter.d/nginx-req-limit.conf << 'EOF'
[Definition]
failregex = limiting requests, excess: .* by zone .*, client: <HOST>
EOF

cat > /etc/fail2ban/filter.d/nginx-attack.conf << 'EOF'
[Definition]
failregex = ^<HOST> -.*"(GET|POST).*(phpunit|eval-stdin|think|invokefunction|containers/json|/bins/|/skid\.|harm|gmpsl).*"
EOF

systemctl enable fail2ban
systemctl restart fail2ban

echo "✅ fail2ban настроен"

# 5. Сохранение iptables правил
echo "💾 Сохранение iptables правил..."
iptables-save > /etc/iptables/rules.v4

echo ""
echo "🎯 ЗАЩИТА НАСТРОЕНА УСПЕШНО!"
echo "=============================="
echo "✅ iptables: Блокировка подозрительных запросов"
echo "✅ nginx: Rate limiting и фильтрация"
echo "✅ fail2ban: Автоматическая блокировка атакующих IP"
echo ""
echo "📊 Для мониторинга используйте:"
echo "  - tail -f /var/log/nginx/linkflow_access.log"
echo "  - fail2ban-client status"
echo "  - iptables -L -n"