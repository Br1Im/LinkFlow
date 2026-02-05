# LinkFlow - Payment Link Generator

Автоматизированная система создания платежных ссылок с админ-панелью.

## Структура проекта

```
LinkFlow/
├── admin/              # Админ-панель (Flask)
│   ├── admin_panel_db.py   # Основной сервер админки (порт 5000)
│   ├── api_server.py       # API сервер (порт 5001)
│   ├── database.py         # Работа с SQLite БД
│   ├── templates/          # HTML шаблоны
│   └── linkflow.db         # База данных
├── test_payment/       # Скрипт создания платежей (Playwright)
│   └── payment_service.py  # Основной сервис
├── 100.xlsx            # Данные отправителей для импорта
├── import_excel_to_db.py   # Скрипт импорта данных в БД
└── linkflow.db         # Главная база данных
```

## Установка

### 1. Установка зависимостей

```bash
# Python зависимости
pip3 install flask playwright pandas openpyxl

# Playwright браузер
playwright install chromium
```

### 2. Импорт данных

```bash
python3 import_excel_to_db.py
```

### 3. Запуск сервисов

**Админ-панель (порт 5000):**
```bash
cd admin
python3 admin_panel_db.py
```

**API сервер (порт 5001):**
```bash
cd admin
python3 api_server.py
```

## Использование

1. Откройте админ-панель: `http://localhost:5000`
2. Добавьте реквизиты получателей в разделе "Реквизиты"
3. Создавайте платежи в разделе "Создать"

### Дополнительные опции

При создании платежа можно использовать кастомные данные:
- **Реквизиты получателя**: номер карты + владелец
- **Паспортные данные**: ФИО, дата рождения, телефон

## API

### Создание платежа

```bash
POST http://localhost:5001/api/payment
Authorization: Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo
Content-Type: application/json

{
  "amount": 1000,
  "orderId": "ORDER-123"
}
```

### Ответ

```json
{
  "success": true,
  "qr_link": "https://...",
  "payment_time": 19.5,
  "order_id": "ORDER-123"
}
```

## Особенности

- ✅ Автоматическая проверка реквизитов при добавлении
- ✅ Случайный выбор данных отправителя из БД
- ✅ Кастомные данные для быстрого тестирования
- ✅ Headless режим браузера
- ✅ Время создания платежа: ~19 секунд
- ✅ Автоматическое решение капчи

## Технологии

- **Backend**: Python 3.8+, Flask
- **Database**: SQLite
- **Automation**: Playwright (Chromium)
- **Frontend**: Alpine.js, Tailwind CSS

## Порты

- `5000` - Админ-панель
- `5001` - API сервер

## Безопасность

API защищен Bearer токеном. Токен указан в `admin/api_server.py`.
