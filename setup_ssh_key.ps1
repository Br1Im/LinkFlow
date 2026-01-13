# Настройка SSH ключа для беспарольного доступа к серверу
# Для Windows PowerShell

Write-Host "🔑 НАСТРОЙКА SSH КЛЮЧА ДЛЯ БЕСПАРОЛЬНОГО ДОСТУПА" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

$SERVER = "85.192.56.74"
$USER = "root"
$SSH_DIR = "$env:USERPROFILE\.ssh"
$KEY_NAME = "linkflow_server_key"

# Создаем директорию .ssh если её нет
if (!(Test-Path $SSH_DIR)) {
    Write-Host "📁 Создаю директорию .ssh..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $SSH_DIR -Force
}

# Проверяем есть ли уже ключ
$PRIVATE_KEY = "$SSH_DIR\$KEY_NAME"
$PUBLIC_KEY = "$SSH_DIR\$KEY_NAME.pub"

if (Test-Path $PRIVATE_KEY) {
    Write-Host "⚠️ SSH ключ уже существует: $PRIVATE_KEY" -ForegroundColor Yellow
    $response = Read-Host "Хотите создать новый ключ? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "❌ Отменено пользователем" -ForegroundColor Red
        exit 1
    }
}

Write-Host "🔧 Генерирую новый SSH ключ..." -ForegroundColor Cyan

# Генерируем SSH ключ
ssh-keygen -t rsa -b 4096 -f $PRIVATE_KEY -N '""' -C "linkflow-deployment-key"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка генерации SSH ключа" -ForegroundColor Red
    exit 1
}

Write-Host "✅ SSH ключ создан: $PRIVATE_KEY" -ForegroundColor Green

# Читаем публичный ключ
if (!(Test-Path $PUBLIC_KEY)) {
    Write-Host "❌ Публичный ключ не найден: $PUBLIC_KEY" -ForegroundColor Red
    exit 1
}

$PUBLIC_KEY_CONTENT = Get-Content $PUBLIC_KEY -Raw
Write-Host "📋 Публичный ключ:" -ForegroundColor Cyan
Write-Host $PUBLIC_KEY_CONTENT -ForegroundColor White

Write-Host "`n🚀 Копирую публичный ключ на сервер..." -ForegroundColor Cyan
Write-Host "⚠️ Потребуется ввести пароль ПОСЛЕДНИЙ РАЗ" -ForegroundColor Yellow

# Копируем публичный ключ на сервер
$SSH_COPY_COMMAND = @"
mkdir -p ~/.ssh && 
chmod 700 ~/.ssh && 
echo '$PUBLIC_KEY_CONTENT' >> ~/.ssh/authorized_keys && 
chmod 600 ~/.ssh/authorized_keys && 
echo 'SSH ключ добавлен успешно'
"@

ssh $USER@$SERVER $SSH_COPY_COMMAND

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка копирования ключа на сервер" -ForegroundColor Red
    Write-Host "💡 Попробуйте скопировать ключ вручную:" -ForegroundColor Yellow
    Write-Host "ssh-copy-id -i $PUBLIC_KEY $USER@$SERVER" -ForegroundColor White
    exit 1
}

Write-Host "✅ Публичный ключ скопирован на сервер" -ForegroundColor Green

# Настраиваем SSH config для удобства
$SSH_CONFIG = "$SSH_DIR\config"
$CONFIG_ENTRY = @"

# LinkFlow Server Configuration
Host linkflow
    HostName $SERVER
    User $USER
    IdentityFile $PRIVATE_KEY
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

Host $SERVER
    User $USER
    IdentityFile $PRIVATE_KEY
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
"@

Add-Content -Path $SSH_CONFIG -Value $CONFIG_ENTRY
Write-Host "✅ SSH config обновлен: $SSH_CONFIG" -ForegroundColor Green

Write-Host "`n🧪 Тестирую беспарольное подключение..." -ForegroundColor Cyan

# Тестируем подключение
ssh -i $PRIVATE_KEY $USER@$SERVER "echo 'Беспарольное подключение работает!'"

if ($LASTEXITCODE -eq 0) {
    Write-Host "🎉 УСПЕХ! Беспарольное подключение настроено" -ForegroundColor Green
    
    Write-Host "`n📋 Теперь вы можете подключаться без пароля:" -ForegroundColor Cyan
    Write-Host "   ssh $USER@$SERVER" -ForegroundColor White
    Write-Host "   ssh linkflow" -ForegroundColor White
    Write-Host "   scp file.txt $USER@${SERVER}:/path/" -ForegroundColor White
    
    Write-Host "`n🔧 Обновляю скрипты развертывания..." -ForegroundColor Cyan
    
    # Обновляем deploy_optimized.sh для использования ключа
    if (Test-Path "deploy_optimized.sh") {
        $deployContent = Get-Content "deploy_optimized.sh" -Raw
        $deployContent = $deployContent -replace 'SERVER="root@85.192.56.74"', 'SERVER="linkflow"'
        Set-Content "deploy_optimized.sh" $deployContent
        Write-Host "✅ deploy_optimized.sh обновлен" -ForegroundColor Green
    }
    
    Write-Host "`n🎯 Готово! Теперь можно запускать:" -ForegroundColor Green
    Write-Host "   ./deploy_optimized.sh" -ForegroundColor White
    
} else {
    Write-Host "❌ Тест подключения не удался" -ForegroundColor Red
    Write-Host "💡 Проверьте настройки сервера или попробуйте вручную:" -ForegroundColor Yellow
    Write-Host "   ssh -i $PRIVATE_KEY $USER@$SERVER" -ForegroundColor White
}

Write-Host "`n📁 Файлы ключей:" -ForegroundColor Cyan
Write-Host "   Приватный: $PRIVATE_KEY" -ForegroundColor White
Write-Host "   Публичный: $PUBLIC_KEY" -ForegroundColor White
Write-Host "   SSH Config: $SSH_CONFIG" -ForegroundColor White

Write-Host "`n⚠️ ВАЖНО: Сохраните приватный ключ в безопасном месте!" -ForegroundColor Yellow