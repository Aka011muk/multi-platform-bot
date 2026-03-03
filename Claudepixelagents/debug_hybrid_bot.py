"""
Debug Hybrid Bot - Отладочная версия с логами
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DebugHybridBot:
    def __init__(self, telegram_token: str, groq_api_key: str):
        logger.info("Инициализация бота...")
        self.telegram_token = telegram_token
        self.groq_api_key = groq_api_key
        self.user_sessions = {}
        
        logger.info(f"Telegram token: {telegram_token[:10]}...")
        logger.info(f"Groq API key: {groq_api_key[:10]}...")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        logger.info(f"Пользователь {username} (ID: {user_id}) запустил бота")
        
        text = """🚀 *Debug Hybrid Bot готов!*

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
        
        try:
            keyboard = [[InlineKeyboardButton("🧠 Создать бота", callback_data="create_bot")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            self.user_sessions[user_id] = {"step": "waiting"}
            
            logger.info(f"Стартовое сообщение отправлено пользователю {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке стартового сообщения: {e}")
            await update.message.reply_text("❌ Произошла ошибка. Попробуйте еще раз.")
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = update.effective_user.id
        
        try:
            await query.answer()
            logger.info(f"Пользователь {user_id} нажал кнопку: {query.data}")
            
            if query.data == "create_bot":
                text = """🧠 *Создание бота по промпту*

📝 *Опиши какого бота хочешь:*
Пример: "Создай бота для итальянского ресторана 'La Bella' с экспертизой по винам"

✍️ *Введи свой промпт:*"""
                
                keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
                self.user_sessions[user_id]["step"] = "prompt"
                
                logger.info(f"Переключили пользователя {user_id} в режим промпта")
                
            elif query.data == "back_to_menu":
                await self.start(update, context)
                
        except Exception as e:
            logger.error(f"Ошибка при обработке кнопки: {e}")
            await query.edit_message_text("❌ Произошла ошибка. Попробуйте еще раз.")
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        message = update.message.text
        
        logger.info(f"Получено сообщение от пользователя {user_id}: {message[:50]}...")
        
        try:
            if user_id not in self.user_sessions:
                await self.start(update, context)
                return
            
            step = self.user_sessions[user_id].get("step")
            
            if step == "prompt":
                await self.process_prompt(update, message)
            elif step == "api_keys":
                await self.process_api_keys(update, message)
            else:
                await update.message.reply_text("🤖 Используйте кнопки для навигации")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
            await update.message.reply_text("❌ Произошла ошибка. Попробуйте еще раз.")
    
    async def process_prompt(self, update: Update, prompt: str):
        user_id = update.effective_user.id
        
        logger.info(f"Обрабатываю промпт от пользователя {user_id}: {prompt[:100]}...")
        
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
        
        try:
            await update.message.reply_text(text, parse_mode='Markdown')
            self.user_sessions[user_id]["step"] = "api_keys"
            self.user_sessions[user_id]["prompt"] = prompt
            
            logger.info(f"Запросил API ключи у пользователя {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка при запросе API ключей: {e}")
            await update.message.reply_text("❌ Произошла ошибка. Попробуйте еще раз.")
    
    async def process_api_keys(self, update: Update, keys_text: str):
        user_id = update.effective_user.id
        
        logger.info(f"Получил API ключи от пользователя {user_id}")
        
        try:
            # Парсинг ключей
            keys = {}
            for line in keys_text.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    keys[key.strip().lower()] = value.strip()
            
            logger.info(f"Распарсил ключи: {list(keys.keys())}")
            
            # Проверка обязательных ключей
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
            
            # Имитация создания бота
            await self.send_mock_bot(update, config)
            
            logger.info(f"Бот для пользователя {user_id} успешно создан")
            
        except Exception as e:
            logger.error(f"Ошибка при обработке API ключей: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке ключей. Попробуйте еще раз.")
    
    async def send_mock_bot(self, update: Update, config: dict):
        """Отправка мок бота"""
        try:
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
            
            logger.info("Мок бот отправлен пользователю")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке мок бота: {e}")
            await update.message.reply_text("❌ Произошла ошибка при отправке бота.")

def main():
    try:
        logger.info("Загрузка переменных окружения...")
        load_dotenv()
        
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not telegram_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN не найден в .env")
            print("❌ TELEGRAM_BOT_TOKEN не найден в .env")
            return
        
        if not groq_api_key:
            logger.error("❌ GROQ_API_KEY не найден в .env")
            print("❌ GROQ_API_KEY не найден в .env")
            return
        
        logger.info("🚀 Запуск Debug Hybrid Bot...")
        
        application = Application.builder().token(telegram_token).build()
        bot = DebugHybridBot(telegram_token, groq_api_key)
        
        # Настройка обработчиков
        application.add_handler(CommandHandler("start", bot.start))
        application.add_handler(CallbackQueryHandler(bot.button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.message_handler))
        
        logger.info("✅ Бот готов! Найди его в Telegram и отправь /start")
        print("✅ Debug Hybrid Bot готов!")
        print("🔍 Найди бота в Telegram и отправь /start")
        print("📊 Логи будут выводиться в консоль")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске: {e}")
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
