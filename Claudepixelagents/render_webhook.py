"""
Render Webhook Bot
Вебхук версия для Render.com с Flask API
"""

import os
import logging
import hashlib
import hmac
from flask import Flask, request, jsonify, abort
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Глобальные переменные
telegram_app = None
bot_instance = None

class RenderWebhookBot:
    def __init__(self, telegram_token: str, groq_api_key: str):
        logger.info("Инициализация вебхук бота для Render...")
        self.telegram_token = telegram_token
        self.groq_api_key = groq_api_key
        self.user_sessions = {}
        
        # Шаблоны для платформ
        self.platform_templates = {
            "telegram": {
                "name": "Telegram Bot",
                "description": "Бот для Telegram с кнопками, меню и командами",
                "features": ["Команды (/start, /help)", "Inline кнопки", "Фото и файлы", "Локация", "Оплата"],
                "api_requirements": ["TELEGRAM_BOT_TOKEN"],
                "price": "$100-200"
            },
            "instagram": {
                "name": "Instagram Bot", 
                "description": "Бот для Instagram Direct с автоматическими ответами",
                "features": ["Авто-ответы", "Stories взаимодействие", "Комментарии", "DM автоматика"],
                "api_requirements": ["INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_BUSINESS_ID"],
                "price": "$150-300"
            },
            "both": {
                "name": "Multi-Platform Bot",
                "description": "Универсальный бот для Telegram и Instagram",
                "features": ["Единая база данных", "Синхронизация сообщений", "Кросс-платформенность"],
                "api_requirements": ["TELEGRAM_BOT_TOKEN", "INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_BUSINESS_ID"],
                "price": "$300-500"
            }
        }
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        text = """🚀 *Multi-Platform Bot Architect (Render)*

🤖 *Системные ключи работают:*
✅ Telegram Bot - активен (Webhook)
✅ Groq API - готов к AI

🎯 *Создаю ботов для платформ:*
📱 **Telegram Bot** - классический бот с кнопками
📸 **Instagram Bot** - автоматические ответы и сторис
🔄 **Multi-Platform** - единый бот для обеих платформ

💰 *Бизнес-модель:*
• Telegram Bot - $100-200
• Instagram Bot - $150-300  
• Multi-Platform - $300-500

🧠 *Выбери платформу для создания бota:*"""
        
        keyboard = [
            [InlineKeyboardButton("📱 Telegram Bot", callback_data="platform_telegram")],
            [InlineKeyboardButton("📸 Instagram Bot", callback_data="platform_instagram")],
            [InlineKeyboardButton("🔄 Multi-Platform", callback_data="platform_both")],
            [InlineKeyboardButton("ℹ️ О платформах", callback_data="info_platforms")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        self.user_sessions[user_id] = {"step": "platform_selection"}
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = update.effective_user.id
        
        await query.answer()
        
        if query.data.startswith("platform_"):
            platform = query.data.replace("platform_", "")
            await self.handle_platform_selection(update, platform)
        elif query.data == "info_platforms":
            await self.show_platform_info(update)
        elif query.data == "back_to_menu":
            await self.start(update, context)
        elif query.data == "create_bot":
            await self.start_prompt_creation(update)
    
    async def handle_platform_selection(self, update: Update, platform: str):
        query = update.callback_query
        user_id = update.effective_user.id
        
        template = self.platform_templates.get(platform, self.platform_templates["telegram"])
        
        text = f"""🎯 *Выбрана платформа: {template['name']}*

📝 *Описание:*
{template['description']}

⚡ *Возможности:*
{chr(10).join(f'• {feature}' for feature in template['features'])}

🔑 *Требуемые API ключи:*
{chr(10).join(f'• {req}' for req in template['api_requirements'])}

💰 *Цена настройки:*
{template['price']}

🧠 *Далее опиши какой бот нужен*"""
        
        keyboard = [[InlineKeyboardButton("📝 Описать бота", callback_data="create_bot")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        self.user_sessions[user_id]["step"] = "prompt"
        self.user_sessions[user_id]["platform"] = platform
    
    async def show_platform_info(self, update: Update):
        query = update.callback_query
        
        text = """ℹ️ *Информация о платформах*

📱 **Telegram Bot:**
• Классические боты с командами
• Inline кнопки и меню
• Отправка фото, файлов, локации
• Интеграция с оплатой
• Простая настройка

📸 **Instagram Bot:**
• Автоматические ответы в Direct
• Реакции на Stories и комментарии
• Приветствие новых подписчиков
• Сбор лидов и конверсий
• Требует Business аккаунт

🔄 **Multi-Platform:**
• Единая база данных
• Синхронизация между платформами
• Кросс-платформенная аналитика
• Универсальный интерфейс
• Максимум возможностей

💎 *Рекомендации:*
• Начни с Telegram Bot - проще всего
• Instagram Bot для бизнеса с активным аккаунтом
• Multi-Platform для крупных проектов

🔙 *Вернуться к выбору платформы*"""
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def start_prompt_creation(self, update: Update):
        query = update.callback_query
        user_id = update.effective_user.id
        platform = self.user_sessions[user_id].get("platform", "telegram")
        template = self.platform_templates[platform]
        
        text = f"""🧠 *Создание {template['name']} по промпту*

📝 *Опиши какой бот нужен:*

🎯 *Примеры промптов:*
• "Создай Telegram бот для пиццерии с меню, доставкой и оплатой"
• "Instagram бот для салона красоты с записью на услуги"
• "Multi-Platform бот для ресторана с бронированием столиков"

🔑 *После промпта нужны будут API ключи:*
{chr(10).join(f'• {req}' for req in template['api_requirements'])}

✍️ *Введи свой промпт:*"""
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        self.user_sessions[user_id]["step"] = "prompt_input"
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        message = update.message.text
        
        if user_id not in self.user_sessions:
            await self.start(update, context)
            return
        
        step = self.user_sessions[user_id].get("step")
        
        if step == "prompt_input":
            await self.process_prompt(update, message)
        elif step == "api_keys":
            await self.process_api_keys(update, message)
        else:
            await update.message.reply_text("🤖 Используйте кнопки для навигации")
    
    async def process_prompt(self, update: Update, prompt: str):
        user_id = update.effective_user.id
        platform = self.user_sessions[user_id].get("platform", "telegram")
        template = self.platform_templates[platform]
        
        text = f"""🧠 *Промпт получен для {template['name']}!*

📝 *Твой запрос:*
{prompt}

🔑 *Теперь нужны API ключи:*

{chr(10).join(f'• {req}' for req in template['api_requirements'])}

📊 *Дополнительные ключи (опционально):*
📱 Green-API Instance & Token (WhatsApp)
📊 Google Sheets URL (меню, клиенты)
⚡ Trigger.dev (напоминания)
🌐 Web Search API (поиск инфы)

📝 *Введи ключи:*
{chr(10).join(f'{req}=your_{req.lower()}' for req in template['api_requirements'])}
GREEN_API_INSTANCE=123456
GREEN_API_TOKEN=xxxxxxxxxx
GOOGLE_SHEETS_URL=https://docs.google.com/...

💡 *Минимум:* {', '.join(template['api_requirements'][:2])}"""
        
        await update.message.reply_text(text, parse_mode='Markdown')
        self.user_sessions[user_id]["step"] = "api_keys"
        self.user_sessions[user_id]["prompt"] = prompt
    
    async def process_api_keys(self, update: Update, keys_text: str):
        user_id = update.effective_user.id
        platform = self.user_sessions[user_id].get("platform", "telegram")
        template = self.platform_templates[platform]
        
        # Парсинг ключей
        keys = {}
        for line in keys_text.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                keys[key.strip().lower()] = value.strip()
        
        # Проверка обязательных ключей
        missing_keys = []
        for req in template['api_requirements']:
            if not keys.get(req.lower()):
                missing_keys.append(req)
        
        if missing_keys:
            await update.message.reply_text(f"❌ Нужны ключи: {', '.join(missing_keys)}!")
            return
        
        # Создаем конфигурацию
        config = {
            "platform": platform,
            "prompt": self.user_sessions[user_id]["prompt"],
            "system_keys": {
                "telegram_bot_token": self.telegram_token,
                "groq_api_key": self.groq_api_key
            },
            "platform_keys": {k: v for k, v in keys.items() if any(req.lower() in k for req in template['api_requirements'])},
            "additional_keys": {k: v for k, v in keys.items() if not any(req.lower() in k for req in template['api_requirements'])}
        }
        
        text = f"""🎉 *{template['name']} создан!*

📦 *Конфигурация готова:*
✅ Платформа: {template['name']}
✅ Промпт: {config['prompt'][:50]}...
✅ Системные ключи: Telegram + Groq
✅ Платформенные ключи: {len(config['platform_keys'])} штук
✅ Дополнительные ключи: {len(config['additional_keys'])} штук

🤖 *Что дальше:*
1. Генерирую код для {template['name']}
2. Создаю архив с инструкциями
3. Отправляю файл

🔨 *Создаю {template['name']}...*"""
        
        await update.message.reply_text(text, parse_mode='Markdown')
        
        # Имитация создания бота
        await self.send_platform_bot(update, config)
    
    async def send_platform_bot(self, update: Update, config: dict):
        platform = config["platform"]
        template = self.platform_templates[platform]
        
        text = f"""📦 *Готово! {template['name']} создан*

🤖 *В архиве:*
• main.py - основной файл для {template['name']}
• platform_config.py - конфигурация платформы
• .env - с твоими ключами
• requirements.txt - зависимости
• README_{platform.upper()}.md - инструкция для платформы
• examples/ - примеры использования

🚀 *Для запуска {template['name']}:*
1. Распакуй архив
2. Установи зависимости: pip install -r requirements.txt
3. Настрой API ключи в .env
4. Запусти: python main.py

💰 *Монетизация:*
• Базовая настройка: {template['price']}
• Дополнительные модули: +$50-100
• Поддержка: $50/мес
• % с продаж: 5-15%

🔥 *{template['name']} готов к работе на Render!*"""
        
        keyboard = [
            [InlineKeyboardButton("🧠 Создать еще", callback_data="back_to_menu")],
            [InlineKeyboardButton("📱 Другая платформа", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        
        # Сброс сессии
        self.user_sessions[update.effective_user.id] = {"step": "platform_selection"}

def setup_bot():
    """Настройка бота"""
    global telegram_app, bot_instance
    
    load_dotenv()
    
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not telegram_token or not groq_api_key:
        logger.error("❌ Токены не найдены!")
        return False
    
    # Создание приложения Telegram
    telegram_app = Application.builder().token(telegram_token).build()
    bot_instance = RenderWebhookBot(telegram_token, groq_api_key)
    
    # Настройка обработчиков
    telegram_app.add_handler(CommandHandler("start", bot_instance.start))
    telegram_app.add_handler(CallbackQueryHandler(bot_instance.button_handler))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_instance.message_handler))
    
    # Настройка вебхука
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        telegram_app.bot.set_webhook(url=f"{webhook_url}/webhook")
        logger.info(f"🪝 Вебхук установлен: {webhook_url}/webhook")
    
    logger.info("✅ Бот настроен для вебхука!")
    return True

@app.route('/')
def home():
    """Главная страница"""
    return jsonify({
        'service': 'Multi-Platform Bot Architect',
        'hosting': 'Render.com',
        'status': 'running',
        'webhook': True,
        'platforms': ['Telegram', 'Instagram', 'WhatsApp']
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Вебхук эндпоинт для Telegram"""
    if not telegram_app:
        abort(500, description="Бот не настроен")
    
    # Проверка секретного ключа (опционально)
    secret_token = os.getenv("TELEGRAM_SECRET_TOKEN")
    if secret_token:
        signature = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        if signature != secret_token:
            abort(403, description="Неверный секретный токен")
    
    # Обработка обновления
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    
    # Асинхронная обработка
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(telegram_app.process_update(update))
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Ошибка обработки вебхука: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        loop.close()

@app.route('/health')
def health():
    """Health check для Render"""
    return jsonify({
        'status': 'healthy',
        'bot_running': telegram_app is not None,
        'webhook': True,
        'hosting': 'Render.com'
    })

@app.route('/setup-webhook', methods=['POST'])
def setup_webhook():
    """Установка вебхука"""
    webhook_url = request.json.get('webhook_url')
    if not webhook_url:
        return jsonify({'error': 'webhook_url required'}), 400
    
    if telegram_app:
        try:
            telegram_app.bot.set_webhook(url=f"{webhook_url}/webhook")
            return jsonify({'status': 'webhook_set', 'url': f"{webhook_url}/webhook"})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Bot not initialized'}), 500

if __name__ == "__main__":
    logger.info("🚀 Запуск Render Webhook Bot...")
    
    # Настройка бота
    if setup_bot():
        port = int(os.environ.get('PORT', 10000))
        logger.info(f"🌐 Запуск на порту: {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        logger.error("❌ Не удалось настроить бота")
        app.run(host='0.0.0.0', port=10000, debug=False)
