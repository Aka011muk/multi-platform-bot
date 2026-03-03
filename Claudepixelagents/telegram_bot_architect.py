"""
AI Bot Architect - Telegram Bot Version
Мета-агент для создания чат-ботов ресторанов через Telegram
Работает на облачном хостинге
"""

import os
import json
import asyncio
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, Document
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import python-dotenv

# Импорты наших модулей
from generators.bot_generator import BotGenerator
from shared_logic.utils import ConfigManager

class TelegramBotArchitect:
    """Telegram-бот для создания ресторанных ботов"""
    
    def __init__(self, telegram_token: str):
        self.bot_token = telegram_token
        self.generator = BotGenerator()
        self.user_sessions: Dict[int, Dict[str, Any]] = {}
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        welcome_text = f"""🤖 *AI Bot Architect - Telegram Edition*

Привет, {user_name}! Я создаю чат-ботов для ресторанов.

🚀 *Что я умею:*
• Генерировать WhatsApp ботов для ресторанов
• Настраивать интеграцию с Google Sheets
• Добавлять AI через Groq
• Готовить код для развертывания

📋 *Как начать:*
1. Нажми "Создать бота"
2. Введи название ресторана
3. Получи готового бота

🎯 *Бизнес-модель:*
Ты вводишь название → Я создаю код → Ты разворачиваешь → Ресторан получает клиентов

Давай создадим твоего первого бота! 👇"""
        
        keyboard = [
            [InlineKeyboardButton("🚀 Создать бота", callback_data="create_bot")],
            [InlineKeyboardButton("📖 Помощь", callback_data="help")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        # Инициализация сессии пользователя
        self.user_sessions[user_id] = {
            "step": "menu",
            "data": {}
        }
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /help"""
        help_text = """📖 *Помощь - AI Bot Architect*

🤖 *Что это?*
Я - AI агент, который создает других агентов! Специализируюсь на WhatsApp ботах для ресторанов.

🎯 *Как работает:*
1. Ты говоришь название ресторана
2. Я генерирую полный код бота
3. Ты получаешь архив с готовым решением
4. Разворачиваешь и зарабатываешь

💰 *Бизнес-модель:*
• Создаешь ботов для ресторанов
• Берешь плату за настройку
• Получаешь % с продаж через бота
• Масштабируешь на множество клиентов

🛠️ *Технологии в боте:*
• FastAPI - веб-сервер
• Groq (Llama 3.3) - AI
• Green-API - WhatsApp
• Google Sheets - заявки
• Trigger.dev - напоминания

📝 *Команды:*
/start - Главное меню
/help - Эта справка
/settings - Настройки API

🚀 *Готов создать первого бота?* Нажми "Создать бота" в главном меню!"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /settings"""
        user_id = update.effective_user.id
        
        settings_text = """⚙️ *Настройки API ключей*

Для работы бота нужны API ключи:

🔑 *Обязательные:*
• Groq API Key - для AI
• Green-API Instance & Token - для WhatsApp

📊 *Опциональные:*
• Google Sheets URL - для заявок
• Trigger.dev - для напоминаний

⚠️ *Безопасность:*
Никогда не делитесь API ключами! Храните их в безопасном месте.

💡 *Где получить ключи:*
• Groq: groq.com
• Green-API: green-api.com
• Google Cloud: console.cloud.google.com
• Trigger.dev: trigger.dev

🔧 *Настроить ключи:* Пришлите в формате:
API_KEY=groq_key_here
GREEN_INSTANCE=instance_here
GREEN_TOKEN=token_here"""
        
        await update.message.reply_text(settings_text, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        action = query.data
        
        if action == "create_bot":
            await self.start_bot_creation(update, user_id)
        elif action == "help":
            await self.show_help(update, user_id)
        elif action == "settings":
            await self.show_settings(update, user_id)
        elif action == "back_to_menu":
            await self.back_to_main_menu(update, user_id)
    
    async def start_bot_creation(self, update: Update, user_id: int):
        """Начало процесса создания бота"""
        self.user_sessions[user_id]["step"] = "restaurant_name"
        
        text = """🚀 *Создание бота для ресторана*

Шаг 1/3: Название ресторана

📝 Введите название ресторана:
Примеры: "Ресторан Веранда", "Кафе Уют", "Бар Москва"

💡 *Совет:* Используйте реальное название, бот будет персонализирован под него."""
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def show_help(self, update: Update, user_id: int):
        """Показать справку"""
        help_text = """📖 *Справка AI Bot Architect*

🎯 *Моя миссия:* Создавать чат-ботов для ресторанов, которые приносят реальных клиентов!

📋 *Что делает созданный бот:*
✅ Записывает на консультации
✅ Сохраняет в Google Sheets  
✅ Напоминает о встрече
✅ Работает с AI
✅ Интегрируется с WhatsApp

💰 *Как монетизировать:*
1. Создай бота для ресторана
2. Настрой интеграции
3. Бери плату за настройку
4. Получай % с продаж

🛠️ *Готовность к деплою:*
• Docker контейнер
• Trigger.dev готовность
• Полная документация
• Техническая поддержка

🚀 *Начни прямо сейчас!*"""
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            help_text,
            parse_mode='Markdown', 
            reply_markup=reply_markup
        )
    
    async def show_settings(self, update: Update, user_id: int):
        """Показать настройки"""
        settings_text = """⚙️ *Настройки API*

🔑 *Текущие ключи:* (скрыты для безопасности)

📝 *Чтобы обновить ключи:*
Пришлите сообщение в формате:
KEY_TYPE=key_value

Поддерживаемые KEY_TYPE:
• GROQ_API_KEY
• GREEN_INSTANCE  
• GREEN_TOKEN
• GOOGLE_SHEETS_URL
• TRIGGER_API_KEY

💡 *Пример:*
GROQ_API_KEY=gsk_xxxxxxxxxx

🔒 *Безопасность:* Ключи сохраняются только в текущей сессии."""
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            settings_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def back_to_main_menu(self, update: Update, user_id: int):
        """Возврат в главное меню"""
        self.user_sessions[user_id]["step"] = "menu"
        
        welcome_text = """🤖 *AI Bot Architect - Главное меню*

Чем могу помочь? 👇"""
        
        keyboard = [
            [InlineKeyboardButton("🚀 Создать бота", callback_data="create_bot")],
            [InlineKeyboardButton("📖 Помощь", callback_data="help")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        if user_id not in self.user_sessions:
            await self.start_command(update, context)
            return
        
        session = self.user_sessions[user_id]
        step = session.get("step", "menu")
        
        if step == "restaurant_name":
            await self.process_restaurant_name(update, user_id, message_text)
        elif step == "api_keys":
            await self.process_api_keys(update, user_id, message_text)
        else:
            await update.message.reply_text(
                "🤔 Используйте кнопки меню для навигации",
                reply_markup=self.get_main_menu_keyboard()
            )
    
    async def process_restaurant_name(self, update: Update, user_id: int, restaurant_name: str):
        """Обработка названия ресторана"""
        session = self.user_sessions[user_id]
        session["step"] = "api_keys"
        session["data"]["restaurant_name"] = restaurant_name
        
        text = f"""🎯 *Отлично! Создаю бота для "{restaurant_name}"*

Шаг 2/3: API ключи

🔑 *Нужны ключи:*
• Groq API Key (обязательно)
• Green-API Instance & Token (обязательно)

📝 *Введите ключи строкой:*
GROQ_API_KEY=your_key
GREEN_INSTANCE=your_instance  
GREEN_TOKEN=your_token

💡 *Можно пропустить* - я создам бота с шаблонными ключами"""
        
        keyboard = [
            [InlineKeyboardButton("⏭️ Пропустить", callback_data="skip_keys")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def process_api_keys(self, update: Update, user_id: int, api_keys_text: str):
        """Обработка API ключей"""
        session = self.user_sessions[user_id]
        
        # Парсинг API ключей
        config = {}
        for line in api_keys_text.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip().lower()] = value.strip()
        
        session["data"]["api_keys"] = config
        
        # Генерация бота
        await self.generate_and_send_bot(update, user_id)
    
    async def skip_keys_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Пропуск ввода API ключей"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        session = self.user_sessions[user_id]
        session["data"]["api_keys"] = {}
        
        await query.answer("Пропускаю ввод ключей...")
        await self.generate_and_send_bot(update, user_id)
    
    async def generate_and_send_bot(self, update: Update, user_id: int):
        """Генерация и отправка бота"""
        session = self.user_sessions[user_id]
        restaurant_name = session["data"]["restaurant_name"]
        api_keys = session["data"]["api_keys"]
        
        # Отправка сообщения о начале генерации
        processing_msg = await update.effective_message.reply_text(
            "🔨 *Генерация бота...*",
            parse_mode='Markdown'
        )
        
        try:
            # Генерация бота
            bot_path = self.generator.generate_bot(restaurant_name, api_keys)
            
            # Создание архива
            archive_path = await self.create_bot_archive(bot_path, restaurant_name)
            
            # Обновление сообщения
            await processing_msg.edit_text(
                f"✅ *Бот для '{restaurant_name}' готов!*",
                parse_mode='Markdown'
            )
            
            # Отправка файла
            await self.send_bot_file(update, user_id, archive_path, restaurant_name)
            
            # Сброс сессии
            self.user_sessions[user_id] = {"step": "menu", "data": {}}
            
        except Exception as e:
            await processing_msg.edit_text(
                f"❌ *Ошибка при создании бота:*\n`{str(e)}`",
                parse_mode='Markdown'
            )
    
    async def create_bot_archive(self, bot_path: str, restaurant_name: str) -> str:
        """Создание архива с ботом"""
        # Создание временного архива
        temp_dir = tempfile.gettempdir()
        archive_name = f"{restaurant_name.replace(' ', '_')}_bot.zip"
        archive_path = os.path.join(temp_dir, archive_name)
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            bot_dir = Path(bot_path)
            
            for file_path in bot_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(bot_dir.parent)
                    zipf.write(file_path, arcname)
        
        return archive_path
    
    async def send_bot_file(self, update: Update, user_id: int, archive_path: str, restaurant_name: str):
        """Отправка файла с ботом"""
        success_text = f"""🎉 *Бот для "{restaurant_name}" готов!*

📦 *Что в архиве:*
• Полный код бота (Python)
• Файл конфигурации (.env)
• Зависимости (requirements.txt)
• Инструкция по развертыванию

🚀 *Следующие шаги:*
1. Распакуйте архив
2. Настройте API ключи в .env
3. Запустите бота
4. Настройте вебхук в Green-API

💰 *Как монетизировать:*
• Берите $50-100 за настройку
• Получайте 5-10% с продаж
• Масштабируйте на N клиентов

📖 *Нужна помощь?* Пишите в @support

🔥 *Удачи в бизнесе!*"""
        
        keyboard = [[InlineKeyboardButton("🚀 Создать еще бота", callback_data="create_bot")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправка файла
        with open(archive_path, 'rb') as file:
            await update.effective_message.reply_document(
                document=file,
                filename=f"{restaurant_name.replace(' ', '_')}_bot.zip",
                caption=success_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        # Удаление временного файла
        os.remove(archive_path)
    
    def get_main_menu_keyboard(self):
        """Клавиатура главного меню"""
        keyboard = [
            [InlineKeyboardButton("🚀 Создать бота", callback_data="create_bot")],
            [InlineKeyboardButton("📖 Помощь", callback_data="help")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def setup_handlers(self, application: Application):
        """Настройка обработчиков"""
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("settings", self.settings_command))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(CallbackQueryHandler(self.skip_keys_callback, pattern="skip_keys"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

def main():
    """Запуск Telegram бота"""
    # Загрузка переменных окружения
    from dotenv import load_dotenv
    load_dotenv()
    
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        print("Добавьте в .env файл: TELEGRAM_BOT_TOKEN=your_token")
        return
    
    # Создание приложения
    application = Application.builder().token(telegram_token).build()
    
    # Создание архитектора
    architect = TelegramBotArchitect(telegram_token)
    
    # Настройка обработчиков
    architect.setup_handlers(application)
    
    print("🤖 AI Bot Architect (Telegram Edition) запущен!")
    print("🚀 Готов создавать ботов для ресторанов!")
    
    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
