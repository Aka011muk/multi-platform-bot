"""
Koyeb Deployment Script
Запуск мульти-платформенного бота на Koyeb
"""

import os
import asyncio
import threading
from flask import Flask, render_template, request, jsonify
from multi_platform_bot import MultiPlatformBot
from telegram.ext import Application
from dotenv import load_dotenv
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Глобальные переменные
bot_instance = None
bot_thread = None
bot_running = False

app = Flask(__name__)

def run_bot_background():
    """Запуск бота в фоновом потоке"""
    global bot_instance, bot_running
    
    try:
        load_dotenv()
        
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not telegram_token or not groq_api_key:
            logger.error("❌ Токены не найдены!")
            return
        
        logger.info("🚀 Запуск бота на Koyeb...")
        
        application = Application.builder().token(telegram_token).build()
        bot_instance = MultiPlatformBot(telegram_token, groq_api_key)
        
        # Настройка обработчиков
        application.add_handler(CommandHandler("start", bot_instance.start))
        application.add_handler(bot_instance.button_handler)
        application.add_handler(bot_instance.message_handler)
        
        bot_running = True
        logger.info("✅ Бот запущен на Koyeb!")
        
        # Запуск бота
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        bot_running = False

@app.route('/')
def home():
    """Главная страница"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check для Koyeb"""
    return jsonify({
        'status': 'healthy',
        'bot_running': bot_running,
        'service': 'Multi-Platform Bot Architect'
    })

@app.route('/status')
def status():
    """Статус бота"""
    return jsonify({
        'bot_running': bot_running,
        'bot_instance': bot_instance is not None,
        'platforms': ['Telegram', 'Instagram', 'WhatsApp'],
        'features': ['Multi-Platform', 'AI Integration', 'Auto-Responses'],
        'hosting': 'Koyeb'
    })

if __name__ == "__main__":
    # Настройка для Koyeb
    port = int(os.environ.get('PORT', 8080))
    
    logger.info("🚀 Запуск на Koyeb...")
    logger.info(f"🌐 Порт: {port}")
    
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot_background, daemon=True)
    bot_thread.start()
    
    # Даем время боту запуститься
    import time
    time.sleep(3)
    
    # Запускаем веб-сервер для Koyeb
    app.run(host='0.0.0.0', port=port, debug=False)
