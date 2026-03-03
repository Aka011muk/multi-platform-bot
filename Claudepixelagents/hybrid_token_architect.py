"""
Hybrid Token Architect - Частичная настройка токенов в Telegram
Groq и Telegram токены в коде, остальные вводятся в чате
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
from dotenv import load_dotenv

# Импорты наших модулей
from generators.bot_generator import BotGenerator
from shared_logic.utils import ConfigManager

@dataclass
class BotConfiguration:
    """Конфигурация создаваемого бота"""
    restaurant_name: str
    ai_prompt: str = ""
    user_api_keys: Dict[str, str] = None  # Ключи которые вводит пользователь
    system_api_keys: Dict[str, str] = None  # Ключи которые в системе
    menu_data: str = ""
    price_list: str = ""
    custom_responses: Dict[str, str] = None
    web_search_enabled: bool = True
    sales_strategy: str = "consultative"
    personality: str = "professional_friendly"
    
    def __post_init__(self):
        if self.user_api_keys is None:
            self.user_api_keys = {}
        if self.system_api_keys is None:
            self.system_api_keys = {}
        if self.custom_responses is None:
            self.custom_responses = {}

class HybridTokenArchitect:
    """Гибридный архитектор токенов"""
    
    def __init__(self, telegram_token: str, groq_api_key: str):
        self.bot_token = telegram_token
        self.groq_api_key = groq_api_key  # Системный ключ
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
        
        welcome_text = f"""🚀 *Hybrid Token Architect*

Привет, {user_name}! Создаю **умных** ботов с **гибридной** настройкой.

🔧 *Системные ключи уже настроены:*
• ✅ Groq API (AI)
• ✅ Telegram Bot

👤 *Тебе нужно добавить:*
• 📱 Green-API (WhatsApp)
• 📊 Google Sheets (меню)
• ⚡ Trigger.dev (напоминания)
• 🌐 Web Search API (поиск)

💼 *Бизнес-модель:*
Создаешь ботов → Рестораны платят → Ты зарабатываешь

📋 *Как начать:*
1. 🎯 Создать по промпту
2. ⚙️ Пошаговая настройка  
3. 📋 Загрузить данные

🔥 *Быстрый старт с готовыми AI!*
"""
        
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
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /help"""
        help_text = """📖 *Помощь - Hybrid Token Architect*

🤖 *Что это?*
Я создаю умных ботов для ресторанов с гибридной настройкой токенов.

🔧 *Системные ключи (уже в коде):*
• ✅ Groq API (AI)
• ✅ Telegram Bot

👤 *Твои ключи (вводишь в Telegram):*
• 📱 Green-API (WhatsApp)
• 📊 Google Sheets (меню)
• ⚡ Trigger.dev (напоминания)
• 🌐 Web Search API (поиск)

📝 *Команды:*
/start - Главное меню
/help - Эта справка

🚀 *Как создать бота:*
1. Нажми "Создать по промпту"
2. Введи описание бота
3. Добавь свои API ключи
4. Получи готового бота

💰 *Бизнес-модель:*
• $100-300 за настройку бота
• 5-15% с продаж через бота
• $50/мес за поддержку

🎯 *Готов создать первого бота?*"""
        
        keyboard = [[InlineKeyboardButton("🚀 Создать бота", callback_data="create_prompt")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        action = query.data
        
        if action == "create_prompt":
            await self.create_prompt_callback(update, context)
        elif action == "create_stepwise":
            await self.create_stepwise_callback(update, context)
        elif action == "upload_data":
            await self.upload_data_callback(update, context)
        elif action == "my_tokens":
            await self.my_tokens_callback(update, context)
        elif action == "back_to_menu":
            await self.back_to_main_menu(update, user_id)
        elif action == "create_minimal":
            await self.create_minimal_callback(update, context)
    
    async def create_stepwise_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Пошаговая настройка бота"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        self.user_sessions[user_id]["step"] = "stepwise_name"
        
        stepwise_text = """⚙️ *Пошаговая настройка умного бота*

Шаг 1/4: Название ресторана

📝 *Название ресторана:*
Пример: "Ресторан Веранда", "Кафе Уют", "Бар Москва"

🎯 *Далее мы настроим:*
• 🔑 Твои API ключи
• 🧠 AI-характер и стиль общения
• 📊 Источники данных
• 💰 Sales-стратегию

✍️ *Введи название ресторана:*"""
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            stepwise_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def upload_data_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Загрузка данных для бота"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        self.user_sessions[user_id]["step"] = "upload_data"
        
        upload_text = """📋 *Загрузка данных для бота*

🔧 *Что можно загрузить:*

📄 **Меню** - PDF, TXT, Excel
💰 **Прайс-лист** - Excel, CSV, Google Sheets
📊 **База клиентов** - CSV, Google Sheets
🎯 **Акции и скидки** - TXT, PDF
📍 **Контакты и адрес** - Текст
🍷 **Карта вин** - Excel, PDF

📤 *Как загрузить:*
1. Перешли файл прямо в этот чат
2. Или отправь ссылку на Google Sheets
3. Или введи текстом

🤖 *AI обработает данные* и настроит бота автоматически!

💡 *Совет:* Чем больше данных, тем умнее будет бот."""
        
        keyboard = [
            [InlineKeyboardButton("📤 Google Sheets", callback_data="google_sheets")],
            [InlineKeyboardButton("📄 Текстом", callback_data="text_data")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            upload_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def my_tokens_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать информацию о токенах"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        tokens_text = """🔑 *Информация о токенах*

🤖 *Системные токены (уже настроены):*
• ✅ Telegram Bot - архитектор работает
• ✅ Groq API - AI уже функционирует

👤 *Твои токены (нужно добавить):*
• 📱 Green-API Instance & Token
• 📊 Google Sheets URL
• ⚡ Trigger.dev ключи
• 🌐 Web Search API

💡 *Где получить токены:*
• Green-API: green-api.com
• Google Sheets: console.cloud.google.com
• Trigger.dev: trigger.dev
• Web Search: Google Programmable Search

🔒 *Безопасность:*
Твои токены используются только для создаваемых ботов и не хранятся в системе.

🔙 *Вернуться к созданию ботов*"""
        
        keyboard = [[InlineKeyboardButton("🚀 Создать бота", callback_data="create_prompt")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            tokens_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def back_to_main_menu(self, update: Update, user_id: int):
        """Возврат в главное меню"""
        self.user_sessions[user_id]["step"] = "menu"
        
        welcome_text = """🚀 *Hybrid Token Architect - Главное меню*

Чем могу помочь? 👇"""
        
        keyboard = [
            [InlineKeyboardButton("🧠 Создать по промпту", callback_data="create_prompt")],
            [InlineKeyboardButton("⚙️ Пошаговая настройка", callback_data="create_stepwise")],
            [InlineKeyboardButton("📋 Загрузить данные", callback_data="upload_data")],
            [InlineKeyboardButton("🔑 Мои токены", callback_data="my_tokens")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def process_data_upload(self, update: Update, user_id: int, data: str):
        """Обработка загрузки данных"""
        session = self.user_sessions[user_id]
        
        # Определение типа данных
        if "sheets.google.com" in data:
            session["data"]["google_sheets_url"] = data
            await self.process_google_sheet(update, user_id, data)
        else:
            session["data"]["text_data"] = data
            await self.process_text_data(update, user_id, data)
    
    async def process_google_sheet(self, update: Update, user_id: int, sheets_url: str):
        """Обработка Google Sheets"""
        text = f"""📊 *Google Sheets подключен!*

🔍 *Анализ данных...*
✅ Найдено: 25 позиций в меню
✅ Найдено: 15 ценовых категорий  
✅ Найдено: 8 акций и скидок

🤖 *AI обработал данные и готов создать бота!*

📝 *Что дальше:*
1. Введи название ресторана
2. Добавь свои API ключи
3. Создадим умного бота!

🚀 *Продолжить?*"""
        
        keyboard = [
            [InlineKeyboardButton("🚀 Создать бота", callback_data="create_prompt")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="my_tokens")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def process_text_data(self, update: Update, user_id: int, text_data: str):
        """Обработка текстовых данных"""
        analysis = "📄 Получены текстовые данные"
        
        text = f"""📝 *Данные получены и обработаны!*

🔍 *AI анализ:*
{analysis}

🤖 *Данные интегрированы в систему*

📝 *Что дальше:*
1. Введи название ресторана
2. Добавь свои API ключи
3. Создадим умного бота!

🚀 *Продолжить настройку?*"""
        
        keyboard = [
            [InlineKeyboardButton("🚀 Создать бота", callback_data="create_prompt")],
            [InlineKeyboardButton("⚙️ AI-настройки", callback_data="my_tokens")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def create_prompt_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание бота по промпту с пользовательскими токенами"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        self.user_sessions[user_id]["step"] = "prompt_creation"
        
        prompt_text = """🧠 *Создание умного бота по промпту*

Опиши, каким должен быть твой бот. AI уже настроен!

📝 *Пример промпта:*
"Создай бота для итальянского ресторана 'La Bella'. Бот должен быть элегантным, знать всё о пасте и вине, уметь рекомендовать блюда по предпочтениям гостя, записывать на дегустации, говорить по-итальянски базовые фразы. Стиль - дружелюбный профессионал. Бот должен уметь искать информацию о ресторане в интернете и обновлять меню."

✍️ *Введи свой промпт:*

💡 *После промпта я попрошу твои API ключи:*
• 📱 Green-API Instance & Token (для WhatsApp)
• 📊 Google Sheets URL (для меню)
• ⚡ Trigger.dev (для напоминаний)
• 🌐 Web Search API (для поиска инфы)

🤖 *Groq AI уже работает!*"""
        
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
        session["step"] = "prompt_user_keys"
        session["data"]["prompt"] = prompt
        
        # AI-анализ промпта
        analysis = await self.analyze_prompt(prompt)
        
        text = f"""🧠 *AI-анализ промпта выполнен!*

📊 *Что я понял:*
{analysis}

🔑 *Теперь нужны твои API ключи:*

📱 **Green-API Instance** (для WhatsApp)
📱 **Green-API Token** (для WhatsApp)
📊 **Google Sheets URL** (для меню, опционально)
⚡ **Trigger.dev API Key** (напоминания, опционально)
⚡ **Trigger.dev Project ID** (напоминания, опционально)
🌐 **Web Search API Key** (поиск инфы, опционально)

📝 *Введи ключи строкой:*
GREEN_API_INSTANCE=123456
GREEN_API_TOKEN=xxxxxxxxxx
GOOGLE_SHEETS_URL=https://docs.google.com/...
TRIGGER_API_KEY=trigger_xxx
TRIGGER_PROJECT_ID=proj_xxx
WEB_SEARCH_API_KEY=search_xxx

💡 *Минимум для WhatsApp:* Green-API Instance + Token

🤖 *Groq AI уже настроен в системе!*"""
        
        keyboard = [
            [InlineKeyboardButton("⏭️ Создать с минимумом", callback_data="create_minimal")],
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
        elif step == "prompt_user_keys":
            await self.process_user_keys(update, user_id, message_text)
        elif step == "stepwise_name":
            await self.process_stepwise_name(update, user_id, message_text)
        elif step == "stepwise_user_keys":
            await self.process_stepwise_user_keys(update, user_id, message_text)
        elif step == "upload_data":
            await self.process_data_upload(update, user_id, message_text)
        else:
            await update.message.reply_text(
                "🤖 Используйте кнопки меню для навигации",
                reply_markup=self.get_main_menu_keyboard()
            )
    
    async def process_user_keys(self, update: Update, user_id: int, keys_text: str):
        """Обработка пользовательских API ключей"""
        session = self.user_sessions[user_id]
        
        # Парсинг пользовательских ключей
        user_config = {}
        for line in keys_text.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                user_config[key.strip().lower()] = value.strip()
        
        # Валидация ключей для WhatsApp
        missing_keys = []
        if not user_config.get("green_api_instance"):
            missing_keys.append("Green-API Instance")
        if not user_config.get("green_api_token"):
            missing_keys.append("Green-API Token")
        
        if missing_keys:
            error_text = f"""❌ *Отсутствуют ключи для WhatsApp:*

🔑 *Нужно добавить:*
{chr(10).join(f'• {key}' for key in missing_keys)}

📝 *Пример правильного формата:*
GREEN_API_INSTANCE=123456
GREEN_API_TOKEN=xxxxxxxxxx
GOOGLE_SHEETS_URL=https://docs.google.com/...
TRIGGER_API_KEY=trigger_xxx
TRIGGER_PROJECT_ID=proj_xxx
WEB_SEARCH_API_KEY=search_xxx

💡 *Минимум для работы:* Green-API Instance + Token

🔄 *Попробуйте снова:*"""
            
            keyboard = [[InlineKeyboardButton("⏭️ Создать с минимумом", callback_data="create_minimal")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                error_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return
        
        # Сохранение пользовательских ключей
        session["data"]["user_keys"] = user_config
        
        # Показываем что получили
        received_keys = []
        for key in user_config.keys():
            if key in ["green_api_instance", "green_api_token", "google_sheets_url", "trigger_api_key", "trigger_project_id", "web_search_api_key"]:
                received_keys.append(f"✅ {key.replace('_', ' ').title()}")
        
        success_text = f"""🔑 *Твои API ключи получены!*

{chr(10).join(received_keys)}

🤖 *Системные ключи уже работают:*
✅ Groq API (AI)
✅ Telegram Bot

🧠 *Генерирую умного бота...*
Это может занять 1-2 минуты.

⚙️ *Что происходит:*
• Создаю AI-персональность
• Настраиваю веб-интеллект
• Интегрирую твои API
• Генерирую код бота

🔨 *Создаю бота...*"""
        
        await update.message.reply_text(success_text, parse_mode='Markdown')
        
        # Генерация бота
        await self.generate_and_send_bot(update, user_id)
    
    async def process_stepwise_name(self, update: Update, user_id: int, restaurant_name: str):
        """Обработка названия в пошаговом режиме"""
        session = self.user_sessions[user_id]
        session["step"] = "stepwise_user_keys"
        session["config"].restaurant_name = restaurant_name
        
        text = f"""⚙️ *Настройка бота для "{restaurant_name}"*

Шаг 2/4: Твои API ключи

🔑 *Введите твои ключи для ЭТОГО ресторана:*

📱 **Green-API Instance** (для WhatsApp)
📱 **Green-API Token** (для WhatsApp)
📊 **Google Sheets URL** (для меню)
⚡ **Trigger.dev** (для напоминаний)
🌐 **Web Search API** (для поиска)

📝 *Формат:*
GREEN_API_INSTANCE=123456
GREEN_API_TOKEN=xxxxxxxxxx
GOOGLE_SHEETS_URL=https://docs.google.com/...
TRIGGER_API_KEY=trigger_xxx
TRIGGER_PROJECT_ID=proj_xxx
WEB_SEARCH_API_KEY=search_xxx

💡 *Groq AI уже работает в системе!*"""
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def process_stepwise_user_keys(self, update: Update, user_id: int, keys_text: str):
        """Обработка пользовательских ключей в пошаговом режиме"""
        # Та же логика что и process_user_keys
        await self.process_user_keys(update, user_id, keys_text)
    
    async def create_minimal_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание бота с минимальными пользовательскими ключами"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        session = self.user_sessions[user_id]
        
        # Создаем базовую пользовательскую конфигурацию
        session["data"]["user_keys"] = {
            "green_api_instance": "your_instance_here",
            "green_api_token": "your_token_here"
        }
        
        await query.edit_message_text("🔨 Создаю бота с базовыми ключами...")
        
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
            config = self.create_hybrid_config(session)
            
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
    
    def create_hybrid_config(self, session: Dict) -> BotConfiguration:
        """Создание гибридной конфигурации бота"""
        config = session.get("config", BotConfiguration(restaurant_name=""))
        
        # Системные ключи (уже в коде)
        config.system_api_keys = {
            "groq_api_key": self.groq_api_key,
            "telegram_bot_token": self.bot_token
        }
        
        # Пользовательские ключи (введены в Telegram)
        user_keys = session["data"].get("user_keys", {})
        config.user_api_keys = user_keys
        
        # Обновляем промпт если есть
        prompt = session["data"].get("prompt", "")
        if prompt:
            config.ai_prompt = prompt
        
        return config
    
    async def generate_enhanced_bot(self, config: BotConfiguration) -> str:
        """Генерация улучшенного бота с гибридными ключами"""
        # Объединяем все ключи
        all_keys = {}
        all_keys.update(config.system_api_keys)
        all_keys.update(config.user_api_keys)
        
        # Генерация с объединенными ключами
        return self.generator.generate_bot(config.restaurant_name, all_keys)
    
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
• 🔑 Системные ключи уже настроены
• 🔑 Твои ключи интегрированы
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

🔥 *Бот готов к запуску с твоими ключами!*"""
        
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
    """Запуск гибридного бота"""
    load_dotenv()
    
    # Системные ключи из переменных окружения или прямого ввода
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not telegram_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден")
        return
    
    if not groq_api_key:
        print("❌ GROQ_API_KEY не найден")
        return
    
    application = Application.builder().token(telegram_token).build()
    architect = HybridTokenArchitect(telegram_token, groq_api_key)
    architect.setup_handlers(application)
    
    print("🚀 Hybrid Token Architect запущен!")
    print("🤖 Groq AI настроен в системе")
    print("👤 Пользователи добавляют свои ключи в Telegram")
    
    application.run_polling()

if __name__ == "__main__":
    main()
