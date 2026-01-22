#!/bin/bash

echo "🚀 Запуск LinkFlow Admin Panel..."
echo ""

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Остановка старых контейнеров
echo "🛑 Остановка старых контейнеров..."
docker-compose -f docker-compose.local.yml down 2>/dev/null

# Сборка и запуск
echo "🔨 Сборка образа..."
docker-compose -f docker-compose.local.yml build

echo "▶️  Запуск контейнера..."
docker-compose -f docker-compose.local.yml up -d

echo ""
echo "✅ LinkFlow запущен!"
echo ""
echo "📍 Админ-панель: http://localhost:5000"
echo "📊 Список платежей: http://localhost:5000/payments"
echo ""
echo "Команды:"
echo "  Логи:      docker-compose -f docker-compose.local.yml logs -f"
echo "  Остановка: docker-compose -f docker-compose.local.yml down"
echo ""
