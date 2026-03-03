"""
Simple Hybrid Bot - Быстрый тест
Groq и Telegram в коде, остальные ключи в Telegram
"""

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from dotenv import load_dotenv

class SimpleHybridBot:
    def __init__(self, telegram_token: str, groq_api_key: str):
        self.telegram_token = telegram_token
        self.groq_api_key = groq_api_key
        self.user_sessions = {}
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        text = """🚀 *Simple Hybrid Bot готов!*

🤖 *Системные ключи работают:*
✅ Telegram Bot - активен
✅ Groq API - готов к AI

👤 *Тебе нужно добавить:*
📱 Green-API (WhatsApp)
📊 Google Sheets (меню)
⚡ Trigger.dev (напоминания)
🌐 Web Search API (поиск)

🎯 *Протестируем:*
1. Создай бота по промпту
2. Введи свои API ключи
3. Получи готового бота

🧠 *Начнем создание бота!*"""
        
        keyboard = [[InlineKeyboardButton("🧠 Создать бота", callback_data="create_bot")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        
        self.user_sessions[user_id] = {"step": "waiting"}
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == "create_bot":
            text = """🧠 *Создание бота по промпту*

📝 *Опиши какого бота хочешь:*
Пример: "Создай бота для итальянского ресторана 'La Bella' с экспертизой по винам"

✍️ *Введи свой промпт:*"""
            
            await query.edit_message_text(text, parse_mode='Markdown')
            self.user_sessions[update.effective_user.id]["step"] = "prompt"
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        message = update.message.text
        
        if user_id not in self.user_sessions:
            await self.start(update, context)
            return
        
        step = self.user_sessions[user_id].get("step")
        
        if step == "prompt":
            await self.process_prompt(update, message)
        elif step == "api_keys":
            await self.process_api_keys(update, message)
    
    async def process_prompt(self, update: Update, prompt: str):
        user_id = update.effective_user.id
        
        text = f"""🧠 *Промпт получен!*

📝 *Твой запрос:*
{prompt}

🔑 *Теперь нужны твои API ключи:*

📱 **Green-API Instance** (обязательно)
📱 **Green-API Token** (обязательно)
📊 **Google Sheets URL** (опционально)
⚡ **Trigger.dev** (опционально)
🌐 **Web Search API** (опционально)

📝 *Введи ключи:*
GREEN_API_INSTANCE=123456
GREEN_API_TOKEN=xxxxxxxxxx
GOOGLE_SHEETS_URL=https://docs.google.com/...

💡 *Минимум:* Green-API Instance + Token"""
        
        await update.message.reply_text(text, parse_mode='Markdown')
        self.user_sessions[user_id]["step"] = "api_keys"
        self.user_sessions[user_id]["prompt"] = prompt
    
    async def process_api_keys(self, update: Update, keys_text: str):
        user_id = update.effective_user.id
        
        # Парсинг ключей
        keys = {}
        for line in keys_text.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                keys[key.strip().lower()] = value.strip()
        
        # Проверка обязательных
        if not keys.get("green_api_instance") or not keys.get("green_api_token"):
            await update.message.reply_text("❌ Нужны Green-API Instance и Token!")
            return
        
        # Создаем конфигурацию
        config = {
            "prompt": self.user_sessions[user_id]["prompt"],
            "system_keys": {
                "telegram_bot_token": self.telegram_token,
                "groq_api_key": self.groq_api_key
            },
            "user_keys": keys
        }
        
        text = f"""🎉 *Бот создан!*

📦 *Конфигурация готова:*
✅ Промпт: {config['prompt'][:50]}...
✅ Системные ключи: Telegram + Groq
✅ Пользовательские ключи: {len(keys)} штук

🤖 *Что дальше:*
1. Генерирую код бота
2. Создаю архив
3. Отправляю файл

🔨 *Создаю бота...*"""
        
        await update.message.reply_text(text, parse_mode='Markdown')
        
        # Здесь будет генерация бота
        await self.send_mock_bot(update, config)
    
    async def send_mock_bot(self, update: Update, config: str):
        text = """📦 *Готово! Mock бот создан*

🤖 *В архиве:*
• main.py - основной файл
• .env - с твоими ключами
• requirements.txt - зависимости
• README.md - инструкция

🚀 *Для запуска:*
1. Распакуй архив
2. Установи зависимости: pip install -r requirements.txt
3. Запусти: python main.py

💰 *Бизнес-модель:*
• $100-300 за настройку
• 5-15% с продаж
• $50/мес поддержка

🔥 *Бот готов к работе!*"""
        
        keyboard = [[InlineKeyboardButton("🧠 Создать еще", callback_data="create_bot")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        
        # Сброс сессии
        self.user_sessions[update.effective_user.id] = {"step": "waiting"}

def main():
    load_dotenv()
    
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not telegram_token or not groq_api_key:
        print("❌ Нужны TELEGRAM_BOT_TOKEN и GROQ_API_KEY в .env")
        return
    
    print("🚀 Simple Hybrid Bot запускается...")
    print(f"🤖 Telegram: {telegram_token[:10]}...")
    print(f"🧠 Groq: {groq_api_key[:10]}...")
    
    application = Application.builder().token(telegram_token).build()
    bot = SimpleHybridBot(telegram_token, groq_api_key)
    
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CallbackQueryHandler(bot.button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.message_handler))
    
    print("✅ Бот готов! Найди его в Telegram и отправь /start")
    application.run_polling()

if __name__ == "__main__":
    main()
