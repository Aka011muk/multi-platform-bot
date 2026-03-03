"""
Advanced Restaurant Bot Template
Продвинутый шаблон чат-бота для ресторанов с AI-возможностями
Стек: FastAPI + Trigger.dev + Groq + Google Sheets API + Web Intelligence
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Импорты продвинутых модулей
from shared_logic.web_intelligence import RestaurantDataIntegrator
from shared_logic.flexible_config import FlexibleConfigManager, DataConnector, SalesStrategyManager, DynamicResponseGenerator

@dataclass
class AdvancedBookingData:
    """Расширенные данные для бронирования"""
    client_name: str
    phone: str
    email: str = ""
    date: str = ""
    time: str = ""
    guests_count: int = 0
    budget: str = ""
    event_type: str = "банкет"
    preferences: List[str] = None
    special_requests: str = ""
    marketing_source: str = ""
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = []

class AdvancedRestaurantBot:
    """Продвинутый бот ресторана с AI-возможностями"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.restaurant_name = config.get("restaurant_name", "Ресторан")
        self.groq_api_key = config.get("groq_api_key")
        self.green_api_instance = config.get("green_api_instance")
        self.green_api_token = config.get("green_api_token")
        self.google_sheets_url = config.get("google_sheets_url")
        self.google_credentials_path = config.get("google_credentials_path")
        
        # AI-компоненты
        self.data_integrator = RestaurantDataIntegrator(config.get("search_api_key"))
        self.config_manager = FlexibleConfigManager()
        self.data_connector = DataConnector(self.config_manager)
        self.sales_manager = SalesStrategyManager()
        self.response_generator = DynamicResponseGenerator(self.config_manager, self.sales_manager)
        
        # Инициализация клиентов
        self.groq_client = None
        self.sheets_client = None
        self.worksheet = None
        
        # Состояния диалогов
        self.user_states: Dict[str, Dict] = {}
        
        # Данные ресторана
        self.restaurant_data = {}
        self.menu_data = []
        self.pricing_data = []
        
    async def initialize(self):
        """Инициализация всех компонентов"""
        # Инициализация Groq
        self.groq_client = httpx.AsyncClient(
            base_url="https://api.groq.com/openai/v1",
            headers={"Authorization": f"Bearer {self.groq_api_key}"}
        )
        
        # Инициализация Google Sheets
        if self.google_credentials_path and os.path.exists(self.google_credentials_path):
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.google_credentials_path, scope)
            self.sheets_client = gspread.authorize(creds)
            self.worksheet = self.sheets_client.open_by_url(self.google_sheets_url).sheet1
        
        # Инициализация AI-компонентов
        await self.data_integrator.initialize()
        await self.data_connector.initialize()
        
        # Загрузка конфигурации
        config_file = self.config.get("config_file", "bot_config.json")
        if os.path.exists(config_file):
            self.config_manager.load_from_file(config_file)
        
        # Загрузка данных ресторана
        await self.load_restaurant_data()
    
    async def load_restaurant_data(self):
        """Загрузка данных о ресторане"""
        try:
            # Получение данных из интернета
            self.restaurant_data = await self.data_integrator.get_comprehensive_restaurant_data(
                self.restaurant_name, 
                self.config.get("city", "")
            )
            
            # Получение данных из настроенных источников
            self.menu_data = await self.data_connector.get_menu_data()
            self.pricing_data = await self.data_connector.get_pricing_data()
            
            print(f"✅ Данные ресторана загружены: {len(self.menu_data)} позиций в меню")
            
        except Exception as e:
            print(f"Error loading restaurant data: {e}")
    
    async def process_message(self, phone: str, message: str) -> str:
        """Обработка входящего сообщения с AI"""
        user_state = self.user_states.get(phone, {"step": "greeting"})
        
        # Контекст для AI
        context = {
            "user_phone": phone,
            "restaurant_data": self.restaurant_data,
            "menu_data": self.menu_data,
            "pricing_data": self.pricing_data,
            "user_state": user_state
        }
        
        # Генерация динамического ответа
        if user_state["step"] == "greeting":
            return await self.handle_greeting(phone, message, context)
        elif user_state["step"] == "conversation":
            # AI-обработка в режиме диалога
            return await self.handle_ai_conversation(phone, message, context)
        else:
            # Стандартная обработка состояний
            return await self.handle_standard_flow(phone, message, context)
    
    async def handle_greeting(self, phone: str, message: str, context: Dict) -> str:
        """Обработка приветствия с AI"""
        # Проверка, есть ли у пользователя уже состояние
        if phone in self.user_states and self.user_states[phone].get("step") != "greeting":
            return await self.process_message(phone, message)
        
        # AI-генерация приветствия
        personality = self.config_manager.personality
        if personality:
            greeting_style = personality.greeting_style
        else:
            greeting_style = "friendly"
        
        if greeting_style == "luxury":
            greeting_msg = f"""💎 Добро пожаловать в {self.restaurant_name}!

Я ваш персональный консьерж. Готов предоставить эксклюзивный сервис и помочь с выбором лучших блюд и вин.

Чем могу быть полезен сегодня?"""
        elif greeting_style == "professional":
            greeting_msg = f"""🍽️ Добро пожаловать в {self.restaurant_name}!

Я профессиональный ассистент ресторана. Могу помочь с выбором блюд, бронированием столика или организацией мероприятия.

Что вас интересует?"""
        else:
            greeting_msg = f"""😊 Добро пожаловать в {self.restaurant_name}!

Рад помочь вам! Могу рассказать о меню, забронировать столик или помочь с организацией праздника.

Что хотите узнать?"""
        
        self.user_states[phone] = {"step": "conversation", "data": {}}
        return greeting_msg
    
    async def handle_ai_conversation(self, phone: str, message: str, context: Dict) -> str:
        """AI-обработка диалога"""
        try:
            # Генерация ответа с помощью AI
            response = await self.response_generator.generate_response(message, context)
            
            # Анализ на наличие намерения к бронированию
            if self._detect_booking_intent(message):
                self.user_states[phone]["step"] = "booking_start"
                return await self.start_booking_flow(phone, context)
            
            return response
            
        except Exception as e:
            print(f"Error in AI conversation: {e}")
            return "Извините, произошла ошибка. Попробуйте переформулировать вопрос."
    
    def _detect_booking_intent(self, message: str) -> bool:
        """Определение намерения забронировать"""
        booking_keywords = [
            "бронь", "забронировать", "столик", "резерв", "записаться",
            "посетить", "прийти", "мероприятие", "банкет", "день рождения"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in booking_keywords)
    
    async def start_booking_flow(self, phone: str, context: Dict) -> str:
        """Начало процесса бронирования"""
        return """📅 Отлично! Помогу с бронированием.

Для начала, расскажите немного о вашем мероприятии:
• Количество гостей
• Желаемая дата и время
• Повод (если есть)

С чего начнем?"""
    
    async def handle_standard_flow(self, phone: str, message: str, context: Dict) -> str:
        """Стандартная обработка состояний"""
        user_state = self.user_states.get(phone, {"step": "greeting"})
        
        if user_state["step"] == "collect_name":
            return await self.handle_collect_name(phone, message, context)
        elif user_state["step"] == "collect_date":
            return await self.handle_collect_date(phone, message, context)
        elif user_state["step"] == "collect_guests":
            return await self.handle_collect_guests(phone, message, context)
        elif user_state["step"] == "collect_budget":
            return await self.handle_collect_budget(phone, message, context)
        elif user_state["step"] == "confirmation":
            return await self.handle_confirmation(phone, message, context)
        else:
            return await self.handle_greeting(phone, message, context)
    
    async def handle_collect_name(self, phone: str, message: str, context: Dict) -> str:
        """Сбор имени клиента с AI-персонализацией"""
        self.user_states[phone]["step"] = "collect_date"
        self.user_states[phone]["data"]["client_name"] = message.strip()
        
        # Персонализированный ответ
        personality = self.config_manager.personality
        if personality and personality.communication_tone == "enthusiastic":
            return f"""🎉 Приятно познакомиться, {message.strip()}!

Теперь выберите желаемую дату консультации:
📅 Введите дату в формате ДД.ММ.ГГГГ

У нас есть особые предложения для первого визита! ✨"""
        else:
            return f"""Приятно познакомиться, {message.strip()}!

Выберите желаемую дату консультации:
📅 Введите дату в формате ДД.ММ.ГГГГ"""
    
    async def handle_collect_date(self, phone: str, message: str, context: Dict) -> str:
        """Сбор даты с учетом загруженности"""
        try:
            date_obj = datetime.strptime(message.strip(), "%d.%m.%Y")
            if date_obj < datetime.now():
                return "❌ Дата не может быть в прошлом. Пожалуйста, введите корректную дату:"
            
            # Проверка доступности с учетом загруженности
            is_available = await self.check_date_availability_with_ai(message.strip(), context)
            if not is_available:
                # AI-предложение альтернатив
                alternatives = await self.suggest_alternative_dates(message.strip(), context)
                return f"""❌ К сожалению, эта дата уже занята.

🗓️ Альтернативные даты:
{alternatives}

Какая дата вам подходит?"""
            
            self.user_states[phone]["step"] = "collect_guests"
            self.user_states[phone]["data"]["date"] = message.strip()
            
            return "Отлично! 📝 Сколько гостей планируется на мероприятии?"
            
        except ValueError:
            return "❌ Неверный формат даты. Используйте формат ДД.ММ.ГГГГ:"
    
    async def check_date_availability_with_ai(self, date: str, context: Dict) -> bool:
        """Проверка доступности даты с AI-анализом"""
        if not self.worksheet:
            return True
        
        try:
            records = self.worksheet.get_all_records()
            
            # AI-анализ загруженности
            bookings_on_date = [r for r in records if r.get("Дата") == date]
            
            # Если более 5 бронирований, считаем днем загруженным
            return len(bookings_on_date) < 5
        except:
            return True
    
    async def suggest_alternative_dates(self, requested_date: str, context: Dict) -> str:
        """AI-предложение альтернативных дат"""
        try:
            date_obj = datetime.strptime(requested_date, "%d.%m.%Y")
            alternatives = []
            
            # Предлагаем ближайшие свободные даты
            for i in range(1, 8):
                alt_date = date_obj + timedelta(days=i)
                alt_date_str = alt_date.strftime("%d.%m.%Y")
                
                if await self.check_date_availability_with_ai(alt_date_str, context):
                    alternatives.append(f"• {alt_date_str} ({alt_date.strftime('%A')})")
                
                if len(alternatives) >= 3:
                    break
            
            return "\n".join(alternatives)
        except:
            return "• Свяжитесь с менеджером для подбора даты"
    
    async def handle_collect_guests(self, phone: str, message: str, context: Dict) -> str:
        """Сбор количества гостей с AI-рекомендациями"""
        try:
            guests = int(message.strip())
            if guests < 1:
                return "❌ Количество гостей должно быть положительным числом:"
            
            self.user_states[phone]["step"] = "collect_budget"
            self.user_states[phone]["data"]["guests_count"] = guests
            
            # AI-рекомендации на основе количества гостей
            if guests <= 4:
                recommendation = "Для небольшой компании идеально подойдут столики в основном зале."
            elif guests <= 10:
                recommendation = "Для вашей компании могу предложить VIP-зону или объединенные столики."
            else:
                recommendation = "Для большого количества гостей у нас есть банкетный зал и специальные предложения."
            
            return f"""Хорошо! 👥 {guests} гостей.

{recommendation}

💰 Какой бюджет вы планируете на мероприятие?"""
            
        except ValueError:
            return "❌ Пожалуйста, введите корректное число гостей:"
    
    async def handle_collect_budget(self, phone: str, message: str, context: Dict) -> str:
        """Сбор бюджета с AI-анализом"""
        self.user_states[phone]["step"] = "confirmation"
        self.user_states[phone]["data"]["budget"] = message.strip()
        
        data = self.user_states[phone]["data"]
        
        # AI-анализ бюджета и рекомендации
        budget_analysis = await self.analyze_budget(message.strip(), data["guests_count"])
        
        confirmation_msg = f"""🎯 Проверьте ваши данные:

👤 Имя: {data['client_name']}
📅 Дата: {data['date']}
👥 Гостей: {data['guests_count']}
💰 Бюджет: {data['budget']}

{budget_analysis}

Все верно? Ответьте "Да" для подтверждения или "Нет" для изменений."""
        
        return confirmation_msg
    
    async def analyze_budget(self, budget: str, guests: int) -> str:
        """AI-анализ бюджета"""
        # Извлечение числового значения бюджета
        import re
        budget_match = re.search(r'(\d+)', budget.replace(' ', ''))
        
        if budget_match:
            budget_num = int(budget_match.group(1))
            per_person = budget_num / guests
            
            if per_person < 500:
                return f"💡 Бюджет ~{per_person:.0f} ₽/чел - рекомендуем бизнес-ланч или фуршет."
            elif per_person < 1500:
                return f"💡 Бюджет ~{per_person:.0f} ₽/чел - отличный выбор для банкета с полным сервисом."
            else:
                return f"💡 Бюджет ~{per_person:.0f} ₽/чел - премиум-обслуживание с индивидуальным подходом."
        
        return ""
    
    async def handle_confirmation(self, phone: str, message: str, context: Dict) -> str:
        """Подтверждение с AI-персонализацией"""
        if message.lower() in ["да", "yes", "д"]:
            # Сохранение в Google Sheets
            success = await self.save_advanced_booking(phone, self.user_states[phone]["data"])
            
            if success:
                # Настройка напоминания через Trigger.dev
                await self.schedule_advanced_reminder(phone, self.user_states[phone]["data"])
                
                # AI-генерация финального сообщения
                final_message = await self.generate_final_message(phone, self.user_states[phone]["data"])
                
                # Сброс состояния
                self.user_states[phone] = {"step": "conversation", "data": {}}
                
                return final_message
            else:
                return "❌ Произошла ошибка при сохранении заявки. Попробуйте позже."
        
        elif message.lower() in ["нет", "no", "н"]:
            self.user_states[phone] = {"step": "conversation", "data": {}}
            return "Давайте начнем заново. Что вас интересует?"
        
        else:
            return "Пожалуйста, ответьте 'Да' или 'Нет':"
    
    async def generate_final_message(self, phone: str, data: Dict) -> str:
        """AI-генерация финального сообщения"""
        personality = self.config_manager.personality
        
        base_message = f"""✅ Заявка успешно оформлена!

🎉 Мы ждем вас на консультацию {data['date']}
📍 Наш менеджер свяжется с вами для подтверждения
📞 В случае вопросов: +7 (XXX) XXX-XX-XX

Спасибо за обращение в {self.restaurant_name}! 🍽️"""
        
        if personality and personality.communication_tone == "enthusiastic":
            return f"""🎉 {base_message}

🔥 Не забудьте про нашу акцию для первого визита!
✨ Ждем вас в гости!"""
        
        return base_message
    
    async def save_advanced_booking(self, phone: str, data: Dict) -> bool:
        """Сохранение расширенной заявки"""
        if not self.worksheet:
            return False
        
        try:
            # Расширенная строка для таблицы
            row = [
                datetime.now().strftime("%d.%m.%Y %H:%M"),
                data.get("client_name", ""),
                phone,
                data.get("date", ""),
                data.get("guests_count", ""),
                data.get("budget", ""),
                "Новая",
                data.get("event_type", "банкет"),
                data.get("special_requests", ""),
                json.dumps(data.get("preferences", [])),
                self._detect_marketing_source(phone)
            ]
            
            self.worksheet.append_row(row)
            return True
        except Exception as e:
            print(f"Error saving advanced booking: {e}")
            return False
    
    def _detect_marketing_source(self, phone: str) -> str:
        """Определение маркетингового источника"""
        # Логика определения источника по номеру телефона или другим данным
        return "WhatsApp Bot"
    
    async def schedule_advanced_reminder(self, phone: str, data: Dict):
        """Расширенное напоминание через Trigger.dev"""
        # Здесь будет интеграция с Trigger.dev
        # Отправка нескольких напоминаний:
        # - За 24 часа
        # - За 2 часа  
        # - За 30 минут
        pass
    
    async def send_whatsapp_message(self, phone: str, message: str):
        """Отправка сообщения через WhatsApp"""
        if not self.green_api_instance or not self.green_api_token:
            return
        
        try:
            url = f"https://api.green-api.com/waInstance{self.green_api_instance}/sendMessage/{self.green_api_token}"
            payload = {
                "chatId": f"{phone}@c.us",
                "message": message
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                return response.json()
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return None
    
    async def get_ai_recommendations(self, user_preferences: List[str]) -> List[Dict]:
        """AI-рекомендации блюд"""
        recommendations = []
        
        for preference in user_preferences:
            # Поиск блюд по предпочтениям
            matching_dishes = [
                dish for dish in self.menu_data
                if preference.lower() in dish.get("name", "").lower() or 
                   preference.lower() in dish.get("description", "").lower()
            ]
            
            recommendations.extend(matching_dishes[:3])
        
        return recommendations
    
    async def close(self):
        """Закрытие всех компонентов"""
        if self.groq_client:
            await self.groq_client.aclose()
        
        await self.data_integrator.close()
        await self.data_connector.close()

# FastAPI приложение
app = FastAPI(title="Advanced Restaurant Bot API")

# Глобальная переменная для бота
bot: Optional[AdvancedRestaurantBot] = None

@app.on_event("startup")
async def startup_event():
    """Инициализация бота при запуске"""
    global bot
    config = {
        "restaurant_name": os.getenv("RESTAURANT_NAME", "Ресторан"),
        "groq_api_key": os.getenv("GROQ_API_KEY"),
        "green_api_instance": os.getenv("GREEN_API_INSTANCE"),
        "green_api_token": os.getenv("GREEN_API_TOKEN"),
        "google_sheets_url": os.getenv("GOOGLE_SHEETS_URL"),
        "google_credentials_path": os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"),
        "search_api_key": os.getenv("SEARCH_API_KEY"),
        "city": os.getenv("CITY", ""),
        "config_file": os.getenv("BOT_CONFIG_FILE", "bot_config.json")
    }
    
    bot = AdvancedRestaurantBot(config)
    await bot.initialize()

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(message: WhatsAppMessage):
    """Вебхук для приема сообщений WhatsApp"""
    if not bot:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    # Обработка сообщения
    response = await bot.process_message(message.phone, message.message)
    
    # Отправка ответа
    await bot.send_whatsapp_message(message.phone, response)
    
    return JSONResponse(content={"status": "success", "response": response})

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy", 
        "bot_initialized": bot is not None,
        "features": [
            "ai_conversation",
            "web_intelligence", 
            "flexible_config",
            "advanced_booking"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
