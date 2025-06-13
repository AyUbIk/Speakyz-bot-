"""
FAQ website for SPEAKYZ bot system.
Provides web interface for FAQ entries.
"""

from flask import Flask, render_template_string, jsonify
from models import FAQ, get_db
import threading
import logging

logger = logging.getLogger(__name__)

FAQ_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SPEAKYZ - FAQ</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .faq-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }

        .faq-item {
            border-bottom: 1px solid #eee;
        }

        .faq-item:last-child {
            border-bottom: none;
        }

        .faq-question {
            background: #f8f9fa;
            padding: 20px;
            cursor: pointer;
            font-weight: 600;
            font-size: 1.1em;
            color: #2c3e50;
            transition: background-color 0.3s ease;
        }

        .faq-question:hover {
            background: #e9ecef;
        }

        .faq-question::before {
            content: "▶";
            margin-right: 10px;
            transition: transform 0.3s ease;
        }

        .faq-item.active .faq-question::before {
            transform: rotate(90deg);
        }

        .faq-answer {
            padding: 0 20px;
            max-height: 0;
            overflow: hidden;
            transition: all 0.3s ease;
            background: white;
        }

        .faq-item.active .faq-answer {
            padding: 20px;
            max-height: 500px;
        }

        .faq-answer p {
            color: #555;
            line-height: 1.7;
        }

        .bot-link {
            text-align: center;
            margin-top: 30px;
        }

        .bot-button {
            display: inline-block;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }

        .bot-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 7px 20px rgba(0,0,0,0.3);
        }

        .footer {
            text-align: center;
            margin-top: 40px;
            color: white;
            opacity: 0.8;
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }

            .header h1 {
                font-size: 2em;
            }

            .faq-question {
                padding: 15px;
                font-size: 1em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 SPEAKYZ</h1>
            <p>Часто задаваемые вопросы</p>
        </div>

        <div class="faq-container">
            {% for faq in faqs %}
            <div class="faq-item">
                <div class="faq-question" onclick="toggleFaq(this)">
                    {{ faq.question }}
                </div>
                <div class="faq-answer">
                    <p>{{ faq.answer | replace('\\n', '<br>') | safe }}</p>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="bot-link">
            <a href="https://t.me/speakyz_bot" class="bot-button">
                🤖 Открыть бота SPEAKYZ
            </a>
        </div>

        <div class="footer">
            <p>© 2024 SPEAKYZ - Онлайн школа английского языка</p>
        </div>
    </div>

    <script>
        function toggleFaq(element) {
            const faqItem = element.parentElement;
            const isActive = faqItem.classList.contains('active');

            // Закрыть все открытые FAQ
            document.querySelectorAll('.faq-item.active').forEach(item => {
                item.classList.remove('active');
            });

            // Открыть текущий, если он не был активен
            if (!isActive) {
                faqItem.classList.add('active');
            }
        }
    </script>
</body>
</html>
"""

def create_faq_app():
    """Create Flask app for FAQ website."""
    app = Flask(__name__)

    @app.route('/')
    def faq_page():
        """Main FAQ page."""
        db = get_db()
        if not db:
            faqs = []
        else:
            try:
                faqs = db.query(FAQ).filter(FAQ.is_active == True).all()
                db.close()
            except Exception as e:
                logger.error(f"Error fetching FAQ: {e}")
                faqs = []
                if db:
                    db.close()

        return render_template_string(FAQ_TEMPLATE, faqs=faqs)

    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return {'status': 'ok', 'service': 'speakyz-faq'}, 200

    @app.route('/api/faq')
    def api_faq():
        """API endpoint for FAQ data."""
        db = get_db()
        if not db:
            return {'error': 'Database not available'}, 500

        try:
            faqs = db.query(FAQ).filter(FAQ.is_active == True).all()
            faq_list = []
            for faq in faqs:
                faq_list.append({
                    'id': faq.id,
                    'question': faq.question,
                    'answer': faq.answer
                })
            db.close()
            return {'faqs': faq_list}
        except Exception as e:
            logger.error(f"Error in FAQ API: {e}")
            if db:
                db.close()
            return {'error': 'Internal server error'}, 500

    return app

def start_faq_site():
    """Start FAQ site in a separate thread."""
    import os
    # Skip FAQ site on Render (single service deployment)
    if os.getenv('RENDER'):
        logger.info("Skipping FAQ site on Render deployment")
        return
        
    try:
        def run_site():
            app = create_faq_app()
            app.run(host='0.0.0.0', port=8080, debug=False)

        site_thread = threading.Thread(target=run_site, daemon=True)
        site_thread.start()
        logger.info("FAQ site started on port 8080")
    except Exception as e:
        logger.error(f"Failed to start FAQ site: {e}")