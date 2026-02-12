Установка и запуск проекта вручную 


Подготовка сервера
--------------------
sudo apt update
sudo apt -y upgrade

# базовые пакеты
sudo apt -y install python3 python3-pip python3-venv build-essential

# если вдруг venv не создаётся и ругается на ensurepip, поставь полный python:
# sudo apt -y install python3-full

Проходим в домашнюю директорию root:
   cd Nutrition
   python3 -m venv venv
   source venv/bin/activate
   pip install -U pip

Устанавливаем зависимости:
pip install -r requirements.txt

pip install "aiosqlite>=0.19,<1"
pip install "python-dotenv>=1.0,<2"
pip install "requests>=2.31,<3"

# опционально, но полезно на Linux — ускоряет event loop
pip install "uvloop>=0.19,<1"

Авот и всё, можно запускать бота:
python run.py 

!!!!!!!Внимание! когда нажмете старт в боте он ничего не покажет ! напишите в чате бота /admin чтобы увидеть меню админа и выберете пункт сменить приветственное фото! поставьте картинку и все потом /start

Если всё работает, то можно настроить автозапуск через systemd
Создаём systemd-сервис:
nano /etc/systemd/system/Nutrition.service

Вставляем в файл:

[Unit]
Description=Telegram Nutrition
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/Nutrition
Environment=PYTHONUNBUFFERED=1
ExecStart=/root/Nutrition/.venv/bin/python /root/Nutrition/run.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target

Сохраняем (Ctrl+O, Enter) и выходим (Ctrl+X)
Запускаем и добавляем в автозагрузку

   systemctl daemon-reload    # обновляем конфигурацию systemd
   systemctl start tgbotpay   # запускаем бота
   systemctl enable tgbotpay  # добавляем в автозагрузку

Проверяем статус
systemctl status tgbotpay -l
Если бот упал, то смотрим логи:
journalctl -u tgbotpay -f
# или последние 100 строк
journalctl -u tgbotpay -e -n 100 --no-pager
# или с поиском по слову ERROR
journalctl -u tgbotpay | grep ERROR
# или с поиском по слову WARNING
journalctl -u tgbotpay | grep WARNING
### Если бот работает через systemd, то при изменениях в коде или в .env нужно его остановить и перезапустить.
----------------------------------------
----------------------------------------

Все настройки конфигурации в файле .env
Настройки бота, токены, ключи, пароли, пути к файлам и т.д.

# Telegram
API_TOKEN=your_bot_token
CHANNEL_ID=-1001234567890 # ID канала (со знаком минус)
ADMIN_IDS=123456789,987654321  # ID админов через запятую
TEST_MODE=false
AUTO_DELETE_ENABLED=true

# Тексты/ссылки
CHANNEL_LINK=https://t.me/your_channel
WELCOME_TEXT= 
CHANNEL_TEXT=
SUPPORT_CONTACT=@uxnox
SUPPORT_TG_LINK=
SUPPORT_LINK=https://t.me/@uxnox
FAQ_URL=https://telegra.ph/CHasto-zadavaemye-voprosy-09-04-3 
CHANNEL_PHOTO=  # file_id или URL (опц.)
SUPPORT_PHOTO=  # опц.
ABOUT_TEXT=     # опц. если не хранишь в БД

# YooKassa
SHOP_ID=your_shop_id # Идентификатор магазина (shopId)
SECRET_KEY=sk_test_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX # Секретный ключ (secretKey)

# TON
TON_WALLET_ADDRESS=UQDOq_Rudxe334pGWbweUkHYqNG80K7xhhhWodM5EUZamSS5
TON_API_URL=https://toncenter.com/api/v2
TON_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
COINGECKO_API_URL=https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=rub

# Прочее
CHECK_INTERVAL=30
REMINDER_DAYS=1

# Stars (если нужно)
STARS_PROVIDER_TOKEN=



# любые изменения в .env требуют перезапуска бота
# systemctl restart tgbotpay
Если не работает то сначала останови:
# systemctl stop tgbotpay
# потом запусти вручную:
python run.py
Если ошибок нет, то останавливаем бота (Ctrl+C) и запускаем через systemd:
systemctl start tgbotpay

------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------    ------------

Настройки бота в админке
---------------------
Настройка тарифов
---------------------   
1. В админке нажимаем "Тарифы"
2. Добавляем тарифы, указываем цену, период (в днях), описание
или в файле tariffs.py
3. Сохраняем
4. Проверяем в боте
