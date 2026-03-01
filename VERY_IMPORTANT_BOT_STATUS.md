# Very Important Bot - Статус развертывания

## Информация о боте

- **Имя бота**: @Very_iimportant_Bot
- **API Token**: `8625985451:AAFFqd2MLu0hLypjRiMnpIuE1DhFFNZk65I`
- **Расположение на сервере**: `/root/Very_Important_Bot/`
- **Screen сессия**: `very_important_bot`
- **PID процесса**: 470284
- **База данных**: `very_important_bot.db`

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
ssh root@85.192.56.74 "screen -S very_important_bot -X quit"
```

### Запустить бота
```bash
ssh root@85.192.56.74 "cd /root/Very_Important_Bot && screen -dmS very_important_bot python3.11 run.py"
```

### Посмотреть процессы
```bash
ssh root@85.192.56.74 "ps aux | grep python3.11 | grep pts"
```

## Активные боты на сервере

1. **Axis_Bot** - @AxisPay_bot (PID 456324, pts/0)
2. **Very_Important_Bot** - @Very_iimportant_Bot (PID 470284, pts/1)
3. **Food Bot** - @nutrition_vip_bot (python3)
4. **Fit Bot** - @fitness_vip_robot (python3.11)
5. **Crypto Bot** - @crypto_vip_bot (python3.11)
6. **AI Bot** - @ai_vip_robot (python3.11)

## Дата создания

01.03.2026 21:49 (UTC)
