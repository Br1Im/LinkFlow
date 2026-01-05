import logging
import os
import time
import asyncio
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, ConversationHandler, CallbackQueryHandler
)
from database import db
from keyboards import *
from config import BOT_TOKEN
from payment_service import warmup_for_user, create_payment_fast, is_browser_ready
from payment_automation import login_account

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

AMOUNT, ADD_ADMIN, ADD_ACCOUNT_PHONE, ADD_ACCOUNT_PASSWORD, ADD_REQUISITE_CARD, ADD_REQUISITE_NAME = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    if db.get_super_admin() is None:
        db.set_super_admin(user_id)
        await update.message.reply_text(
            f"🎉 Поздравляем, {user_name}!\n\n"
            "Вы назначены главным администратором системы.\n\n"
            "🔐 Ваши возможности:\n"
            "• Управление администраторами\n"
            "• Управление аккаунтами\n"
            "• Управление реквизитами\n"
            "• Создание платёжных ссылок\n\n"
            "Используйте кнопки меню для навигации 👇",
            reply_markup=main_menu_keyboard()
        )
        return
    
    if db.is_admin(user_id):
        role = "👑 Главный администратор" if db.is_super_admin(user_id) else "👤 Администратор"
        
        await update.message.reply_text(
            f"👋 Добро пожаловать, {user_name}!\n\n"
            f"Ваша роль: {role}\n\n"
            "🔹 Доступные функции:\n"
            "• 💳 Создание платёжных ссылок\n"
            "• ⚙️ Управление системой\n"
            "• 📊 Просмотр статистики\n\n"
            "Выберите действие из меню 👇",
            reply_markup=main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            f"👋 Здравствуйте, {user_name}!\n\n"
            "🔒 Этот бот предназначен для администраторов системы.\n\n"
            "Если вы хотите получить доступ, обратитесь к главному администратору.\n\n"
            f"Ваш ID: <code>{user_id}</code>",
            parse_mode='HTML'
        )

async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if not db.is_admin(user_id):
        await update.message.reply_text("❌ У вас нет доступа к этой функции.")
        return
    
    if text == "⚙️ Админ-панель":
        return await admin_panel(update, context)
    
    elif text == "📊 Аналитика":
        return await show_analytics(update, context)
    
    elif text == "ℹ️ Информация":
        admins_count = len(db.get_admins())
        accounts_count = len(db.get_accounts())
        requisites_count = len(db.get_requisites())
        
        stats = db.get_statistics()
        admin_stats = db.get_admin_statistics(user_id)
        
        role = "👑 Главный администратор" if db.is_super_admin(user_id) else "👤 Администратор"
        
        await update.message.reply_text(
            f"ℹ️ Информация о системе\n\n"
            f"Ваша роль: {role}\n"
            f"Ваш ID: <code>{user_id}</code>\n\n"
            f"📊 Общая статистика:\n"
            f"• Администраторов: {admins_count + 1}\n"
            f"• Аккаунтов: {accounts_count}\n"
            f"• Реквизитов: {requisites_count}\n"
            f"• Всего платежей: {stats['total_payments']}\n"
            f"• Общая сумма: {stats['total_amount']:,.0f} руб.\n\n"
            f"👤 Ваша статистика:\n"
            f"• Платежей: {admin_stats['count']}\n"
            f"• Сумма: {admin_stats['total_amount']:,.0f} руб.",
            parse_mode='HTML'
        )

async def show_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not db.is_admin(user_id):
        await update.message.reply_text("❌ У вас нет доступа.")
        return
    
    stats = db.get_statistics()
    payments = db.get_payments(limit=10)
    
    text = "📊 Детальная аналитика\n\n"
    text += f"💰 Общие показатели:\n"
    text += f"• Всего платежей: {stats['total_payments']}\n"
    text += f"• Общая сумма: {stats['total_amount']:,.0f} руб.\n"
    
    if stats['total_payments'] > 0:
        avg_amount = stats['total_amount'] / stats['total_payments']
        text += f"• Средний чек: {avg_amount:,.0f} руб.\n"
    
    text += f"\n📈 По реквизитам:\n"
    for req_key, req_data in stats['by_requisite'].items():
        text += f"\n💳 {req_data['card_number']}\n"
        text += f"   {req_data['owner_name']}\n"
        text += f"   Платежей: {req_data['count']}\n"
        text += f"   Сумма: {req_data['total_amount']:,.0f} руб.\n"
    
    text += f"\n👥 По администраторам:\n"
    for admin_id, admin_data in stats['by_admin'].items():
        text += f"\nID {admin_id}:\n"
        text += f"   Платежей: {admin_data['count']}\n"
        text += f"   Сумма: {admin_data['total_amount']:,.0f} руб.\n"
    
    if payments:
        text += f"\n📋 Последние 10 платежей:\n"
        for payment in reversed(payments):
            text += f"\n#{payment['id']} | {payment['date']} {payment['time']}\n"
            text += f"   Сумма: {payment['amount']:,.0f} руб.\n"
            text += f"   Админ: {payment['admin_id']}\n"
    
    await update.message.reply_text(text)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not db.is_admin(user_id):
        await update.message.reply_text("❌ У вас нет доступа к админ-панели.")
        return
    
    role = "Главный администратор" if db.is_super_admin(user_id) else "Администратор"
    
    await update.message.reply_text(
        f"🔐 Админ-панель\n\n"
        f"Ваша роль: {role}\n\n"
        f"Выберите действие:",
        reply_markup=main_admin_menu()
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if not db.is_admin(user_id):
        await query.edit_message_text("❌ У вас нет доступа.")
        return
    
    data = query.data
    
    if data == "close":
        await query.delete_message()
        return
    
    elif data == "back_to_main":
        await query.edit_message_text(
            "🔐 Админ-панель\n\nВыберите действие:",
            reply_markup=main_admin_menu()
        )
    
    elif data == "manage_admins":
        admins = db.get_admins()
        super_admin = db.get_super_admin()
        
        text = "👥 Управление администраторами\n\n"
        text += f"Главный админ: {super_admin}\n\n"
        text += f"Администраторы ({len(admins)}):\n"
        for admin_id in admins:
            text += f"• {admin_id}\n"
        
        await query.edit_message_text(text, reply_markup=admins_menu())
    
    elif data == "add_admin":
        context.user_data['action'] = 'add_admin'
        await query.edit_message_text(
            "➕ Добавление администратора\n\n"
            "Отправьте ID пользователя:",
            reply_markup=cancel_button()
        )
        return ADD_ADMIN
    
    elif data == "list_admins":
        admins = db.get_admins()
        text = "📋 Список администраторов:\n\n"
        
        for i, admin_id in enumerate(admins):
            text += f"{i+1}. ID: {admin_id}\n"
        
        if not admins:
            text += "Список пуст"
        
        await query.edit_message_text(text, reply_markup=back_button("manage_admins"))
    
    elif data == "manage_accounts":
        accounts = db.get_accounts()
        text = f"🔐 Управление аккаунтами\n\nВсего аккаунтов: {len(accounts)}"
        await query.edit_message_text(text, reply_markup=accounts_menu())
    
    elif data == "add_account":
        context.user_data['action'] = 'add_account'
        await query.edit_message_text(
            "➕ Добавление аккаунта\n\n"
            "Отправьте номер телефона (например: +79880260334):",
            reply_markup=cancel_button()
        )
        return ADD_ACCOUNT_PHONE
    
    elif data == "list_accounts":
        accounts = db.get_accounts()
        text = "📋 Список аккаунтов:\n\n"
        
        for i, acc in enumerate(accounts):
            status_emoji = {
                "online": "🟢",
                "offline": "🔴",
                "not_checked": "⚪",
                "error": "❌"
            }.get(acc.get('status', 'not_checked'), "⚪")
            
            text += f"{i+1}. {status_emoji} {acc['phone']}\n"
            if acc.get('last_check'):
                from datetime import datetime
                check_time = datetime.fromisoformat(acc['last_check']).strftime("%d.%m %H:%M")
                text += f"   Проверка: {check_time}\n"
        
        if not accounts:
            text += "Список пуст"
        
        await query.edit_message_text(text, reply_markup=back_button("manage_accounts"))
    
    elif data == "check_accounts_status":
        accounts = db.get_accounts()
        
        if not accounts:
            await query.edit_message_text(
                "❌ Нет аккаунтов для проверки",
                reply_markup=back_button("manage_accounts")
            )
            return
        
        await query.edit_message_text("🔄 Выполняю вход в аккаунты...\n\nЭто может занять 30-60 секунд")
        
        import asyncio
        
        results = []
        for i, acc in enumerate(accounts):
            await query.edit_message_text(
                f"🔄 Проверяю аккаунт {i+1}/{len(accounts)}...\n\n"
                f"📱 {acc['phone']}"
            )
            
            # Запускаем в отдельном потоке
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                login_account, 
                acc['phone'], 
                acc['password'], 
                acc['profile_path']
            )
            
            if result['status'] == 'online':
                db.update_account_status(i, 'online')
                results.append(f"🟢 {acc['phone']}: Авторизован")
            else:
                db.update_account_status(i, 'error', result['message'])
                results.append(f"❌ {acc['phone']}: {result['message']}")
        
        text = "📊 Результаты проверки:\n\n" + "\n".join(results)
        text += "\n\n✅ Теперь можно создавать платежи!"
        await query.edit_message_text(text, reply_markup=back_button("manage_accounts"))
    
    elif data == "manage_requisites":
        requisites = db.get_requisites()
        text = f"💳 Управление реквизитами\n\nВсего реквизитов: {len(requisites)}"
        await query.edit_message_text(text, reply_markup=requisites_menu())
    
    elif data == "add_requisite":
        context.user_data['action'] = 'add_requisite'
        await query.edit_message_text(
            "➕ Добавление реквизитов\n\n"
            "Отправьте номер карты (16 цифр):",
            reply_markup=cancel_button()
        )
        return ADD_REQUISITE_CARD
    
    elif data == "list_requisites":
        requisites = db.get_requisites()
        text = "📋 Список реквизитов:\n\n"
        
        for i, req in enumerate(requisites):
            text += f"{i+1}. {req['card_number']} - {req['owner_name']}\n"
        
        if not requisites:
            text += "Список пуст"
        
        await query.edit_message_text(text, reply_markup=back_button("manage_requisites"))
    
    elif data == "payment_mode":
        from payment_modes import mode_manager
        status = mode_manager.get_status()
        await query.edit_message_text(
            status,
            reply_markup=payment_mode_menu()
        )
    
    elif data == "set_mode_hybrid":
        from payment_modes import mode_manager, PaymentMode
        mode_manager.set_mode(PaymentMode.HYBRID)
        status = mode_manager.get_status()
        await query.edit_message_text(
            f"✅ Режим изменен на HYBRID (Быстрый)\n\n{status}",
            reply_markup=payment_mode_menu()
        )
    
    elif data == "set_mode_selenium":
        from payment_modes import mode_manager, PaymentMode
        mode_manager.set_mode(PaymentMode.SELENIUM)
        status = mode_manager.get_status()
        await query.edit_message_text(
            f"✅ Режим изменен на SELENIUM (Надежный)\n\n{status}",
            reply_markup=payment_mode_menu()
        )
    
    elif data == "toggle_auto_fallback":
        from payment_modes import mode_manager
        mode_manager.toggle_auto_fallback()
        status = mode_manager.get_status()
        await query.edit_message_text(
            f"✅ Настройка изменена\n\n{status}",
            reply_markup=payment_mode_menu()
        )
    
    elif data == "mode_status":
        from payment_modes import mode_manager
        status = mode_manager.get_status()
        await query.edit_message_text(
            status,
            reply_markup=payment_mode_menu()
        )
    
    elif data == "view_statistics":
        stats = db.get_statistics()
        
        text = "📊 Статистика системы\n\n"
        text += f"💰 Общие показатели:\n"
        text += f"• Всего платежей: {stats['total_payments']}\n"
        text += f"• Общая сумма: {stats['total_amount']:,.0f} руб.\n\n"
        
        text += f"📈 Топ реквизитов:\n"
        sorted_reqs = sorted(stats['by_requisite'].items(), 
                           key=lambda x: x[1]['total_amount'], 
                           reverse=True)[:5]
        
        for i, (req_key, req_data) in enumerate(sorted_reqs, 1):
            text += f"\n{i}. {req_data['card_number']}\n"
            text += f"   Платежей: {req_data['count']}\n"
            text += f"   Сумма: {req_data['total_amount']:,.0f} руб.\n"
        
        await query.edit_message_text(text, reply_markup=back_button("back_to_main"))
    
    elif data == "cancel":
        await query.edit_message_text(
            "❌ Операция отменена",
            reply_markup=back_button("back_to_main")
        )
        return ConversationHandler.END

async def add_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        admin_id = int(update.message.text.strip())
        
        if db.add_admin(admin_id):
            await update.message.reply_text(
                f"✅ Администратор {admin_id} успешно добавлен!",
                reply_markup=back_button("manage_admins")
            )
        else:
            await update.message.reply_text(
                f"⚠️ Пользователь {admin_id} уже является администратором",
                reply_markup=back_button("manage_admins")
            )
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат ID. Отправьте числовой ID:",
            reply_markup=cancel_button()
        )
        return ADD_ADMIN
    
    return ConversationHandler.END

async def add_account_phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    context.user_data['account_phone'] = phone
    
    await update.message.reply_text(
        f"✅ Телефон: {phone}\n\n"
        "Теперь отправьте пароль:",
        reply_markup=cancel_button()
    )
    return ADD_ACCOUNT_PASSWORD

async def add_account_password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    phone = context.user_data.get('account_phone')
    
    index = db.add_account(phone, password)
    
    await update.message.reply_text(
        "🔄 Выполняю вход в аккаунт...\n\n"
        "Это может занять 20-30 секунд"
    )
    
    import asyncio
    
    account = db.get_account(index)
    
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, 
        login_account, 
        phone, 
        password, 
        account['profile_path']
    )
    
    if result['status'] == 'online':
        db.update_account_status(index, 'online')
        await update.message.reply_text(
            f"✅ Аккаунт успешно добавлен и авторизован!\n\n"
            f"📱 Телефон: {phone}\n"
            f"🟢 Статус: Онлайн\n\n"
            f"Теперь можно создавать платежи!",
            reply_markup=back_button("manage_accounts")
        )
    else:
        db.update_account_status(index, 'error', result['message'])
        await update.message.reply_text(
            f"⚠️ Аккаунт добавлен, но вход не удался:\n\n"
            f"📱 Телефон: {phone}\n"
            f"❌ Ошибка: {result['message']}\n\n"
            f"Проверьте логин и пароль",
            reply_markup=back_button("manage_accounts")
        )
    
    return ConversationHandler.END

async def add_requisite_card_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    card = update.message.text.strip()
    
    if not card.isdigit() or len(card) != 16:
        await update.message.reply_text(
            "❌ Неверный формат номера карты!\n\n"
            "Отправьте 16 цифр:",
            reply_markup=cancel_button()
        )
        return ADD_REQUISITE_CARD
    
    context.user_data['requisite_card'] = card
    
    await update.message.reply_text(
        f"✅ Номер карты: {card}\n\n"
        "Теперь отправьте ФИО владельца:",
        reply_markup=cancel_button()
    )
    return ADD_REQUISITE_NAME

async def add_requisite_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    card = context.user_data.get('requisite_card')
    
    db.add_requisite(card, name)
    
    await update.message.reply_text(
        f"✅ Реквизиты успешно добавлены!\n\n"
        f"Карта: {card}\n"
        f"Владелец: {name}",
        reply_markup=back_button("manage_requisites")
    )
    
    return ConversationHandler.END

async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Создание платежей отменено",
        reply_markup=admin_keyboard()
    )
    return ConversationHandler.END

async def pay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not db.is_admin(user_id):
        await update.message.reply_text("❌ У вас нет доступа к этой команде.")
        return
    
    requisites = db.get_requisites()
    
    if not requisites:
        await update.message.reply_text(
            "❌ Нет доступных реквизитов!\n\n"
            "Добавьте реквизиты через /admin"
        )
        return
    
    context.user_data.clear()
    
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, warmup_for_user, user_id)
    
    await update.message.reply_text(
        "💰 Создание ссылки для оплаты\n\n"
        "Введите сумму (1000-100000 руб.):"
    )
    
    return AMOUNT

async def amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"\n{'='*60}", flush=True)
    print(f"📥 ПОЛУЧЕНО СООБЩЕНИЕ С СУММОЙ", flush=True)
    print(f"{'='*60}\n", flush=True)
    
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    try:
        amount_value = float(text)
        
        if amount_value < 1000:
            await update.message.reply_text(
                "❌ Сумма слишком мала!\n\n"
                "Минимальная сумма: 1000 руб.\n"
                "Введите другую сумму или /cancel для выхода"
            )
            return AMOUNT
        
        if amount_value > 100000:
            await update.message.reply_text(
                "❌ Сумма слишком велика!\n\n"
                "Максимальная сумма: 100000 руб.\n"
                "Введите другую сумму или /cancel для выхода"
            )
            return AMOUNT
            
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат! Введите число:\n"
            "Или /cancel для выхода"
        )
        return AMOUNT
    
    requisites = db.get_requisites()
    requisite = requisites[0]
    
    status_msg = await update.message.reply_text(
        "⏳ Создаю платёжную ссылку...\n\n"
        "Это займёт 3-5 секунд"
    )
    
    start_time = time.time()
    payment_sent = False
    
    # Callback для МГНОВЕННОЙ отправки
    async def send_to_user(payment_link, qr_file_path):
        nonlocal payment_sent
        if payment_sent:
            return
        payment_sent = True
        
        elapsed = time.time() - start_time
        
        payment_id = db.add_payment(
            admin_id=user_id,
            card_number=requisite['card_number'],
            owner_name=requisite['owner_name'],
            amount=float(text),
            payment_link=payment_link
        )
        
        await status_msg.delete()
        
        response = (
            f"✅ Платёж #{payment_id} создан!\n\n"
            f"💳 Карта: {requisite['card_number']}\n"
            f"👤 Владелец: {requisite['owner_name']}\n"
            f"💰 Сумма: {text} руб.\n"
            f"⏱ Время: {elapsed:.1f} сек\n\n"
            f"🔗 {payment_link}"
        )
        
        with open(qr_file_path, 'rb') as qr_file:
            await update.message.reply_photo(photo=qr_file, caption=response)
        
        try:
            os.remove(qr_file_path)
        except:
            pass
        
        await update.message.reply_text(
            "💰 Введите следующую сумму (1000-100000 руб.)\n"
            "или /cancel для выхода"
        )
    
    try:
        loop = asyncio.get_event_loop()
        
        # Создаем wrapper для callback
        def sync_callback(payment_link, qr_file_path):
            asyncio.run_coroutine_threadsafe(
                send_to_user(payment_link, qr_file_path),
                loop
            )
        
        result = await loop.run_in_executor(
            None,
            create_payment_fast,
            text,
            sync_callback
        )
        
        if "error" in result and not payment_sent:
            elapsed_time = result.get('elapsed_time', time.time() - start_time)
            error_msg = result['error']
            
            print(f"⚠️ Ошибка платежа: {error_msg}", flush=True)
            print("🔄 Пытаюсь восстановить браузер...", flush=True)
            
            loop = asyncio.get_event_loop()
            warmup_result = await loop.run_in_executor(None, warmup_for_user, user_id)
            
            if warmup_result.get('success'):
                await status_msg.edit_text(
                    f"⚠️ Браузер был восстановлен\n\n"
                    f"Введите сумму снова:"
                )
            else:
                await status_msg.edit_text(
                    f"❌ Ошибка при создании платежа\n\n"
                    f"Детали: {error_msg}\n"
                    f"⏱ Время: {elapsed_time:.1f} сек\n\n"
                    f"Введите сумму снова или /cancel для выхода"
                )
            return AMOUNT
    
    except Exception as e:
        if not payment_sent:
            elapsed_time = time.time() - start_time
            error_trace = str(e)
            print(f"❌ ОШИБКА: {error_trace}", flush=True)
            
            print("🔄 Пытаюсь восстановить браузер...", flush=True)
            loop = asyncio.get_event_loop()
            warmup_result = await loop.run_in_executor(None, warmup_for_user, user_id)
            
            if warmup_result.get('success'):
                await status_msg.edit_text(
                    f"⚠️ Браузер был восстановлен\n\n"
                    f"Введите сумму снова:"
                )
            else:
                await status_msg.edit_text(
                    f"❌ Ошибка\n\n"
                    f"Детали: {error_trace}\n"
                    f"⏱ Время: {elapsed_time:.1f} сек\n\n"
                    f"Введите сумму снова или /cancel для выхода"
                )
            return AMOUNT
    
    return AMOUNT


async def auto_check_accounts():
    accounts = db.get_accounts()
    
    if not accounts:
        print("⚠️ Нет аккаунтов для проверки", flush=True)
        return
    
    print(f"\n{'='*60}", flush=True)
    print(f"🔄 АВТОМАТИЧЕСКАЯ ПРОВЕРКА АККАУНТОВ", flush=True)
    print(f"Всего аккаунтов: {len(accounts)}", flush=True)
    print(f"{'='*60}\n", flush=True)
    
    for i, acc in enumerate(accounts):
        print(f"\n📱 Проверяю аккаунт {i+1}/{len(accounts)}: {acc['phone']}", flush=True)
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            login_account,
            acc['phone'],
            acc['password'],
            acc['profile_path']
        )
        
        if result['status'] == 'online':
            db.update_account_status(i, 'online')
            print(f"✅ {acc['phone']}: Авторизован", flush=True)
        else:
            db.update_account_status(i, 'error', result['message'])
            print(f"❌ {acc['phone']}: {result['message']}", flush=True)
    
    print(f"\n{'='*60}", flush=True)
    print(f"✅ ПРОВЕРКА ЗАВЕРШЕНА", flush=True)
    print(f"{'='*60}\n", flush=True)


async def periodic_account_check(interval_minutes=30):
    while True:
        await asyncio.sleep(interval_minutes * 60)
        print(f"\n⏰ Запуск периодической проверки аккаунтов...", flush=True)
        await auto_check_accounts()


async def periodic_browser_check(interval_minutes=5):
    """Периодическая проверка и восстановление браузера"""
    while True:
        await asyncio.sleep(interval_minutes * 60)
        print(f"\n🔍 Проверка состояния браузера...", flush=True)
        
        from payment_service import browser_manager
        
        if not browser_manager.is_ready or not browser_manager.driver:
            print("⚠️ Браузер не готов, восстанавливаю...", flush=True)
            loop = asyncio.get_event_loop()
            warmup_result = await loop.run_in_executor(None, warmup_for_user, SUPER_ADMIN_ID)
            
            if warmup_result.get('success'):
                print("✅ Браузер восстановлен!", flush=True)
            else:
                print("❌ Не удалось восстановить браузер", flush=True)
        else:
            print("✅ Браузер в порядке", flush=True)


async def post_init(application):
    print("\n🔐 Запускаю автоматическую проверку аккаунтов...", flush=True)
    await auto_check_accounts()
    
    print("\n🔥 Прогреваю браузер для быстрых платежей...", flush=True)
    loop = asyncio.get_event_loop()
    warmup_result = await loop.run_in_executor(None, warmup_for_user, SUPER_ADMIN_ID)
    
    if warmup_result.get('success'):
        print("✅ Браузер прогрет и готов к работе!", flush=True)
    else:
        print("⚠️ Не удалось прогреть браузер, будет прогрет при первом платеже", flush=True)
    
    asyncio.create_task(periodic_account_check(30))
    print("⏰ Периодическая проверка аккаунтов запущена (каждые 30 минут)", flush=True)
    
    asyncio.create_task(periodic_browser_check(5))
    print("🔍 Периодическая проверка браузера запущена (каждые 5 минут)", flush=True)


def main():
    print("🚀 Запуск платёжного бота...")
    print("✅ Система готова к работе!")
    
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    pay_conv = ConversationHandler(
        entry_points=[
            CommandHandler('pay', pay_command),
            MessageHandler(filters.Text(['💳 Создать ссылку']), pay_command)
        ],
        states={
            AMOUNT: [
                MessageHandler(filters.Text(['💳 Создать ссылку']), pay_command),
                MessageHandler(filters.TEXT & ~filters.COMMAND, amount_handler)
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_payment),
            MessageHandler(filters.Text(['💳 Создать ссылку']), pay_command)
        ],
    )
    
    admin_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback)],
        states={
            ADD_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_admin_handler)],
            ADD_ACCOUNT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_account_phone_handler)],
            ADD_ACCOUNT_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_account_password_handler)],
            ADD_REQUISITE_CARD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_requisite_card_handler)],
            ADD_REQUISITE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_requisite_name_handler)],
        },
        fallbacks=[CallbackQueryHandler(button_callback)],
    )
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('admin', admin_panel))
    application.add_handler(pay_conv)
    application.add_handler(admin_conv)
    application.add_handler(MessageHandler(filters.Text(['⚙️ Админ-панель', 'ℹ️ Информация', '📊 Аналитика']), handle_menu_buttons))
    
    print("✅ Бот запущен и готов к работе!")
    application.run_polling()


if __name__ == '__main__':
    main()
