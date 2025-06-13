
#!/usr/bin/env python3
"""
Main entry point for the SPEAKYZ Telegram bot application.
Runs both the Flask FAQ site and Telegram bot.
"""

import logging
import threading
import os
from flask import Flask
from bot import start_bot
from faq_site import create_faq_app
from console_admin import start_console_admin
from models import init_db, init_default_faq

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def run_flask_app():
    """Run Flask FAQ application."""
    try:
        app = create_faq_app()
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"Error starting Flask app: {e}")

def run_telegram_bot():
    """Run Telegram bot."""
    try:
        start_bot()
    except Exception as e:
        logger.error(f"Error starting Telegram bot: {e}")

def main():
    """Start the complete SPEAKYZ bot system."""
    try:
        logger.info("Initializing SPEAKYZ bot system...")
        
        # Initialize database
        logger.info("Initializing database...")
        if not init_db():
            logger.error("Failed to initialize database - continuing without DB")
        else:
            init_default_faq()
        
        # Start console admin in separate thread
        try:
            admin_thread = threading.Thread(target=start_console_admin, daemon=True)
            admin_thread.start()
            logger.info("Console admin started")
        except Exception as e:
            logger.warning(f"Console admin failed to start: {e}")
        
        # Skip Flask site for Render deployment (single service only)
        if not os.getenv('RENDER'):
            try:
                flask_thread = threading.Thread(target=run_flask_app, daemon=True)
                flask_thread.start()
                logger.info("Flask FAQ site started")
            except Exception as e:
                logger.warning(f"Flask site failed to start: {e}")
        else:
            logger.info("Skipping Flask site on Render (bot-only deployment)")
        
        # Start Telegram bot (main thread)
        logger.info("Starting Telegram bot...")
        run_telegram_bot()
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        raise

if __name__ == '__main__':
    main()
