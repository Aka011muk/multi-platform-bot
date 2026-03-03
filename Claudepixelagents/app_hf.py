"""
Hugging Face Spaces Web App
Веб-интерфейс для мульти-платформенного бота с фоновым запуском
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
        
        logger.info("🚀 Запуск бота в фоновом режиме...")
        
        application = Application.builder().token(telegram_token).build()
        bot_instance = MultiPlatformBot(telegram_token, groq_api_key)
        
        # Настройка обработчиков
        application.add_handler(CommandHandler("start", bot_instance.start))
        application.add_handler(bot_instance.button_handler)
        application.add_handler(bot_instance.message_handler)
        
        bot_running = True
        logger.info("✅ Бот запущен в фоновом режиме!")
        
        # Запуск бота
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        bot_running = False

@app.route('/')
def home():
    """Главная страница с информацией о боте"""
    return render_template('index.html')

@app.route('/status')
def status():
    """Статус бота"""
    return jsonify({
        'bot_running': bot_running,
        'bot_instance': bot_instance is not None,
        'platforms': ['Telegram', 'Instagram', 'WhatsApp'],
        'features': ['Multi-Platform', 'AI Integration', 'Auto-Responses']
    })

@app.route('/start_bot', methods=['POST'])
def start_bot():
    """Ручной запуск бота"""
    global bot_thread, bot_running
    
    if not bot_running:
        bot_thread = threading.Thread(target=run_bot_background, daemon=True)
        bot_thread.start()
        return jsonify({'status': 'starting', 'message': 'Бот запускается...'})
    else:
        return jsonify({'status': 'already_running', 'message': 'Бот уже работает'})

@app.route('/stop_bot', methods=['POST'])
def stop_bot():
    """Остановка бота"""
    global bot_running
    
    bot_running = False
    if bot_instance:
        # Здесь можно добавить логику остановки бота
        pass
    
    return jsonify({'status': 'stopped', 'message': 'Бот остановлен'})

@app.route('/health')
def health():
    """Health check для Hugging Face"""
    return jsonify({'status': 'healthy', 'bot_running': bot_running})

if __name__ == "__main__":
    # Запуск веб-сервера
    port = int(os.environ.get('PORT', 7860))
    
    # Автоматический запуск бота при старте
    logger.info("🚀 Запуск веб-сервера и бота...")
    
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot_background, daemon=True)
    bot_thread.start()
    
    # Запускаем веб-сервер
    app.run(host='0.0.0.0', port=port, debug=False)
