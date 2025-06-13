"""
SPEAKYZ Telegram bot with full functionality.
Includes admin panel, FAQ, subscription management, and keep-alive system.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN, WEBSITE_URL, WELCOME_MESSAGE, BUTTON_TEXT, FAQ_URL
from models import create_tables, init_default_faq, User, get_db
from admin import (admin_edit_bot, handle_admin_callback, remove_subscription_command, 
                  is_admin, SUBSCRIPTION_PRICES)
from faq_site import start_faq_site
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def register_or_update_user(telegram_user):
    """Register or update user in database."""
    db = get_db()

    user = db.query(User).filter(User.telegram_id == telegram_user.id).first()

    if not user:
        # Create new user
        user = User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name
        )
        db.add(user)
    else:
        # Update existing user
        user.username = telegram_user.username
        user.first_name = telegram_user.first_name
        user.last_name = telegram_user.last_name
        user.updated_at = datetime.utcnow()

    db.commit()
    db.close()
    return user

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.
    Sends welcome message with school photo and website button.
    """
    try:
        user = update.effective_user

        # Register or update user
        register_or_update_user(user)

        # Create keyboard with main options
        keyboard = [
            [InlineKeyboardButton("🎓 Наши тарифы", callback_data="show_plans")],
            [InlineKeyboardButton("❓ FAQ", callback_data="show_faq")],
            [InlineKeyboardButton("👤 Мой профиль", callback_data="my_profile")],
            [InlineKeyboardButton(BUTTON_TEXT, url=WEBSITE_URL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        logger.info(f"User {user.id} ({user.first_name}) started the bot")

        # Send photo with caption and buttons
        try:
            with open('attached_assets/IMG_20250605_114549_367.jpg', 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=WELCOME_MESSAGE,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        except FileNotFoundError:
            # Fallback to text message if image not found
            await update.message.reply_text(
                WELCOME_MESSAGE,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        logger.info(f"Welcome message with photo sent to user {user.id}")

    except Exception as e:
        logger.error(f"Error in start_command: {e}")
        await update.message.reply_text(
            "Извините, произошла ошибка. Попробуйте позже или обратитесь в поддержку."
        )

async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show subscription plans."""
    query = update.callback_query
    await query.answer()

    text = "🎓 **Тарифы SPEAKYZ**\n\n"
    text += "🆓 **Базовый — Start**\n"
    text += "✅ 2 групповых занятия в неделю\n"
    text += "✅ Учебные материалы и доступ к платформе\n"
    text += "✅ Домашние задания с проверкой\n"
    text += "❌ Без разговорной практики с носителем\n"
    text += "📚 +40–60 новых слов / месяц\n\n"

    text += "⭐ **Продвинутый — Smart**\n"
    text += "✅ 2 групповых + 1 разговорный клуб в неделю\n"
    text += "✅ Проверка ДЗ с обратной связью\n"
    text += "✅ Чат с преподавателем\n"
    text += "📚 +80–120 новых слов / месяц\n"
    text += "💰 870,000 UZS / месяц\n\n"

    text += "🌟 **Премиум — Pro+**\n"
    text += "✅ 2 индивидуальных + 2 групповых занятия\n"
    text += "✅ Персональный преподаватель\n"
    text += "✅ Подготовка к IELTS / TOEFL\n"
    text += "✅ Поддержка 24/7\n"
    text += "📚 +150–200 новых слов / месяц\n"
    text += "💰 1,650,000 UZS / месяц\n\n"

    text += "💬 **Разговорный клуб**\n"
    text += "✅ 1 встреча в неделю\n"
    text += "✅ Тематические дискуссии\n"
    text += "📚 +20–30 новых слов / месяц\n"
    text += "💰 190,000 UZS / месяц"

    keyboard = [
        [InlineKeyboardButton("💳 Купить подписку", callback_data="buy_subscription")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_caption(caption=text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show FAQ website link."""
    query = update.callback_query
    await query.answer()

    text = "❓ **Часто задаваемые вопросы**\n\n"
    text += "Полный список ответов на популярные вопросы доступен на нашем сайте:\n"
    text += f"{FAQ_URL}\n\n"
    text += "Там вы найдете информацию о:\n"
    text += "• Процессе обучения\n"
    text += "• Тарифах и оплате\n"
    text += "• Возврате средств\n"
    text += "• И многое другое!"

    keyboard = [
        [InlineKeyboardButton("🌐 Открыть FAQ", url=FAQ_URL)],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_caption(caption=text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user profile."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    db = get_db()
    db_user = db.query(User).filter(User.telegram_id == user.id).first()
    db.close()

    if not db_user:
        text = "❌ Профиль не найден. Используйте /start для регистрации."
    else:
        text = f"👤 **Ваш профиль**\n\n"
        text += f"Имя: {db_user.first_name or 'Не указано'}\n"
        text += f"Username: @{db_user.username or 'Не указан'}\n\n"

        if db_user.subscription_type:
            sub_name = {
                'start': 'Базовый (Start)',
                'smart': 'Продвинутый (Smart)', 
                'pro_plus': 'Премиум (Pro+)',
                'speaking_club': 'Разговорный клуб'
            }.get(db_user.subscription_type, db_user.subscription_type)

            text += f"📋 Подписка: {sub_name}\n"
            if db_user.subscription_end:
                text += f"📅 Действует до: {db_user.subscription_end.strftime('%d.%m.%Y')}\n"
            if db_user.speaking_clubs_count > 0:
                text += f"💬 Разговорных клубов: {db_user.speaking_clubs_count}\n"
        else:
            text += "📋 Подписка: Не активна\n"

    keyboard = [
        [InlineKeyboardButton("💳 Купить подписку", callback_data="buy_subscription")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_caption(caption=text, reply_markup=reply_markup, parse_mode='Markdown')

async def buy_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show subscription purchase options."""
    query = update.callback_query
    await query.answer()

    text = "💳 **Оплата подписки**\n\n"
    text += "Для оплаты переведите нужную сумму на карту Humo:\n"
    text += "`9860 3501 0188 0457`\n\n"
    text += "**Тарифы:**\n"
    text += "• Smart: 870,000 UZS\n"
    text += "• Pro+: 1,650,000 UZS\n"
    text += "• Разговорный клуб: 190,000 UZS\n\n"
    text += "После перевода ваша подписка активируется автоматически!\n\n"
    text += "❓ **Проблемы с оплатой?**\n"
    text += "Обратитесь в поддержку: @Dream565758"

    keyboard = [
        [InlineKeyboardButton("🔙 Назад к тарифам", callback_data="show_plans")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_caption(caption=text, reply_markup=reply_markup, parse_mode='Markdown')

async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /faq command."""
    keyboard = [
        [InlineKeyboardButton("🌐 Открыть FAQ сайт", url=FAQ_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "❓ **FAQ - Часто задаваемые вопросы**\n\nПереходите на наш сайт с полным списком ответов:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return to main menu from callback query."""
    query = update.callback_query
    await query.answer()

    user = query.from_user

    # Register or update user
    register_or_update_user(user)

    # Create keyboard with main options
    keyboard = [
        [InlineKeyboardButton("🎓 Наши тарифы", callback_data="show_plans")],
        [InlineKeyboardButton("❓ FAQ", callback_data="show_faq")],
        [InlineKeyboardButton("👤 Мой профиль", callback_data="my_profile")],
        [InlineKeyboardButton(BUTTON_TEXT, url=WEBSITE_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        # Check if message has photo (caption) or text
        if query.message.photo:
            await query.edit_message_caption(
                caption=WELCOME_MESSAGE,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                text=WELCOME_MESSAGE,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        # Fallback: delete and send new message
        try:
            await query.delete_message()
            try:
                with open('attached_assets/IMG_20250605_114549_367.jpg', 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo,
                        caption=WELCOME_MESSAGE,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
            except FileNotFoundError:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=WELCOME_MESSAGE,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        except Exception as e2:
            logger.error(f"Error in fallback: {e2}")
            await query.message.reply_text("Произошла ошибка. Попробуйте /start")

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all callback queries."""
    query = update.callback_query
    data = query.data

    try:
        # Admin callbacks
        if data.startswith("admin_"):
            await handle_admin_callback(update, context)
            return

        # Main bot callbacks
        if data == "show_plans":
            await show_plans(update, context)
        elif data == "show_faq":
            await show_faq(update, context)
        elif data == "my_profile":
            await show_profile(update, context)
        elif data == "buy_subscription":
            await buy_subscription(update, context)
        elif data == "back_to_main":
            await back_to_main(update, context)
        else:
            await query.answer("Неизвестная команда")
    except Exception as e:
        logger.error(f"Error in callback query handler: {e}")
        await query.answer("Произошла ошибка. Попробуйте еще раз.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    user = update.effective_user
    help_text = """
🤖 **Команды SPEAKYZ бота:**

/start - Главное меню
/faq - Часто задаваемые вопросы
/help - Это сообщение

📞 **Поддержка:**
@Dream565758

🌐 **Сайт школы:**
https://sites.google.com/view/wwwspeakzycom
    """

    # Add admin commands for admin users
    if is_admin(user):
        help_text += "\n\n🔧 **Команды администратора:**\n"
        help_text += "/admineditbot - Панель администратора\n"
        help_text += "/remove_subscription @username - Удалить подписку"

    await update.message.reply_text(help_text, parse_mode='Markdown')

async def add_faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add new FAQ entry."""
    user = update.effective_user

    if not is_admin(user):
        await update.message.reply_text("❌ У вас нет прав администратора.")
        return

    if not context.args:
        await update.message.reply_text("Использование: /add_faq Вопрос | Ответ")
        return

    text = " ".join(context.args)
    if "|" not in text:
        await update.message.reply_text("Неправильный формат. Используйте: /add_faq Вопрос | Ответ")
        return

    question, answer = text.split("|", 1)
    question = question.strip()
    answer = answer.strip()

    if not question or not answer:
        await update.message.reply_text("Вопрос и ответ не могут быть пустыми.")
        return

    try:
        from models import FAQ
        db = get_db()
        new_faq = FAQ(question=question, answer=answer, created_by=user.id)
        db.add(new_faq)
        db.commit()
        db.close()

        await update.message.reply_text(f"✅ FAQ добавлен:\n\n**Вопрос:** {question}\n**Ответ:** {answer}", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error adding FAQ: {e}")
        await update.message.reply_text("❌ Ошибка при добавлении FAQ.")

async def edit_faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Edit existing FAQ entry."""
    user = update.effective_user

    if not is_admin(user):
        await update.message.reply_text("❌ У вас нет прав администратора.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Использование: /edit_faq ID Новый вопрос | Новый ответ")
        return

    try:
        faq_id = int(context.args[0])
        text = " ".join(context.args[1:])

        if "|" not in text:
            await update.message.reply_text("Неправильный формат. Используйте: /edit_faq ID Вопрос | Ответ")
            return

        question, answer = text.split("|", 1)
        question = question.strip()
        answer = answer.strip()

        from models import FAQ
        db = get_db()
        faq = db.query(FAQ).filter(FAQ.id == faq_id).first()

        if not faq:
            await update.message.reply_text(f"❌ FAQ с ID {faq_id} не найден.")
            db.close()
            return

        faq.question = question
        faq.answer = answer
        db.commit()
        db.close()

        await update.message.reply_text(f"✅ FAQ обновлен:\n\n**Вопрос:** {question}\n**Ответ:** {answer}", parse_mode='Markdown')

    except ValueError:
        await update.message.reply_text("❌ Неправильный ID FAQ.")
    except Exception as e:
        logger.error(f"Error editing FAQ: {e}")
        await update.message.reply_text("❌ Ошибка при редактировании FAQ.")

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.message.reply_text(
        "Извините, я не понимаю эту команду. Используйте /start для начала или /help для получения помощи."
    )

def start_bot():
    """
    Initialize and start the Telegram bot with full functionality.
    """
    try:
        # Check BOT_TOKEN
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN is required to start the bot")
            return

        # Initialize database
        if not create_tables():
            logger.error("Failed to initialize database")
            return

        init_default_faq()
        logger.info("Database initialized successfully")

        # Start FAQ website
        start_faq_site()

        # Create application
        application = Application.builder().token(BOT_TOKEN).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("faq", faq_command))
        application.add_handler(CommandHandler("admineditbot", admin_edit_bot))
        application.add_handler(CommandHandler("remove_subscription", remove_subscription_command))
        application.add_handler(CommandHandler("add_faq", add_faq_command))
        application.add_handler(CommandHandler("edit_faq", edit_faq_command))

        # Add callback query handler
        application.add_handler(CallbackQueryHandler(handle_callback_query))

        # Add handler for unknown commands (must be last)
        application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

        logger.info("Bot handlers registered successfully")

        # Start the bot with optimized polling settings for continuous operation
        logger.info("Starting SPEAKYZ bot polling...")
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            pool_timeout=20,  # Reduced for better handling
            read_timeout=20,  # Reduced for better stability
            write_timeout=20,  # Reduced for better stability
            connect_timeout=20,  # Reduced for better connection handling
            close_loop=False  # Keep event loop open
        )

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    start_bot()