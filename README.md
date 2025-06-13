
# SPEAKYZ Telegram Bot

Telegram бот для онлайн-школы английского языка SPEAKYZ с функциями управления подписками, FAQ и административной панелью.

## Функции

- 🎓 Управление тарифными планами и подписками
- ❓ FAQ система с веб-интерфейсом
- 👤 Профили пользователей
- 🔧 Административная панель
- 💳 Система оплаты
- 📊 Статистика пользователей

## Установка

### Требования

- Python 3.11+
- PostgreSQL база данных
- Telegram Bot Token

### Локальная установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd speakyz-bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

4. Заполните переменные окружения в `.env`:
```env
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://user:password@host:port/database
WEBSITE_URL=https://your-website.com
```

5. Запустите бота:
```bash
python main.py
```

## Деплой

### Render

1. Форкните этот репозиторий
2. Создайте новый Web Service на [Render](https://render.com)
3. Подключите ваш форкнутый репозиторий
4. Render автоматически обнаружит `render.yaml` файл
5. Установите следующие Environment Variables:
   - `BOT_TOKEN` - ваш токен Telegram бота
   - `DATABASE_URL` - URL PostgreSQL базы данных
   - `PGDATABASE`, `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD` - параметры БД
   - `SESSION_SECRET` - секретный ключ для сессий
6. Нажмите "Create Web Service"
7. После деплоя ваш бот будет доступен по адресу `https://your-app-name.onrender.com`

### Настройка базы данных

Если у вас нет PostgreSQL базы данных, создайте её на [Neon](https://neon.tech) или [Railway](https://railway.app):

1. Создайте новую PostgreSQL базу данных
2. Скопируйте Connection String
3. Добавьте его как `DATABASE_URL` в Environment Variables

### Локальная разработка в Replit

1. Форкните этот Repl
2. Добавьте переменные окружения в Secrets:
   - `BOT_TOKEN`
   - `DATABASE_URL`
   - И другие необходимые переменные из `.env.example`
3. Нажмите Runорий
2. Подключите репозиторий к Render
3. Настройте переменные окружения в панели Render
4. Деплой произойдет автоматически

### Переменные окружения

| Переменная | Описание | Обязательная |
|------------|----------|--------------|
| `BOT_TOKEN` | Токен Telegram бота | Да |
| `DATABASE_URL` | URL подключения к PostgreSQL | Да |
| `WEBSITE_URL` | URL основного сайта | Нет |
| `SESSION_SECRET` | Секрет для сессий | Нет |

## Структура проекта

```
├── bot.py              # Основная логика бота
├── config.py           # Конфигурация
├── models.py           # Модели базы данных
├── admin.py            # Административные функции
├── faq_site.py         # FAQ веб-сайт
├── console_admin.py    # Консольная админ-панель
├── main.py            # Точка входа
└── attached_assets/   # Медиа файлы
```

## Команды бота

### Пользовательские команды
- `/start` - Главное меню
- `/help` - Справка по командам
- `/faq` - Часто задаваемые вопросы

### Административные команды
- `/admineditbot` - Панель администратора
- `/remove_subscription @username` - Удалить подписку пользователя
- `/add_faq Вопрос | Ответ` - Добавить FAQ
- `/edit_faq ID Вопрос | Ответ` - Редактировать FAQ

## Тарифные планы

- **Start** - Бесплатный (2 групповых занятия/неделю)
- **Smart** - 870,000 UZS/месяц (2 групповых + 1 разговорный клуб)
- **Pro+** - 1,650,000 UZS/месяц (2 индивидуальных + 2 групповых)
- **Разговорный клуб** - 190,000 UZS/месяц (1 встреча/неделю)

## Поддержка

Для получения поддержки обращайтесь к @Dream565758

## Лицензия

MIT License
