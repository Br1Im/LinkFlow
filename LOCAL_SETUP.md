# Локальная настройка LinkFlow через Docker

## Быстрый старт

1. **Запустить админ-панель:**
```bash
cd LinkFlow
docker-compose -f docker-compose.local.yml up --build
```

2. **Открыть в браузере:**
```
http://localhost:5000
```

3. **Создать платёж через админку:**
   - Введите номер карты получателя
   - Введите имя владельца карты
   - Укажите сумму (100-75000 RUB)
   - Выберите режим платежа (standard/fast/test)
   - Нажмите "Создать платёж"

## Режимы платежей

- **Standard** (100-75000 RUB) - обычный режим
- **Fast** (100-15000 RUB) - быстрый режим
- **Test** (100-1000 RUB) - тестовый режим

## API Endpoints

### Создать платёж
```bash
curl -X POST http://localhost:5000/api/create-payment \
  -H "Content-Type: application/json" \
  -d '{
    "card_number": "1234567890123456",
    "owner_name": "IVAN IVANOV",
    "amount": 500,
    "payment_mode": "standard"
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

## Остановка

```bash
docker-compose -f docker-compose.local.yml down
```

## Логи

```bash
docker-compose -f docker-compose.local.yml logs -f
```
