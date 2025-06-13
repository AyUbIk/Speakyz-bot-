"""
Database models for SPEAKYZ bot system.
"""

from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, Boolean, Text, Float
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    subscription_type = Column(String(50), default=None)  # start, smart, pro_plus, speaking_club
    subscription_end = Column(DateTime, default=None)
    speaking_clubs_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FAQ(Base):
    __tablename__ = 'faq'

    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer)  # telegram_id of admin who created

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    telegram_id = Column(BigInteger, nullable=False)
    amount = Column(Float, nullable=False)
    subscription_type = Column(String(50), nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    is_verified = Column(Boolean, default=False)

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("⚠️  DATABASE_URL не найден в переменных окружения!")
    print("Для работы бота требуется PostgreSQL база данных")
    DATABASE_URL = None
if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_timeout=20,
        max_overflow=0,
        echo=False
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None

def create_tables():
    """Create all database tables."""
    if not engine:
        logger.error("Cannot create tables: database not configured")
        return False
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

def get_db():
    """Get database session."""
    if not SessionLocal:
        logger.error("Database not configured")
        return None
    try:
        db = SessionLocal()
        return db
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def init_db():
    """Initialize database."""
    if not DATABASE_URL:
        logger.error("Cannot initialize database: DATABASE_URL not set")
        return False

    return create_tables()

def init_default_faq():
    """Initialize default FAQ entries."""
    db = get_db()
    if not db:
        logger.error("Cannot initialize FAQ: database not available")
        return False

    try:
        # Check if FAQ already exists
        existing_faq = db.query(FAQ).first()
        if existing_faq:
            db.close()
            return True

        default_faqs = [
            {
                "question": "Как проходят занятия?",
                "answer": "Занятия проходят онлайн через Zoom в удобное для вас время. Групповых занятия - до 8 человек, индивидуальные - один на один с преподавателем."
            },
            {
                "question": "Какие тарифы доступны?",
                "answer": "У нас 4 тарифа:\\n• Start - 2 групповых занятия/неделю\\n• Smart - 2 групповых + 1 разговорный клуб (870,000 UZS/мес)\\n• Pro+ - 2 индивидуальных + 2 групповых (1,650,000 UZS/мес)\\n• Разговорный клуб - 1 встреча/неделю (190,000 UZS/мес)"
            },
            {
                "question": "Как оплатить обучение?",
                "answer": "Оплата производится переводом на карту. После оплаты ваша подписка активируется автоматически."
            },
            {
                "question": "Можно ли вернуть деньги?",
                "answer": "Если вы хотите оформить возврат средств то пишите нашему сотруднику @Dream565758"
            }
        ]

        for faq_data in default_faqs:
            faq = FAQ(**faq_data)
            db.add(faq)

        db.commit()
        db.close()
        return True
    except Exception as e:
        logger.error(f"Error initializing FAQ: {e}")
        if db:
            db.close()
        return False