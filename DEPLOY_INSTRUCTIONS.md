# 🚀 Инструкции по развертыванию LinkFlow

## 📋 Подготовка к развертыванию

### 1. Настройка Git репозитория

#### Создание репозитория на GitHub:
1. Перейдите на https://github.com/new
2. Название: `LinkFlow-PaymentSystem`
3. Описание: `🚀 Система автоматического создания платежных ссылок с современной админ панелью`
4. Сделайте репозиторий **публичным**
5. **НЕ** добавляйте README, .gitignore или лицензию (они уже есть)
6. Нажмите "Create repository"

#### Подключение локального репозитория:
```bash
# Замените YOUR_USERNAME на ваш GitHub username
git remote add origin https://github.com/YOUR_USERNAME/LinkFlow-PaymentSystem.git
git push -u origin master
```

### 2. Автоматическая настройка
Используйте готовый скрипт:
```bash
# Windows
.\setup_git_remote.bat

# PowerShell
.\setup_git_remote.ps1
```

## 🐳 Развертывание через Docker

### Локальное развертывание

```bash
# 1. Клонирование репозитория
git clone https://github.com/YOUR_USERNAME/LinkFlow-PaymentSystem.git
cd LinkFlow-PaymentSystem

# 2. Запуск через Docker Compose
docker-compose up -d

# 3. Проверка статуса
docker-compose ps
docker-compose logs -f

# Админ панель будет доступна на http://localhost:8080
```

### Развертывание на сервере

```bash
# 1. Подключение к серверу
ssh user@your-server.com

# 2. Установка Docker (если не установлен)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Клонирование и запуск
git clone https://github.com/YOUR_USERNAME/LinkFlow-PaymentSystem.git
cd LinkFlow-PaymentSystem
docker-compose up -d

# 5. Настройка автозапуска
sudo systemctl enable docker
```

## ⚙️ Настройка системы

### 1. Первоначальная настройка
1. Откройте админ панель: `http://your-server:8080`
2. Перейдите в раздел **"Аккаунты входа"**
3. Добавьте телефон и пароль от аккаунта elecsnet.ru
4. Перейдите в раздел **"Реквизиты карт"**
5. Добавьте номер карты и имя владельца

### 2. Тестирование
1. Перейдите в раздел **"Создать ссылку"**
2. Укажите тестовую сумму (например, 5000 сум)
3. Нажмите **"Создать ссылку"**
4. Проверьте, что ссылка создается за 8-15 секунд

### 3. Мониторинг
- **Дашборд**: Общая статистика системы
- **API Health**: `http://your-server:8080/api/health`
- **Статус очереди**: `http://your-server:8080/api/queue/status`

## 🔧 Конфигурация для продакшена

### 1. Изменение порта (опционально)
Отредактируйте `docker-compose.yml`:
```yaml
ports:
  - "80:8080"  # Для доступа через стандартный HTTP порт
```

### 2. Настройка SSL (рекомендуется)
```bash
# Установка Nginx
sudo apt install nginx

# Настройка reverse proxy
sudo nano /etc/nginx/sites-available/linkflow
```

Конфигурация Nginx:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Настройка автозапуска
```bash
# Создание systemd сервиса
sudo nano /etc/systemd/system/linkflow.service
```

Содержимое сервиса:
```ini
[Unit]
Description=LinkFlow Payment System
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/LinkFlow-PaymentSystem
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Активация:
```bash
sudo systemctl enable linkflow.service
sudo systemctl start linkflow.service
```

## 📊 Мониторинг и логи

### Просмотр логов
```bash
# Все логи
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f payment-admin

# Последние 100 строк
docker-compose logs --tail=100 payment-admin
```

### Мониторинг ресурсов
```bash
# Использование ресурсов контейнерами
docker stats

# Статус контейнеров
docker-compose ps
```

### Ключевые метрики
- **Время создания платежа**: 8-15 секунд (норма)
- **Размер очереди**: 0-2 запроса (норма)
- **Статус браузера**: "ready" (норма)
- **Использование RAM**: ~500MB (норма)

## 🛠 Обслуживание

### Обновление системы
```bash
# 1. Остановка системы
docker-compose down

# 2. Обновление кода
git pull origin master

# 3. Пересборка и запуск
docker-compose up --build -d

# 4. Проверка статуса
docker-compose ps
```

### Резервное копирование данных
```bash
# Создание бэкапа данных
tar -czf linkflow-backup-$(date +%Y%m%d).tar.gz data/

# Восстановление из бэкапа
tar -xzf linkflow-backup-YYYYMMDD.tar.gz
```

### Очистка логов
```bash
# Очистка логов Docker
docker system prune -f

# Ротация логов (добавить в crontab)
0 2 * * * docker-compose -f /path/to/LinkFlow-PaymentSystem/docker-compose.yml logs --tail=1000 > /dev/null
```

## 🚨 Устранение неполадок

### Проблема: Браузер не запускается
```bash
# Проверка версий
docker exec -it linkflow_payment-admin_1 google-chrome --version
docker exec -it linkflow_payment-admin_1 chromedriver --version

# Перезапуск контейнера
docker-compose restart payment-admin
```

### Проблема: Медленное создание платежей
1. Проверьте `/api/health` - браузер должен быть "ready"
2. Проверьте `/api/queue/status` - очередь не должна быть переполнена
3. Перезапустите систему: `docker-compose restart`

### Проблема: Ошибки авторизации elecsnet.ru
1. Проверьте корректность логина/пароля в админ панели
2. Убедитесь, что аккаунт не заблокирован
3. Проверьте логи: `docker-compose logs payment-admin | grep "авторизация"`

## 📞 Поддержка

### Контакты
- **Email**: hackathon@datsteam.dev
- **GitHub Issues**: https://github.com/YOUR_USERNAME/LinkFlow-PaymentSystem/issues

### Полезные ссылки
- **Документация Docker**: https://docs.docker.com/
- **Документация Docker Compose**: https://docs.docker.com/compose/
- **Selenium WebDriver**: https://selenium-python.readthedocs.io/

---

## ✅ Чек-лист развертывания

- [ ] Создан репозиторий на GitHub
- [ ] Код отправлен в репозиторий
- [ ] Docker и Docker Compose установлены
- [ ] Система запущена через `docker-compose up -d`
- [ ] Добавлены аккаунты elecsnet.ru
- [ ] Добавлены банковские карты
- [ ] Протестировано создание платежной ссылки
- [ ] Настроен мониторинг
- [ ] Настроено резервное копирование
- [ ] Настроен автозапуск (для продакшена)

**🎉 Поздравляем! LinkFlow успешно развернут и готов к работе!**