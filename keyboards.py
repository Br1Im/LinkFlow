from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    keyboard = [
        [KeyboardButton("💳 Создать ссылку")],
        [KeyboardButton("📊 Аналитика"), KeyboardButton("⚙️ Админ-панель")],
        [KeyboardButton("ℹ️ Информация")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def main_admin_menu():
    keyboard = [
        [InlineKeyboardButton("👥 Управление админами", callback_data="manage_admins")],
        [InlineKeyboardButton("🔐 Управление аккаунтами", callback_data="manage_accounts")],
        [InlineKeyboardButton("💳 Управление реквизитами", callback_data="manage_requisites")],
        [InlineKeyboardButton("📊 Статистика", callback_data="view_statistics")],
        [InlineKeyboardButton("❌ Закрыть", callback_data="close")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admins_menu():
    keyboard = [
        [InlineKeyboardButton("➕ Добавить админа", callback_data="add_admin")],
        [InlineKeyboardButton("📋 Список админов", callback_data="list_admins")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def accounts_menu():
    keyboard = [
        [InlineKeyboardButton("➕ Добавить аккаунт", callback_data="add_account")],
        [InlineKeyboardButton("📋 Список аккаунтов", callback_data="list_accounts")],
        [InlineKeyboardButton("🔄 Проверить статус", callback_data="check_accounts_status")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def requisites_menu():
    keyboard = [
        [InlineKeyboardButton("➕ Добавить реквизиты", callback_data="add_requisite")],
        [InlineKeyboardButton("📋 Список реквизитов", callback_data="list_requisites")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def delete_item_keyboard(item_type: str, index: int):
    keyboard = [
        [InlineKeyboardButton("🗑 Удалить", callback_data=f"delete_{item_type}_{index}")],
        [InlineKeyboardButton("🔙 Назад", callback_data=f"manage_{item_type}s")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_button(callback: str):
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data=callback)]]
    return InlineKeyboardMarkup(keyboard)

def cancel_button():
    keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data="cancel")]]
    return InlineKeyboardMarkup(keyboard)
