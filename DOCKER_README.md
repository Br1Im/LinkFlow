# LinkFlow Docker Setup

## Быстрый старт

### 1. Запуск через Docker Compose

```bash
# Сборка и запуск
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

### 2. Доступ к сервисам

- **Админ-панель**: http://localhost:5000
- **API Server**: http://localhost:5001

### 3. Остановка

```bash
docker-compose down
```

## Структура

```
LinkFlow/
├── admin/                    # Админ-панель
│   ├── admin_panel_db.py    # Flask админка (порт 5000)
│   ├── api_server.py        # API сервер (порт 5001)
│   ├── database.py          # Работа с БД
│   ├── linkflow.db          # SQLite база данных
│   └── templates/           # HTML шаблоны
├── test_payment/            # Playwright скрипт
│   └── payment_service.py   # Сервис генерации платежей
├── 100.xlsx                 # Данные отправителей
├── Dockerfile               # Docker образ
├── docker-compose.yml       # Docker Compose конфигурация
└── start_admin.py           # Запуск обоих сервисов
```

## База данных

### Таблицы

1. **payments** - История платежей
2. **logs** - Логи системы
3. **settings** - Настройки
4. **sender_data** - Данные отправителей (из Excel)

### Импорт данных из Excel

Данные автоматически импортируются при сборке Docker образа из файла `100.xlsx`.

Для ручного импорта:

```bash
python import_excel_to_db.py
```

### Управление данными отправителей

Через админ-панель можно:
- Просматривать все данные отправителей
- Добавлять новые записи
- Редактировать существующие
- Активировать/деактивировать записи

## API Endpoints

### POST /api/payment
Создание платежа

**Headers:**
```
Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo
Content-Type: application/json
```

**Body:**
```json
{
  "amount": 1000,
  "orderId": "ORD-12345"
}
```

**Response (201):**
```json
{
  "success": true,
  "order_id": "ORD-12345",
  "amount": 1000,
  "status": "completed",
  "qr_link": "https://...",
  "payment_time": 19.5,
  "message": "Payment created successfully"
}
```

### GET /health
Проверка статуса API

**Response:**
```json
{
  "status": "ok",
  "service": "LinkFlow API",
  "version": "2.0.0",
  "mode": "playwright",
  "browser_ready": true
}
```

## Volumes

Docker Compose монтирует следующие директории:

- `./admin/linkflow.db` - База данных (сохраняется между перезапусками)
- `./screenshots` - Скриншоты при ошибках
- `./src` - Исходный код (для разработки)

## Переменные окружения

В `docker-compose.yml`:

```yaml
environment:
  - PYTHONUNBUFFERED=1
  - API_URL=http://localhost:5001
  - API_TOKEN=-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo
```

## Логи

Просмотр логов:

```bash
# Все логи
docker-compose logs

# Следить за логами в реальном времени
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs linkflow-admin
```

## Troubleshooting

### Браузер не запускается

Убедитесь что установлены все зависимости Playwright:

```bash
docker-compose exec linkflow-admin playwright install-deps chromium
```

### База данных пустая

Импортируйте данные вручную:

```bash
docker-compose exec linkflow-admin python import_excel_to_db.py
```

### Порты заняты

Измените порты в `docker-compose.yml`:

```yaml
ports:
  - "5000:5000"  # Измените первое число
  - "5001:5001"
```

## Разработка

Для разработки без Docker:

```bash
# Установка зависимостей
pip install -r admin/requirements.txt
pip install -r requirements_playwright.txt
playwright install chromium

# Импорт данных
python import_excel_to_db.py

# Запуск
python start_admin.py
```

## Production

Для production рекомендуется:

1. Изменить API_TOKEN на случайный
2. Использовать reverse proxy (nginx)
3. Настроить SSL сертификаты
4. Включить логирование в файлы
5. Настроить автоматический перезапуск

## Поддержка

При возникновении проблем проверьте:

1. Логи Docker: `docker-compose logs`
2. Статус API: `curl http://localhost:5001/health`
3. База данных: `sqlite3 admin/linkflow.db "SELECT COUNT(*) FROM sender_data;"`
