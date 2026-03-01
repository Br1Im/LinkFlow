# BridgeAPI Bot - Статус развертывания

## Информация о боте

- **Имя бота**: @BridgeAPI_bot
- **API Token**: `8552546743:AAHvSFp01bGp3UbcWJt84FtG0WQtKF5pBEI`
- **Расположение на сервере**: `/root/BridgeAPI_Bot/`
- **Screen сессия**: `bridgeapi_bot`
- **PID процесса**: 474655
- **База данных**: `bridgeapi_bot.db`

## Статус

✅ Бот создан и запущен на сервере
✅ Все файлы скопированы из Axis_Bot
✅ Обновлены:
  - API токен
  - Название бота в приветственном сообщении
  - Название бота в пользовательском соглашении
  - Имя базы данных
  - README.md

## Функционал

Идентичен Axis_Bot:
- 💎 Платные каналы (стоимость 1500-3000₽ + 100₽/день ведение)
- 🤖 AI-инструменты (5-15₽)
- 🔮 Бесплатный гороскоп
- 💰 Баланс и пополнение
- 📄 Политика конфиденциальности
- 📋 Пользовательское соглашение

## Управление ботом

### Проверить статус
```bash
ssh root@85.192.56.74 "screen -ls"
```

### Остановить бота
```bash
ssh root@85.192.56.74 "screen -S bridgeapi_bot -X quit"
```

### Запустить бота
```bash
ssh root@85.192.56.74 "cd /root/BridgeAPI_Bot && screen -dmS bridgeapi_bot python3.11 run.py"
```

### Посмотреть процессы
```bash
ssh root@85.192.56.74 "ps aux | grep python3.11 | grep pts"
```

## Активные боты на сервере

1. **Axis_Bot** - @AxisPay_bot (PID 456324, pts/0)
2. **Very_Important_Bot** - @Very_iimportant_Bot (PID 470284, pts/1)
3. **BridgeAPI_Bot** - @BridgeAPI_bot (PID 474655, pts/2)
4. **Food Bot** - @nutrition_vip_bot (python3)
5. **Fit Bot** - @fitness_vip_robot (python3.11)
6. **Crypto Bot** - @crypto_vip_bot (python3.11)
7. **AI Bot** - @ai_vip_robot (python3.11)

## Дата создания

01.03.2026 22:10 (UTC)
