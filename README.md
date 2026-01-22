# 💳 LinkFlow

Автоматизированная система создания платежей через multitransfer.ru и elecsnet.ru для карт Узбекистана.

## 🚀 Быстрый старт (Docker)

```bash
cd LinkFlow
./start.sh
```

Откройте в браузере: **http://localhost:5000**

## 🧪 Тестирование API

```bash
./test_api.sh
```

## ✨ Возможности

- 🌐 **Веб-интерфейс** для создания платежей
- 🔄 **Две платёжные системы**: Multitransfer.ru и Elecsnet.ru
- ⚡ **Три режима работы**: standard/fast/test
- 📊 **Мониторинг статуса** платежей в реальном времени
- 🐳 **Docker** для простого развертывания
- 🔌 **REST API** для интеграции
- 🎯 **React-safe** работа с MUI controlled inputs
- ⚡ **Оптимизация**: страна и банк выбираются заранее при логине

## 📋 Режимы платежей

| Режим | Лимиты (RUB) | Описание |
|-------|--------------|----------|
| **Standard** | 100 - 75,000 | Обычный режим |
| **Fast** | 100 - 15,000 | Быстрый режим |
| **Test** | 100 - 1,000 | Тестовый режим |

## 🔌 API Endpoints

### Создать платёж
```bash
curl -X POST http://localhost:5000/api/create-payment \
  -H "Content-Type: application/json" \
  -d '{
    "card_number": "9860080323894719",
    "owner_name": "Test User",
    "amount": 500,
    "payment_mode": "standard",
    "payment_system": "multitransfer"
  }'
```

### Получить статус платежа
```bash
curl http://localhost:5000/api/payment/1
```

### Список всех платежей
```bash
curl http://localhost:5000/api/payments
```

## 📖 Документация

- [LOCAL_SETUP.md](LOCAL_SETUP.md) - Локальная настройка через Docker
- [QUICKSTART.md](QUICKSTART.md) - Быстрый старт для разработки
- [SSH_SETUP.md](SSH_SETUP.md) - Настройка SSH для деплоя
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Архитектура проекта
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Решение проблем

## 🔧 Требования

- Docker
- Docker Compose

## 📁 Структура проекта

```
LinkFlow/
├── admin/                        # Админ-панель
│   ├── app.py                    # Flask приложение
│   └── templates/                # HTML шаблоны
├── src/                          # Исходный код
│   ├── config.py                 # Конфигурация
│   ├── multitransfer_payment.py  # Multitransfer.ru
│   └── payment_manager.py        # Elecsnet.ru
├── docker-compose.local.yml      # Docker Compose для локальной работы
├── Dockerfile.admin              # Docker образ админки
├── start.sh                      # Скрипт запуска
└── test_api.sh                   # Скрипт тестирования
```

## 🛑 Остановка

```bash
docker-compose -f docker-compose.local.yml down
```

## 📊 Логи

```bash
docker-compose -f docker-compose.local.yml logs -f
```

## 💻 Использование в коде

```python
from src.multitransfer_payment import MultitransferPayment

payment = MultitransferPayment(headless=True)
payment.login()

result = payment.create_payment(
    card_number="9860080323894719",
    owner_name="Nodir Asadullayev",
    amount=500
)

payment.close()
```

## 📄 Лицензия

MIT
