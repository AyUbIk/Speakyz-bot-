
"""
Configuration settings for the Telegram bot.
"""

import os
import sys

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("⚠️  BOT_TOKEN не найден в переменных окружения!")
    print("Для локальной разработки: добавьте в Secrets")
    print("Для Replit: установите в Environment Variables")
    if os.getenv("RENDER"):
        raise ValueError("BOT_TOKEN is required for production deployment")
    BOT_TOKEN = None  # Для разработки

WEBSITE_URL = os.getenv("WEBSITE_URL", "https://sites.google.com/view/wwwspeakzycom/%D0%BC%D0%B5%D1%81%D1%82%D0%BE-%D0%BF%D1%80%D0%BE%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F")

# FAQ site URL - dynamically determined
def get_faq_url():
    """Get FAQ site URL based on environment."""
    # For Render deployment
    if os.getenv('RENDER'):
        render_url = os.getenv('RENDER_EXTERNAL_URL')
        if render_url:
            return render_url
    
    # For Replit development
    replit_url = os.getenv('REPLIT_DEV_DOMAIN')
    if replit_url:
        return f"https://{replit_url}"
    
    # Local development fallback
    return "http://localhost:8080"

FAQ_URL = get_faq_url()

# Welcome message configuration
WELCOME_MESSAGE = """
🎉 Добро пожаловать в SPEAKYZ - Онлайн-школу английского языка! 🎉

📚 **О нас:**
• Современные методики обучения английскому языку
• Опытные преподаватели с международными сертификатами
• Индивидуальный подход к каждому студенту
• Гибкое расписание, подходящее вашему ритму жизни

🌟 **SPEAKYZ — YOUR ENGLISH, YOUR WAY**
• Разговорная практика с носителями языка
• Подготовка к международным экзаменам
• Бизнес-английский для карьерного роста
• Интерактивные уроки и современные материалы

🚀 **Начните свой путь к свободному владению английским уже сегодня!**

Нажмите кнопку ниже, чтобы узнать больше о наших курсах и записаться на бесплатный пробный урок! 👇
"""

BUTTON_TEXT = "🌐 Перейти на сайт SPEAKYZ"
