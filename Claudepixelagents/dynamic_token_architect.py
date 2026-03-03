"""
Dynamic Token Architect - Telegram Bot с вводом токенов в чате
Пользователь вводит все API ключи прямо в Telegram при создании бота
"""

import os
import json
import asyncio
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, Document
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import python_dotenv

# Импорты наших модулей
from generators.bot_generator import BotGenerator
from shared_logic.utils import ConfigManager

@dataclass
class BotConfiguration:
    """Конфигурация создаваемого бота"""
    restaurant_name: str
    ai_prompt: str = ""
    api_keys: Dict[str, str] = None
    menu_data: str = ""
    price_list: str = ""
    custom_responses: Dict[str, str] = None
    web_search_enabled: bool = True
    sales_strategy: str = "consultative"
    personality: str = "professional_friendly"
    
    def __post_init__(self):
        if self.api_keys is None:
            self.api_keys = {}
        if self.custom_responses is None:
            self.custom_responses = {}

class DynamicTokenArchitect:
    """Архитектор с динамическим вводом токенов"""
    
    def __init__(self, telegram_token: str):
        self.bot_token = telegram_token
        self.generator = BotGenerator()
        self.user_sessions: Dict[int, Dict[str, Any]] = {}
        self.ai_templates = self.load_ai_templates()
        
    def load_ai_templates(self) -> Dict[str, str]:
        """Загрузка AI-шаблонов"""
        return {
            "professional_friendly": """Ты - профессиональный ассистент ресторана {restaurant_name}. 
Твой стиль: дружелюбный, но экспертный. Ты знаешь всё о ресторане, можешь консультировать по меню, 
винам, мероприятиям. Всегда предлагаешь дополнительные услуги и записываешь на консультацию.""",
            
            "luxury": """Ты - премиум-консьерж ресторана {restaurant_name}.
Твой стиль: элегантный, изысканный. Ты говоришь как представитель высокого класса, 
предлагаешь эксклюзивные услуги, персональный подход. Всегда подчеркиваешь уникальность.""",
            
            "casual_friendly": """Ты - дружелюбный помощник ресторана {restaurant_name}.
Твой стиль: неформальный, веселый. Ты как друг, который отлично знает ресторан и 
хочет помочь гостям получить лучший опыт. Используешь эмодзи, шутки.""",
            
            "expert_consultant": """Ты - эксперт-консультант по ресторанному бизнесу.
Ты не просто помогаешь с выбором, а даешь профессиональные рекомендации, 
объясняешь нюансы кухни, рассказываешь о концепции ресторана."""
        }
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        welcome_text = f"""🚀 *Dynamic Token Architect*

Привет, {user_name}! Создаю **умных** ботов с **персональными** токенами.

🎯 *Уникальность:*
• 📝 Вводи API ключи прямо в Telegram
• 🔧 Каждый бот со своими настройками
• 🧠 AI-персонализация под ресторан
• 🌐 Веб-интеллект и поиск
• 💰 Sales-стратегии

💼 *Бизнес-модель:*
Создаешь ботов → Рестораны платят → Ты зарабатываешь

📋 *Как начать:*
1. 🎯 Создать по промпту
2. ⚙️ Пошаговая настройка  
3. 📋 Загрузить данные

🔥 *Каждый бот - уникальный!*"""
        
        keyboard = [
            [InlineKeyboardButton("🎯 Создать по промпту", callback_data="create_prompt")],
            [InlineKeyboardButton("⚙️ Пошаговая настройка", callback_data="create_stepwise")],
            [InlineKeyboardButton("📋 Загрузить данные", callback_data="upload_data")],
            [InlineKeyboardButton("🔑 Мои токены", callback_data="my_tokens")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        self.user_sessions[user_id] = {
            "step": "menu",
            "data": {},
            "config": BotConfiguration(restaurant_name="")
        }
    
    async def create_prompt_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание бота по промпту с токенами"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        self.user_sessions[user_id]["step"] = "prompt_creation"
        
        prompt_text = """🧠 *Создание умного бота по промпту*

Опиши, каким должен быть твой бот. Чем подробнее, тем умнее получится!

📝 *Пример промпта:*
"Создай бота для итальянского ресторана 'La Bella'. Бот должен быть элегантным, знать всё о пасте и вине, уметь рекомендовать блюда по предпочтениям гостя, записывать на дегустации, говорить по-итальянски базовые фразы. Стиль - дружелюбный профессионал. Бот должен уметь искать информацию о ресторане в интернете и обновлять меню."

✍️ *Введи свой промпт:*

💡 *После промпта я попрошу API ключи для этого бота:*
• 🤖 Groq API Key (обязательно)
• 📱 Green-API Instance & Token (для WhatsApp)
• 📊 Google Sheets URL (для меню)
• ⚡ Trigger.dev (для напоминаний)
• 🌐 Web Search API (для поиска инфы)"""
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            prompt_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def process_prompt_creation(self, update: Update, user_id: int, prompt: str):
        """Обработка создания по промпту"""
        session = self.user_sessions[user_id]
        session["step"] = "prompt_api_keys"
        session["data"]["prompt"] = prompt
        
        # AI-анализ промпта
        analysis = await self.analyze_prompt(prompt)
        
        text = f"""🧠 *AI-анализ промпта выполнен!*

📊 *Что я понял:*
{analysis}

🔑 *Теперь нужны API ключи для ЭТОГО бота:*

🤖 **Groq API Key** (обязательно для AI)
📱 **Green-API Instance** (для WhatsApp)
📱 **Green-API Token** (для WhatsApp)
📊 **Google Sheets URL** (для меню, опционально)
⚡ **Trigger.dev API Key** (напоминания, опционально)
⚡ **Trigger.dev Project ID** (напоминания, опционально)
🌐 **Web Search API Key** (поиск инфы, опционально)

📝 *Введи ключи строкой:*
GROQ_API_KEY=gsk_xxxxxxxxxx
GREEN_API_INSTANCE=123456
GREEN_API_TOKEN=xxxxxxxxxx
GOOGLE_SHEETS_URL=https://docs.google.com/...
TRIGGER_API_KEY=trigger_xxx
TRIGGER_PROJECT_ID=proj_xxx
WEB_SEARCH_API_KEY=search_xxx

💡 *Минимум для работы:* Groq + Green-API

🔒 *Безопасность:* Ключи сохраняются только для этого бота"""
        
        keyboard = [
            [InlineKeyboardButton("⏭️ Создать с базовыми", callback_data="create_minimal")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def analyze_prompt(self, prompt: str) -> str:
        """AI-анализ промпта"""
        analysis_points = []
        
        if "итальянск" in prompt.lower():
            analysis_points.append("🍝 Итальянская кухня")
        if "вино" in prompt.lower():
            analysis_points.append("🍷 Экспертиза по винам")
        if "элегантн" in prompt.lower():
            analysis_points.append("💎 Элегантный стиль")
        if "дружелюбн" in prompt.lower():
            analysis_points.append("😊 Дружелюбный подход")
        if "поиск" in prompt.lower() or "интернет" in prompt.lower():
            analysis_points.append("🌐 Веб-поиск включен")
        if "мультиязыч" in prompt.lower():
            analysis_points.append("🌍 Мультиязычность")
        if "премиум" in prompt.lower():
            analysis_points.append("💎 Премиум сегмент")
        
        return "\n".join(analysis_points) if analysis_points else "🤖 Создаю универсального умного бота"
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка сообщений"""
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        if user_id not in self.user_sessions:
            await self.start_command(update, context)
            return
        
        session = self.user_sessions[user_id]
        step = session.get("step", "menu")
        
        if step == "prompt_creation":
            await self.process_prompt_creation(update, user_id, message_text)
        elif step == "prompt_api_keys":
            await self.process_api_keys(update, user_id, message_text)
        elif step == "stepwise_name":
            await self.process_stepwise_name(update, user_id, message_text)
        elif step == "stepwise_tokens":
            await self.process_stepwise_tokens(update, user_id, message_text)
        elif step == "upload_data":
            await self.process_data_upload(update, user_id, message_text)
        else:
            await update.message.reply_text(
                "🤖 Используйте кнопки меню для навигации",
                reply_markup=self.get_main_menu_keyboard()
            )
    
    async def process_api_keys(self, update: Update, user_id: int, api_keys_text: str):
        """Обработка API ключей с валидацией"""
        session = self.user_sessions[user_id]
        
        # Парсинг API ключей
        config = {}
        for line in api_keys_text.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip().lower()] = value.strip()
        
        # Валидация обязательных ключей
        missing_keys = []
        if not config.get("groq_api_key"):
            missing_keys.append("Groq API Key")
        if not config.get("green_api_instance"):
            missing_keys.append("Green-API Instance")
        if not config.get("green_api_token"):
            missing_keys.append("Green-API Token")
        
        if missing_keys:
            error_text = f"""❌ *Отсутствуют обязательные ключи:*

🔑 *Нужно добавить:*
{chr(10).join(f'• {key}' for key in missing_keys)}

📝 *Пример правильного формата:*
GROQ_API_KEY=gsk_xxxxxxxxxx
GREEN_API_INSTANCE=123456
GREEN_API_TOKEN=xxxxxxxxxx
GOOGLE_SHEETS_URL=https://docs.google.com/...
TRIGGER_API_KEY=trigger_xxx
TRIGGER_PROJECT_ID=proj_xxx
WEB_SEARCH_API_KEY=search_xxx

💡 *Минимум для работы:* Groq + Green-API

🔄 *Попробуйте снова:*"""
            
            keyboard = [[InlineKeyboardButton("⏭️ Создать с базовыми", callback_data="create_minimal")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                error_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return
        
        # Сохранение конфигурации
        session["data"]["api_keys"] = config
        
        # Показываем что получили
        received_keys = []
        for key in config.keys():
            if key in ["groq_api_key", "green_api_instance", "green_api_token", "google_sheets_url", "trigger_api_key", "trigger_project_id", "web_search_api_key"]:
                received_keys.append(f"✅ {key.replace('_', ' ').title()}")
        
        success_text = f"""🔑 *API ключи получены!*

{chr(10).join(received_keys)}

🧠 *Генерирую умного бота...*
Это может занять 1-2 минуты.

⚙️ *Что происходит:*
• Создаю AI-персональность
• Настраиваю веб-интеллект
• Интегрирую API
• Генерирую код бота

🔨 *Создаю бота...*"""
        
        await update.message.reply_text(success_text, parse_mode='Markdown')
        
        # Генерация бота
        await self.generate_and_send_bot(update, user_id)
    
    async def process_stepwise_name(self, update: Update, user_id: int, restaurant_name: str):
        """Обработка названия в пошаговом режиме"""
        session = self.user_sessions[user_id]
        session["step"] = "stepwise_tokens"
        session["config"].restaurant_name = restaurant_name
        
        text = f"""⚙️ *Настройка бота для "{restaurant_name}"*

Шаг 2/4: API ключи для бота

🔑 *Введите API ключи для ЭТОГО ресторана:*

🤖 **Groq API Key** (обязательно для AI)
📱 **Green-API Instance** (для WhatsApp)
📱 **Green-API Token** (для WhatsApp)
📊 **Google Sheets URL** (для меню)
⚡ **Trigger.dev** (для напоминаний)
🌐 **Web Search API** (для поиска)

📝 *Формат:*
GROQ_API_KEY=gsk_xxxxxxxxxx
GREEN_API_INSTANCE=123456
GREEN_API_TOKEN=xxxxxxxxxx
... другие ключи

💡 *Каждый ресторан - уникальные ключи!*"""
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def process_stepwise_tokens(self, update: Update, user_id: int, tokens_text: str):
        """Обработка токенов в пошаговом режиме"""
        # Та же логика что и process_api_keys
        await self.process_api_keys(update, user_id, tokens_text)
    
    async def create_minimal_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание бота с минимальными ключами"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        session = self.user_sessions[user_id]
        
        # Создаем базовую конфигурацию
        session["data"]["api_keys"] = {
            "groq_api_key": "your_groq_key_here",
            "green_api_instance": "your_instance_here",
            "green_api_token": "your_token_here"
        }
        
        await query.edit_message_text("🔨 Создаю базового бота...")
        
        # Генерация бота
        await self.generate_and_send_bot(update, user_id)
    
    async def generate_and_send_bot(self, update: Update, user_id: int):
        """Генерация и отправка бота"""
        session = self.user_sessions[user_id]
        
        # Отправка сообщения о начале генерации
        processing_msg = await update.effective_message.reply_text(
            "🧠 *Генерация интеллектуального бота...*",
            parse_mode='Markdown'
        )
        
        try:
            # Создание конфигурации
            config = self.create_bot_config(session)
            
            # Генерация бота
            bot_path = await self.generate_enhanced_bot(config)
            
            # Создание архива
            archive_path = await self.create_bot_archive(bot_path, config.restaurant_name)
            
            await processing_msg.edit_text(
                f"🧠 *Интеллектуальный бот для '{config.restaurant_name}' готов!*",
                parse_mode='Markdown'
            )
            
            # Отправка файла
            await self.send_bot_file(update, user_id, archive_path, config)
            
            # Сброс сессии
            self.user_sessions[user_id] = {"step": "menu", "data": {}, "config": BotConfiguration(restaurant_name="")}
            
        except Exception as e:
            await processing_msg.edit_text(
                f"❌ *Ошибка при создании бота:*\n`{str(e)}`",
                parse_mode='Markdown'
            )
    
    def create_bot_config(self, session: Dict) -> BotConfiguration:
        """Создание конфигурации бота"""
        config = session.get("config", BotConfiguration(restaurant_name=""))
        
        # Обновляем API ключи
        api_keys = session["data"].get("api_keys", {})
        config.api_keys = api_keys
        
        # Обновляем промпт если есть
        prompt = session["data"].get("prompt", "")
        if prompt:
            config.ai_prompt = prompt
        
        return config
    
    async def generate_enhanced_bot(self, config: BotConfiguration) -> str:
        """Генерация улучшенного бота"""
        # Генерация с персональными ключами
        return self.generator.generate_bot(config.restaurant_name, config.api_keys)
    
    async def create_bot_archive(self, bot_path: str, restaurant_name: str) -> str:
        """Создание архива с ботом"""
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
    
    async def send_bot_file(self, update: Update, user_id: int, archive_path: str, config: BotConfiguration):
        """Отправка файла с ботом"""
        success_text = f"""🧠 *Интеллектуальный бот для "{config.restaurant_name}" готов!*

📦 *Что в архиве:*
• 🤖 Продвинутый AI-бот
• 🔑 Ваши API ключи уже настроены
• 📊 Интеграция с данными
• 🌐 Веб-интеллект
• 💰 Sales-стратегии
• 📋 Полная документация

🚀 *Умные возможности:*
• 🎯 Персонализация диалогов
• 📊 Анализ предпочтений
• 🔮 Предсказание потребностей
• 🌐 Автообновление данных
• 💬 Генерация ответов

💰 *Монетизация:*
• $100-300 за настройку
• 5-15% с AI-продаж
• $50/мес за поддержку

🔥 *Бот готов к запуску!*"""
        
        keyboard = [[InlineKeyboardButton("🧠 Создать еще бота", callback_data="create_prompt")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправка файла
        with open(archive_path, 'rb') as file:
            await update.effective_message.reply_document(
                document=file,
                filename=f"{config.restaurant_name.replace(' ', '_')}_bot.zip",
                caption=success_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        # Удаление временного файла
        os.remove(archive_path)
    
    def get_main_menu_keyboard(self):
        """Клавиатура главного меню"""
        keyboard = [
            [InlineKeyboardButton("🧠 Создать по промпту", callback_data="create_prompt")],
            [InlineKeyboardButton("⚙️ Пошаговая настройка", callback_data="create_stepwise")],
            [InlineKeyboardButton("📋 Загрузить данные", callback_data="upload_data")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def setup_handlers(self, application: Application):
        """Настройка обработчиков"""
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(CallbackQueryHandler(self.create_minimal_callback, pattern="create_minimal"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

def main():
    """Запуск динамического бота"""
    from dotenv import load_dotenv
    load_dotenv()
    
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден")
        return
    
    application = Application.builder().token(telegram_token).build()
    architect = DynamicTokenArchitect(telegram_token)
    architect.setup_handlers(application)
    
    print("🚀 Dynamic Token Architect запущен!")
    print("🔑 Готов к вводу токенов в Telegram!")
    
    application.run_polling()

if __name__ == "__main__":
    main()
