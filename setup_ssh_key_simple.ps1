# Setup SSH key for passwordless access
Write-Host "Setting up SSH key for passwordless access..." -ForegroundColor Green

$SERVER = "85.192.56.74"
$USER = "root"
$SSH_DIR = "$env:USERPROFILE\.ssh"
$KEY_NAME = "linkflow_server_key"

# Create .ssh directory if it doesn't exist
if (!(Test-Path $SSH_DIR)) {
    Write-Host "Creating .ssh directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $SSH_DIR -Force
}

$PRIVATE_KEY = "$SSH_DIR\$KEY_NAME"
$PUBLIC_KEY = "$SSH_DIR\$KEY_NAME.pub"

# Generate SSH key
Write-Host "Generating SSH key..." -ForegroundColor Cyan
ssh-keygen -t rsa -b 4096 -f $PRIVATE_KEY -N '""' -C "linkflow-deployment-key"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error generating SSH key" -ForegroundColor Red
    exit 1
}

Write-Host "SSH key created: $PRIVATE_KEY" -ForegroundColor Green

# Read public key
$PUBLIC_KEY_CONTENT = Get-Content $PUBLIC_KEY -Raw
Write-Host "Public key:" -ForegroundColor Cyan
Write-Host $PUBLIC_KEY_CONTENT -ForegroundColor White

Write-Host "Copying public key to server..." -ForegroundColor Cyan
Write-Host "You will need to enter password ONE LAST TIME" -ForegroundColor Yellow

# Copy public key to server
$SSH_COPY_COMMAND = "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$PUBLIC_KEY_CONTENT' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo 'SSH key added successfully'"

ssh $USER@$SERVER $SSH_COPY_COMMAND

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error copying key to server" -ForegroundColor Red
    exit 1
}

Write-Host "Public key copied to server successfully" -ForegroundColor Green

# Update SSH config
$SSH_CONFIG = "$SSH_DIR\config"
$CONFIG_ENTRY = @"

# LinkFlow Server Configuration
Host linkflow
    HostName $SERVER
    User $USER
    IdentityFile $PRIVATE_KEY
    StrictHostKeyChecking no

Host $SERVER
    User $USER
    IdentityFile $PRIVATE_KEY
    StrictHostKeyChecking no
"@

Add-Content -Path $SSH_CONFIG -Value $CONFIG_ENTRY
Write-Host "SSH config updated: $SSH_CONFIG" -ForegroundColor Green

# Test connection
Write-Host "Testing passwordless connection..." -ForegroundColor Cyan
ssh -i $PRIVATE_KEY $USER@$SERVER "echo 'Passwordless connection works!'"

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS! Passwordless connection configured" -ForegroundColor Green
    Write-Host "You can now connect without password:" -ForegroundColor Cyan
    Write-Host "  ssh $USER@$SERVER" -ForegroundColor White
    Write-Host "  ssh linkflow" -ForegroundColor White
} else {
    Write-Host "Connection test failed" -ForegroundColor Red
}

Write-Host "Key files:" -ForegroundColor Cyan
Write-Host "  Private: $PRIVATE_KEY" -ForegroundColor White
Write-Host "  Public: $PUBLIC_KEY" -ForegroundColor White