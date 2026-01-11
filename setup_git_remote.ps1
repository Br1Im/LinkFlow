# Настройка удаленного Git репозитория
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Настройка удаленного Git репозитория" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$username = Read-Host "Введите ваш GitHub username"
$reponame = Read-Host "Введите название репозитория (по умолчанию LinkFlow-PaymentSystem)"

if ([string]::IsNullOrEmpty($reponame)) {
    $reponame = "LinkFlow-PaymentSystem"
}

Write-Host ""
Write-Host "Добавляем удаленный репозиторий..." -ForegroundColor Yellow
try {
    git remote add origin "https://github.com/$username/$reponame.git"
    Write-Host "Удаленный репозиторий добавлен" -ForegroundColor Green
} catch {
    Write-Host "Ошибка добавления удаленного репозитория: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Отправляем код в репозиторий..." -ForegroundColor Yellow
try {
    git push -u origin master
    Write-Host "Код успешно отправлен!" -ForegroundColor Green
} catch {
    Write-Host "Ошибка отправки кода: $_" -ForegroundColor Red
    Write-Host "Возможно, репозиторий не существует или нет прав доступа" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Готово! Репозиторий настроен" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ваш репозиторий: https://github.com/$username/$reponame" -ForegroundColor Green
Write-Host ""
Read-Host "Нажмите Enter для выхода"