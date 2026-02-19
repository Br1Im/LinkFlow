# Базовая стоимость курса: 1500 рублей
# Дополнительно: 100 рублей/сутки персональное ведение (макс 15 дней)
# Итого: от 1500 до 3000 рублей

TARIFFS = {
    'custom': {
        'price': 1500,  # Базовая цена
        'stars': 750,   # Для Telegram Stars (если используется)
        'duration': 'Курс',
        'seconds': 2592000,  # 30 дней базовый доступ
    },
}

# Функция для расчета стоимости и длительности на основе введенной суммы
def calculate_tariff(amount):
    """
    Рассчитывает длительность подписки на основе суммы оплаты
    1500 руб = базовый курс (30 дней)
    Каждые 100 руб сверх 1500 = +1 день персонального ведения (макс 15 дней)
    """
    base_price = 1500
    daily_price = 100
    max_extra_days = 15
    base_days = 30
    
    if amount < base_price:
        return None  # Недостаточная сумма
    
    if amount > 3000:
        amount = 3000  # Максимум 3000 рублей
    
    extra_amount = amount - base_price
    extra_days = min(extra_amount // daily_price, max_extra_days)
    
    total_days = base_days + extra_days
    total_seconds = total_days * 86400
    
    if extra_days == 0:
        duration_text = "Базовый курс (30 дней)"
    else:
        duration_text = f"Курс + {extra_days} дней персонального ведения"
    
    return {
        'price': amount,
        'duration': duration_text,
        'seconds': total_seconds,
        'extra_days': extra_days
    }
