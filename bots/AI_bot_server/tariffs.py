def calculate_tariff(amount):
    """
    Рассчитывает тариф на основе введённой суммы.
    Базовая стоимость: 2000 рублей
    Дополнительно: 100 рублей/сутки персональное ведение (макс. 20 дней)
    Диапазон: 2000-4000 рублей
    """
    if amount < 2000:
        return None, "Минимальная сумма — 2000 рублей"
    if amount > 4000:
        return None, "Максимальная сумма — 4000 рублей"
    
    base_price = 2000
    daily_price = 100
    max_days = 20
    
    extra_amount = amount - base_price
    days = extra_amount // daily_price
    
    if days > max_days:
        return None, f"Максимум {max_days} дней персонального ведения"
    
    # Создаём описание тарифа
    if days == 0:
        description = "Базовый курс (без персонального ведения)"
        duration_text = "1 месяц"
    else:
        description = f"Базовый курс + {days} дней персонального ведения"
        duration_text = "1 месяц"
    
    return {
        'price': amount,
        'stars': amount // 2,  # Примерно половина в Stars
        'duration': duration_text,
        'seconds': 2592000,  # 30 дней
        'description': description,
        'days': days
    }, None


# Для совместимости со старым кодом
TARIFFS = {
    '1 месяц': {
        'price': 2000,
        'stars': 1000,
        'duration': '1 month',
        'seconds': 2592000,  # 30 дней
    },
}
