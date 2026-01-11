@echo off
echo ========================================
echo   Настройка удаленного Git репозитория
echo ========================================
echo.

set /p username="Введите ваш GitHub username: "
set /p reponame="Введите название репозитория (по умолчанию LinkFlow-PaymentSystem): "

if "%reponame%"=="" set reponame=LinkFlow-PaymentSystem

echo.
echo Добавляем удаленный репозиторий...
git remote add origin https://github.com/%username%/%reponame%.git

echo.
echo Отправляем код в репозиторий...
git push -u origin master

echo.
echo ========================================
echo   Готово! Репозиторий настроен
echo ========================================
echo.
echo Ваш репозиторий: https://github.com/%username%/%reponame%
echo.
pause