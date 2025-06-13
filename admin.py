"""
Admin functionality for SPEAKYZ bot.
Handles admin commands and user management.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models import User, FAQ, Payment, get_db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

ADMIN_USERNAME = "prosto_993"
CARD_NUMBER = "9860 3501 0188 0457"

# Subscription prices in UZS
SUBSCRIPTION_PRICES = {
    "start": 0,  # Free basic plan
    "smart": 870000,
    "pro_plus": 1650000,
    "speaking_club": 190000
}

def is_admin(user):
    """Check if user is admin."""
    return user and user.username == ADMIN_USERNAME

async def admin_edit_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command to edit bot settings."""
    user = update.effective_user

    if not is_admin(user):
        await update.message.reply_text("❌ У вас нет прав администратора.")
        return

    keyboard = [
        [InlineKeyboardButton("📝 Управление FAQ", callback_data="admin_faq")],
        [InlineKeyboardButton("👥 Управление пользователями", callback_data="admin_users")],
        [InlineKeyboardButton("💰 Управление подписками", callback_data="admin_subscriptions")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🔧 **Панель администратора SPEAKYZ**\n\nВыберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle admin callback queries."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    if not is_admin(user):
        await query.edit_message_text("❌ У вас нет прав администратора.")
        return

    data = query.data

    if data == "admin_faq":
        await show_faq_management(query, context)
    elif data == "admin_users":
        await show_user_management(query, context)
    elif data == "admin_subscriptions":
        await show_subscription_management(query, context)
    elif data == "admin_stats":
        await show_admin_stats(query, context)
    elif data == "admin_back":
        await show_admin_main_menu(query, context)
    elif data.startswith("faq_"):
        await handle_faq_action(query, context, data)

async def show_admin_main_menu(query, context):
    """Show admin main menu."""
    keyboard = [
        [InlineKeyboardButton("📝 Управление FAQ", callback_data="admin_faq")],
        [InlineKeyboardButton("👥 Управление пользователями", callback_data="admin_users")],
        [InlineKeyboardButton("💰 Управление подписками", callback_data="admin_subscriptions")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🔧 **Панель администратора SPEAKYZ**\n\nВыберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_faq_management(query, context):
    """Show FAQ management interface."""
    db = get_db()
    if not db:
        await query.edit_message_text("❌ База данных недоступна.")
        return

    faqs = db.query(FAQ).filter(FAQ.is_active == True).all()
    db.close()

    text = "📝 **Управление FAQ**\n\n"
    keyboard = []

    for faq in faqs[:10]:  # Показываем только первые 10
        keyboard.append([InlineKeyboardButton(
            f"✏️ {faq.question[:30]}...", 
            callback_data=f"faq_edit_{faq.id}"
        )])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_back")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_user_management(query, context):
    """Show user management interface."""
    db = get_db()
    if not db:
        await query.edit_message_text("❌ База данных недоступна.")
        return

    user_count = db.query(User).count()
    active_subs = db.query(User).filter(User.subscription_type.isnot(None)).count()
    db.close()

    text = f"👥 **Управление пользователями**\n\n"
    text += f"Всего пользователей: {user_count}\n"
    text += f"Активных подписок: {active_subs}\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_subscription_management(query, context):
    """Show subscription management interface."""
    text = "💰 **Управление подписками**\n\n"
    text += "Для управления подписками используйте команды:\n"
    text += "/remove_subscription @username - удалить подписку\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_admin_stats(query, context):
    """Show admin statistics."""
    db = get_db()
    if not db:
        await query.edit_message_text("❌ База данных недоступна.")
        return

    try:
        total_users = db.query(User).count()
        active_subs = db.query(User).filter(User.subscription_type.isnot(None)).count()
        faq_count = db.query(FAQ).filter(FAQ.is_active == True).count()

        text = f"📊 **Статистика SPEAKYZ**\n\n"
        text += f"👥 Всего пользователей: {total_users}\n"
        text += f"💰 Активных подписок: {active_subs}\n"
        text += f"❓ FAQ записей: {faq_count}\n"

        db.close()
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        text = "❌ Ошибка получения статистики"
        if db:
            db.close()

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_faq_action(query, context, data):
    """Handle FAQ-related actions."""
    if data.startswith("faq_edit_"):
        faq_id = data.replace("faq_edit_", "")
        text = f"✏️ **Редактирование FAQ #{faq_id}**\n\n"
        text += "Для редактирования FAQ отправьте команду:\n"
        text += f"`/edit_faq {faq_id} Новый вопрос | Новый ответ`"

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_faq")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def remove_subscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove user subscription."""
    user = update.effective_user

    if not is_admin(user):
        await update.message.reply_text("❌ У вас нет прав администратора.")
        return

    if not context.args:
        await update.message.reply_text("Использование: /remove_subscription @username")
        return

    username = context.args[0].replace("@", "")

    db = get_db()
    if not db:
        await update.message.reply_text("❌ База данных недоступна.")
        return

    try:
        target_user = db.query(User).filter(User.username == username).first()

        if not target_user:
            await update.message.reply_text(f"❌ Пользователь @{username} не найден.")
            db.close()
            return

        target_user.subscription_type = None
        target_user.subscription_end = None
        target_user.speaking_clubs_count = 0
        db.commit()
        db.close()

        await update.message.reply_text(f"✅ Подписка пользователя @{username} удалена.")

    except Exception as e:
        logger.error(f"Error removing subscription: {e}")
        await update.message.reply_text("❌ Ошибка при удалении подписки.")
        if db:
            db.close()