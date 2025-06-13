
#!/usr/bin/env python3
"""
Database initialization script for SPEAKYZ bot.
Run this once to set up the database schema.
"""

import logging
from models import init_db, init_default_faq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize database with tables and default data."""
    try:
        logger.info("Starting database initialization...")
        
        # Create tables
        init_db()
        logger.info("Database tables created successfully")
        
        # Add default FAQ
        init_default_faq()
        logger.info("Default FAQ data added successfully")
        
        logger.info("Database initialization completed!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == '__main__':
    main()
