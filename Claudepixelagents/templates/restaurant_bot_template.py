"""
Restaurant Bot Template
Шаблон чат-бота для ресторанов с записью на консультации
Стек: FastAPI + Trigger.dev + Groq + Google Sheets API + WhatsApp (Green-API)
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import gspread
from oauth2client.service_account import ServiceAccountCredentials

@dataclass
class BookingData:
    """Данные для бронирования консультации"""
    client_name: str
    phone: str
    date: str
    guests_count: int
    budget: str
    event_type: str = "банкет"
    notes: str = ""

class WhatsAppMessage(BaseModel):
    """Модель входящего сообщения WhatsApp"""
    phone: str
    message: str
    timestamp: str

class RestaurantBot:
    """Основной класс бота ресторана"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.restaurant_name = config.get("restaurant_name", "Ресторан")
        self.groq_api_key = config.get("groq_api_key")
        self.green_api_instance = config.get("green_api_instance")
        self.green_api_token = config.get("green_api_token")
        self.google_sheets_url = config.get("google_sheets_url")
        self.google_credentials_path = config.get("google_credentials_path")
        
        # Инициализация клиентов
        self.groq_client = None
        self.sheets_client = None
        self.worksheet = None
        
        # Состояния диалогов
        self.user_states: Dict[str, Dict] = {}
        
    async def initialize(self):
        """Инициализация клиентов API"""
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
    
    async def process_message(self, phone: str, message: str) -> str:
        """Обработка входящего сообщения"""
        user_state = self.user_states.get(phone, {"step": "greeting"})
        
        # Определение шага диалога
        if user_state["step"] == "greeting":
            return await self.handle_greeting(phone, message)
        elif user_state["step"] == "collect_name":
            return await self.handle_collect_name(phone, message)
        elif user_state["step"] == "collect_date":
            return await self.handle_collect_date(phone, message)
        elif user_state["step"] == "collect_guests":
            return await self.handle_collect_guests(phone, message)
        elif user_state["step"] == "collect_budget":
            return await self.handle_collect_budget(phone, message)
        elif user_state["step"] == "confirmation":
            return await self.handle_confirmation(phone, message)
        else:
            return await self.handle_greeting(phone, message)
    
    async def handle_greeting(self, phone: str, message: str) -> str:
        """Обработка приветствия"""
        greeting_msg = f"""🍽️ Добро пожаловать в {self.restaurant_name}!

Я помогу вам записаться на консультацию по организации банкета или мероприятия.

Для начала, представьтесь, пожалуйста:
📝 Как вас зовут?"""
        
        self.user_states[phone] = {"step": "collect_name", "data": {}}
        return greeting_msg
    
    async def handle_collect_name(self, phone: str, message: str) -> str:
        """Сбор имени клиента"""
        self.user_states[phone]["step"] = "collect_date"
        self.user_states[phone]["data"]["client_name"] = message.strip()
        
        return f"""Приятно познакомиться, {message.strip()}! 🎉

Теперь выберите желаемую дату консультации:
📅 Введите дату в формате ДД.ММ.ГГГГ"""
    
    async def handle_collect_date(self, phone: str, message: str) -> str:
        """Сбор даты консультации"""
        # Проверка формата даты
        try:
            date_obj = datetime.strptime(message.strip(), "%d.%m.%Y")
            if date_obj < datetime.now():
                return "❌ Дата не может быть в прошлом. Пожалуйста, введите корректную дату:"
            
            # Проверка доступности слота
            is_available = await self.check_date_availability(message.strip())
            if not is_available:
                return "❌ К сожалению, эта дата уже занята. Выберите другую дату:"
            
            self.user_states[phone]["step"] = "collect_guests"
            self.user_states[phone]["data"]["date"] = message.strip()
            
            return "Отлично! 📝 Сколько гостей планируется на мероприятии?"
            
        except ValueError:
            return "❌ Неверный формат даты. Используйте формат ДД.ММ.ГГГГ:"
    
    async def handle_collect_guests(self, phone: str, message: str) -> str:
        """Сбор количества гостей"""
        try:
            guests = int(message.strip())
            if guests < 1:
                return "❌ Количество гостей должно быть положительным числом:"
            
            self.user_states[phone]["step"] = "collect_budget"
            self.user_states[phone]["data"]["guests_count"] = guests
            
            return "Хорошо! 💰 Какой бюджет вы планируете на мероприятие?"
            
        except ValueError:
            return "❌ Пожалуйста, введите корректное число гостей:"
    
    async def handle_collect_budget(self, phone: str, message: str) -> str:
        """Сбор бюджета"""
        self.user_states[phone]["step"] = "confirmation"
        self.user_states[phone]["data"]["budget"] = message.strip()
        
        data = self.user_states[phone]["data"]
        confirmation_msg = f"""🎯 Проверьте ваши данные:

👤 Имя: {data['client_name']}
📅 Дата: {data['date']}
👥 Гостей: {data['guests_count']}
💰 Бюджет: {data['budget']}

Все верно? Ответьте "Да" для подтверждения или "Нет" для изменений."""
        
        return confirmation_msg
    
    async def handle_confirmation(self, phone: str, message: str) -> str:
        """Подтверждение и сохранение заявки"""
        if message.lower() in ["да", "yes", "д"]:
            # Сохранение в Google Sheets
            success = await self.save_booking(phone, self.user_states[phone]["data"])
            
            if success:
                # Настройка напоминания через Trigger.dev
                await self.schedule_reminder(phone, self.user_states[phone]["data"])
                
                # Сброс состояния
                self.user_states[phone] = {"step": "greeting", "data": {}}
                
                return f"""✅ Заявка успешно оформлена!

🎉 Мы ждем вас на консультацию {self.user_states[phone]['data']['date']}
📍 Наш менеджер свяжется с вами для подтверждения

Спасибо за обращение в {self.restaurant_name}! 🍽️"""
            else:
                return "❌ Произошла ошибка при сохранении заявки. Попробуйте позже."
        
        elif message.lower() in ["нет", "no", "н"]:
            self.user_states[phone] = {"step": "greeting", "data": {}}
            return "Давайте начнем заново. Как вас зовут?"
        
        else:
            return "Пожалуйста, ответьте 'Да' или 'Нет':"
    
    async def check_date_availability(self, date: str) -> bool:
        """Проверка доступности даты в Google Sheets"""
        if not self.worksheet:
            return True  # Если нет доступа к таблице, считаем дату доступной
        
        try:
            # Поиск даты в таблице
            records = self.worksheet.get_all_records()
            for record in records:
                if record.get("Дата") == date:
                    return False
            return True
        except:
            return True
    
    async def save_booking(self, phone: str, data: Dict) -> bool:
        """Сохранение заявки в Google Sheets"""
        if not self.worksheet:
            return False
        
        try:
            # Добавление новой строки
            row = [
                datetime.now().strftime("%d.%m.%Y %H:%M"),  # Время создания
                data["client_name"],
                phone,
                data["date"],
                data["guests_count"],
                data["budget"],
                "Новая"  # Статус
            ]
            
            self.worksheet.append_row(row)
            return True
        except Exception as e:
            print(f"Error saving booking: {e}")
            return False
    
    async def schedule_reminder(self, phone: str, data: Dict):
        """Настройка напоминания через Trigger.dev"""
        # Здесь будет интеграция с Trigger.dev
        # Отправка задачи на напоминание за 2 часа до консультации
        pass
    
    async def send_whatsapp_message(self, phone: str, message: str):
        """Отправка сообщения через WhatsApp (Green-API)"""
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

# FastAPI приложение
app = FastAPI(title="Restaurant Bot API")

# Глобальная переменная для бота
bot: Optional[RestaurantBot] = None

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
        "google_credentials_path": os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    }
    
    bot = RestaurantBot(config)
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
    return {"status": "healthy", "bot_initialized": bot is not None}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
