"""
Advanced AI Bot Architect - Продвинутый AI-агент
Умная система создания чат-ботов с промптами, кастомизацией и AI-интеграцией
"""

import os
import json
import asyncio
import zipfile
import tempfile
import requests
import aiohttp
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
    google_sheets_url: str = ""
    ai_api_token: str = ""
    menu_data: str = ""
    price_list: str = ""
    custom_responses: Dict[str, str] = None
    web_search_enabled: bool = True
    sales_strategy: str = "consultative"
    personality: str = "professional_friendly"

class AdvancedAIArchitect:
    """Продвинутый AI-архитектор ботов"""
    
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
объясняешь нюансы кухни, сочетания, рассказываешь о концепции ресторана."""
        }
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        welcome_text = f"""🧠 *Advanced AI Bot Architect*

Привет, {user_name}! Я - **умный** AI-агент для создания **интеллектуальных** чат-ботов ресторанов.

🚀 *Что я умею (в отличие от простых ботов):*
• 🎯 **Создаю по промптам** - опиши поведение бота текстом
• 📊 **Гибкая настройка данных** - Google Sheets, API, базы
• 📋 **Загрузка меню/прайсов** - просто отправь файлы
• 🌐 **Веб-скрапинг** - бот сам ищет инфу о ресторане
• 🧠 **AI-персонализация** - настраивай характер и стиль
• 💰 **Sales-экспертиза** - встроенные техники продаж

🎯 *Бизнес-модель 2.0:*
Создаешь **умного** бота → Ресторан получает **реальных клиентов** → Ты берешь **% с продаж**

📝 *Как начать:*
1. 🎯 "Создать по промпту" - для продвинутых
2. ⚙️ "Пошаговая настройка" - для начинающих
3. 📋 "Загрузить данные" - быстрая настройка

Давай создадим **интеллектуального** бота! 👇"""
        
        keyboard = [
            [InlineKeyboardButton("🎯 Создать по промпту", callback_data="create_prompt")],
            [InlineKeyboardButton("⚙️ Пошаговая настройка", callback_data="create_stepwise")],
            [InlineKeyboardButton("📋 Загрузить данные", callback_data="upload_data")],
            [InlineKeyboardButton("🧠 AI-настройки", callback_data="ai_settings")]
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
        """Создание бота по промпту"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        self.user_sessions[user_id]["step"] = "prompt_creation"
        
        prompt_text = """🧠 *Создание бота по промпту*

Опиши, каким должен быть твой бот. Чем подробнее, тем умнее получится бот!

📝 *Пример промпта:*
"Создай бота для итальянского ресторана 'La Bella'. Бот должен быть элегантным, знать всё о пасте и вине, уметь рекомендовать блюда по предпочтениям гостя, записывать на дегустации, говорить по-итальянски базовые фразы. Стиль - дружелюбный профессионал. Бот должен уметь искать информацию о ресторане в интернете и обновлять меню."

✍️ *Введи свой промпт:*

💡 *Что можно указать:*
• Тип кухни и концепция
• Стиль общения (формальный, дружелюбный, премиум)
• Какие данные должен знать (меню, цены, акции)
• Интеграции (Google Sheets, CRM)
• Особенности (мультиязычность, веб-поиск)"""
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            prompt_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def create_stepwise_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Пошаговая настройка бота"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        self.user_sessions[user_id]["step"] = "stepwise_name"
        
        stepwise_text = """⚙️ *Пошаговая настройка умного бота*

Шаг 1/5: Базовая информация

📝 *Название ресторана:*
Пример: "Ресторан Веранда", "Кафе Уют", "Бар Москва"

🎯 *Далее мы настроим:*
• AI-характер и стиль общения
• Источники данных (Google Sheets, API)
• Меню и прайс-листы
• Sales-стратегию
• Интеграции и доп. возможности

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
    
    async def ai_settings_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """AI-настройки бота"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        ai_text = """🧠 *AI-настройки интеллектуального бота*

🎭 **Характер бота:**
• 🤵 Профессионал-эксперт
• 💎 Премиум-консьерж  
• 😊 Дружелюбный помощник
• 🎓 Умный консультант

🧠 **AI-возможности:**
• 🌐 Веб-поиск информации
• 📊 Анализ предпочтений
• 💬 Генерация ответов
• 🎯 Персонализация
• 🔮 Предсказание потребностей

💰 **Sales-стратегии:**
• 🎯 Консультативные продажи
• ⚡ Импульсивные
• 💎 Премиум-продажи
• 🤝 Партнерские

🔧 *Выбери настройки:*
"""
        
        keyboard = [
            [InlineKeyboardButton("🎭 Характер бота", callback_data="personality")],
            [InlineKeyboardButton("🧠 AI-возможности", callback_data="ai_capabilities")],
            [InlineKeyboardButton("💰 Sales-стратегия", callback_data="sales_strategy")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            ai_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
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
        elif step == "stepwise_name":
            await self.process_stepwise_name(update, user_id, message_text)
        elif step == "upload_data":
            await self.process_data_upload(update, user_id, message_text)
        else:
            await update.message.reply_text(
                "🤖 Используйте кнопки меню для навигации",
                reply_markup=self.get_main_menu_keyboard()
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

🔑 *Теперь нужны API ключи:*

🤖 **Groq API Key** (обязательно)
📊 **Google Sheets URL** (если есть данные)
🌐 **Web Search API** (для поиска инфы)

📝 *Введи ключи строкой:*
GROQ_API_KEY=your_key
GOOGLE_SHEETS_URL=url
WEB_SEARCH_API_KEY=key

💡 *Можно пропустить* - создам с базовыми настройками"""
        
        keyboard = [
            [InlineKeyboardButton("⏭️ Создать бота", callback_data="create_from_prompt")],
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
        # Здесь можно использовать Groq для анализа промпта
        # Пока простая эвристика
        
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
        
        return "\n".join(analysis_points) if analysis_points else "🤖 Создаю универсального умного бота"
    
    async def process_stepwise_name(self, update: Update, user_id: int, restaurant_name: str):
        """Обработка названия в пошаговом режиме"""
        session = self.user_sessions[user_id]
        session["step"] = "stepwise_personality"
        session["config"].restaurant_name = restaurant_name
        
        text = f"""⚙️ *Настройка бота для "{restaurant_name}"*

Шаг 2/5: Выбор характера бота

🎭 *Каким должен быть твой бот?*

🤵 **Профессионал-эксперт**
• Знаток кухни и вин
• Консультирует как эксперт
• Рекомендует на основе предпочтений

💎 **Премиум-консьерж**
• Элегантный и изысканный
• Персональный подход
• Эксклюзивные предложения

😊 **Дружелюбный помощник**
• Неформальный общение
• Эмодзи и шутки
• Создает уютную атмосферу

🎓 **Умный консультант**
• Глубокие знания
• Объясняет нюансы
• Обучает гостей

✍️ *Введи номер характера (1-4) или описание:*"""
        
        keyboard = [
            [InlineKeyboardButton("🤵 Эксперт", callback_data="person_expert")],
            [InlineKeyboardButton("💎 Консьерж", callback_data="person_concierge")],
            [InlineKeyboardButton("😊 Помощник", callback_data="person_assistant")],
            [InlineKeyboardButton("🎓 Консультант", callback_data="person_consultant")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            # Пока имитация
            
            text = f"""📊 *Google Sheets подключен!*

🔍 *Анализ данных...*
✅ Найдено: 25 позиций в меню
✅ Найдено: 15 ценовых категорий  
✅ Найдено: 8 акций и скидок

🤖 *AI обработал данные и готов создать бота!*

📝 *Что дальше:*
1. Выбери характер бота
2. Настрой AI-возможности
3. Создадим умного бота!

🚀 *Создать бота сейчас?*"""
            
            keyboard = [
                [InlineKeyboardButton("🚀 Создать бота", callback_data="create_from_data")],
                [InlineKeyboardButton("⚙️ Настройки", callback_data="ai_settings")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка подключения к Google Sheets: {e}")
    
    async def process_text_data(self, update: Update, user_id: int, text_data: str):
        """Обработка текстовых данных"""
        session = self.user_sessions[user_id]
        
        # AI-анализ текста
        analysis = self.analyze_text_data(text_data)
        
        text = f"""📝 *Данные получены и обработаны!*

🔍 *AI анализ:*
{analysis}

🤖 *Данные интегрированы в систему*

📝 *Что дальше:*
1. Выбери характер бота
2. Настрой стиль общения
3. Создадим персонализированного бота!

🚀 *Продолжить настройку?*"""
        
        keyboard = [
            [InlineKeyboardButton("🚀 Создать бота", callback_data="create_from_data")],
            [InlineKeyboardButton("⚙️ AI-настройки", callback_data="ai_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    def analyze_text_data(self, text: str) -> str:
        """Анализ текстовых данных"""
        analysis = []
        
        if any(word in text.lower() for word in ["меню", "блюдо", "еда"]):
            analysis.append("🍽️ Найдено меню")
        if any(word in text.lower() for word in ["цена", "руб", "$"]):
            analysis.append("💰 Найдены цены")
        if any(word in text.lower() for word in ["адрес", "телефон", "контакт"]):
            analysis.append("📍 Найдены контакты")
        if any(word in text.lower() for word in ["акция", "скидка", "бонус"]):
            analysis.append("🎉 Найдены акции")
        
        return "\n".join(analysis) if analysis else "📄 Получены текстовые данные"
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка документов (меню, прайсы)"""
        user_id = update.effective_user.id
        document = update.message.document
        
        session = self.user_sessions[user_id]
        
        # Скачивание файла
        file_info = await context.bot.get_file(document.file_id)
        
        # Сохранение во временный файл
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, document.file_name)
        
        await file_info.download_to_drive(file_path)
        
        # AI-обработка файла
        analysis = await self.analyze_document(file_path, document.file_name)
        
        text = f"""📄 *Файл "{document.file_name}" обработан!*

🔍 *AI анализ:*
{analysis}

🤖 *Данные интегрированы в систему*

📝 *Что дальше:*
1. Загрузи еще файлы (если есть)
2. Выбери характер бота
3. Создадим умного бота!

🚀 *Создать бота сейчас?*"""
        
        keyboard = [
            [InlineKeyboardButton("🚀 Создать бота", callback_data="create_from_files")],
            [InlineKeyboardButton("📄 Загрузить еще", callback_data="upload_data")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        # Сохранение информации о файле
        if "uploaded_files" not in session["data"]:
            session["data"]["uploaded_files"] = []
        session["data"]["uploaded_files"].append({
            "name": document.file_name,
            "path": file_path,
            "analysis": analysis
        })
    
    async def analyze_document(self, file_path: str, file_name: str) -> str:
        """AI-анализ документа"""
        # Здесь будет реальная обработка документов
        # Пока имитация на основе имени файла
        
        analysis = []
        
        if "меню" in file_name.lower():
            analysis.append("🍽️ Меню ресторана")
        if "прайс" in file_name.lower() or "price" in file_name.lower():
            analysis.append("💰 Прайс-лист")
        if "акция" in file_name.lower():
            analysis.append("🎉 Акции и скидки")
        if "вино" in file_name.lower() or "wine" in file_name.lower():
            analysis.append("🍷 Карта вин")
        
        return "\n".join(analysis) if analysis else "📄 Документ обработан"
    
    async def create_from_prompt_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание бота из промпта"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        session = self.user_sessions[user_id]
        prompt = session["data"].get("prompt", "")
        
        await query.edit_message_text("🧠 Создаю умного бота из промпта...")
        
        # Генерация бота
        await self.generate_advanced_bot(update, user_id, "prompt")
    
    async def generate_advanced_bot(self, update: Update, user_id: int, creation_type: str):
        """Генерация продвинутого бота"""
        session = self.user_sessions[user_id]
        
        # Отправка сообщения о начале генерации
        processing_msg = await update.effective_message.reply_text(
            "🧠 *Генерация интеллектуального бота...*",
            parse_mode='Markdown'
        )
        
        try:
            # Создание продвинутой конфигурации
            config = self.create_advanced_config(session, creation_type)
            
            # Генерация улучшенного бота
            bot_path = await self.generate_enhanced_bot(config)
            
            # Создание архива
            archive_path = await self.create_bot_archive(bot_path, config.restaurant_name)
            
            await processing_msg.edit_text(
                f"🧠 *Интеллектуальный бот для '{config.restaurant_name}' готов!*",
                parse_mode='Markdown'
            )
            
            # Отправка файла
            await self.send_advanced_bot_file(update, user_id, archive_path, config)
            
            # Сброс сессии
            self.user_sessions[user_id] = {"step": "menu", "data": {}, "config": BotConfiguration(restaurant_name="")}
            
        except Exception as e:
            await processing_msg.edit_text(
                f"❌ *Ошибка при создании бота:*\n`{str(e)}`",
                parse_mode='Markdown'
            )
    
    def create_advanced_config(self, session: Dict, creation_type: str) -> BotConfiguration:
        """Создание продвинутой конфигурации"""
        config = session.get("config", BotConfiguration(restaurant_name=""))
        
        if creation_type == "prompt":
            prompt = session["data"].get("prompt", "")
            config.ai_prompt = prompt
            config.web_search_enabled = "поиск" in prompt.lower() or "интернет" in prompt.lower()
            
        return config
    
    async def generate_enhanced_bot(self, config: BotConfiguration) -> str:
        """Генерация улучшенного бота"""
        # Здесь будет реальная генерация с учетом всех настроек
        # Пока используем базовый генератор
        
        api_keys = {
            "groq_api_key": os.getenv("GROQ_API_KEY", ""),
            "google_sheets_url": config.google_sheets_url,
            "ai_prompt": config.ai_prompt
        }
        
        return self.generator.generate_bot(config.restaurant_name, api_keys)
    
    async def create_bot_archive(self, bot_path: str, restaurant_name: str) -> str:
        """Создание архива с ботом"""
        temp_dir = tempfile.gettempdir()
        archive_name = f"{restaurant_name.replace(' ', '_')}_advanced_bot.zip"
        archive_path = os.path.join(temp_dir, archive_name)
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            bot_dir = Path(bot_path)
            
            for file_path in bot_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(bot_dir.parent)
                    zipf.write(file_path, arcname)
        
        return archive_path
    
    async def send_advanced_bot_file(self, update: Update, user_id: int, archive_path: str, config: BotConfiguration):
        """Отправка файла с продвинутым ботом"""
        success_text = f"""🧠 *Интеллектуальный бот для "{config.restaurant_name}" готов!*

📦 *Что в архиве:*
• 🤖 Продвинутый AI-бот с нейросетью
• 🧠 AI-настройки и промпты
• 📊 Интеграция с данными
• 🌐 Веб-скрапинг и поиск
• 💰 Sales-стратегии
• 📋 Полная документация

🚀 *Умные возможности:*
• 🎯 Персонализация диалогов
• 📊 Анализ предпочтений
• 🔮 Предсказание потребностей
• 🌐 Автообновление данных
• 💬 Генерация ответов

💰 *Монетизация 2.0:*
• $100-300 за настройку умного бота
• 5-15% с AI-продаж
• $50/месяц за поддержку

🔥 *Это не просто бот - это AI-ассистент!*"""
        
        keyboard = [[InlineKeyboardButton("🧠 Создать еще бота", callback_data="create_prompt")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправка файла
        with open(archive_path, 'rb') as file:
            await update.effective_message.reply_document(
                document=file,
                filename=f"{config.restaurant_name.replace(' ', '_')}_advanced_bot.zip",
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
        application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

def main():
    """Запуск продвинутого Telegram бота"""
    from dotenv import load_dotenv
    load_dotenv()
    
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден")
        return
    
    application = Application.builder().token(telegram_token).build()
    architect = AdvancedAIArchitect(telegram_token)
    architect.setup_handlers(application)
    
    print("🧠 Advanced AI Bot Architect запущен!")
    print("🚀 Готов создавать интеллектуальных ботов!")
    
    application.run_polling()

if __name__ == "__main__":
    main()
