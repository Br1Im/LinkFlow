@echo off
REM Скрипт для запуска LinkFlow Admin в Docker (Windows)

echo ==========================================
echo   ЗАПУСК LINKFLOW ADMIN В DOCKER
echo ==========================================
echo.

REM Проверка Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не установлен!
    echo Установите Docker: https://docs.docker.com/get-docker/
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose не установлен!
    echo Установите Docker Compose: https://docs.docker.com/compose/install/
    exit /b 1
)

echo ✅ Docker установлен
echo.

REM Сборка и запуск
echo 🔨 Сборка Docker образа...
docker-compose build

if errorlevel 1 (
    echo ❌ Ошибка сборки Docker образа
    exit /b 1
)

echo.
echo 🚀 Запуск контейнера...
docker-compose up -d

if errorlevel 1 (
    echo ❌ Ошибка запуска контейнера
    exit /b 1
)

echo.
echo ✅ LinkFlow Admin запущен!
echo.
echo Доступ:
echo   📊 Admin Panel: http://localhost:5000
echo   🔌 API Server:  http://localhost:5001
echo.
echo Логи:
echo   docker-compose logs -f
echo.
echo Остановка:
echo   docker-compose down
echo.

pause
