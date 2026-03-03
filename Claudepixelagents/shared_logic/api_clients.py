"""
Общие клиенты для работы с API
Используется всеми генерируемыми ботами
"""

import asyncio
import json
from typing import Dict, Any, Optional
import httpx
from datetime import datetime

class GroqClient:
    """Клиент для работы с Groq API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.client = None
    
    async def initialize(self):
        """Инициализация HTTP клиента"""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
    
    async def chat_completion(self, messages: list, model: str = "llama3-70b-8192") -> str:
        """Отправка запроса к chat completion"""
        if not self.client:
            await self.initialize()
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Groq API error: {e}")
            return "Извините, произошла ошибка при обработке запроса."
    
    async def close(self):
        """Закрытие клиента"""
        if self.client:
            await self.client.aclose()

class GreenAPIClient:
    """Клиент для работы с Green-API (WhatsApp)"""
    
    def __init__(self, instance_id: str, token: str):
        self.instance_id = instance_id
        self.token = token
        self.base_url = f"https://api.green-api.com/waInstance{instance_id}"
        self.client = None
    
    async def initialize(self):
        """Инициализация HTTP клиента"""
        self.client = httpx.AsyncClient()
    
    async def send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Отправка сообщения WhatsApp"""
        if not self.client:
            await self.initialize()
        
        url = f"{self.base_url}/sendMessage/{self.token}"
        payload = {
            "chatId": f"{phone}@c.us",
            "message": message
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Green-API error: {e}")
            return {"error": str(e)}
    
    async def get_instance_info(self) -> Dict[str, Any]:
        """Получение информации об инстансе"""
        if not self.client:
            await self.initialize()
        
        url = f"{self.base_url}/getInstanceInfo/{self.token}"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Green-API error: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Закрытие клиента"""
        if self.client:
            await self.client.aclose()

class TriggerDevClient:
    """Клиент для работы с Trigger.dev"""
    
    def __init__(self, api_key: str, project_id: str):
        self.api_key = api_key
        self.project_id = project_id
        self.base_url = "https://api.trigger.dev"
        self.client = None
    
    async def initialize(self):
        """Инициализация HTTP клиента"""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
    
    async def schedule_reminder(self, phone: str, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Планирование напоминания о консультации"""
        if not self.client:
            await self.initialize()
        
        # Расчет времени напоминания (за 2 часа до консультации)
        booking_datetime = datetime.strptime(booking_data["date"], "%d.%m.%Y")
        reminder_time = booking_datetime - timedelta(hours=2)
        
        payload = {
            "job": "send-reminder",
            "payload": {
                "phone": phone,
                "client_name": booking_data["client_name"],
                "date": booking_data["date"],
                "time": reminder_time.isoformat()
            },
            "schedule": {
                "type": "scheduled",
                "runAt": reminder_time.isoformat()
            }
        }
        
        try:
            response = await self.client.post(f"/v1/projects/{self.project_id}/jobs", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Trigger.dev error: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Закрытие клиента"""
        if self.client:
            await self.client.aclose()

class MessageTemplates:
    """Шаблоны сообщений для бота"""
    
    @staticmethod
    def greeting(restaurant_name: str) -> str:
        """Приветственное сообщение"""
        return f"""🍽️ Добро пожаловать в {restaurant_name}!

Я помогу вам записаться на консультацию по организации банкета или мероприятия.

Для начала, представьтесь, пожалуйста:
📝 Как вас зовут?"""
    
    @staticmethod
    def ask_date() -> str:
        """Запрос даты"""
        return """Теперь выберите желаемую дату консультации:
📅 Введите дату в формате ДД.ММ.ГГГГ"""
    
    @staticmethod
    def ask_guests() -> str:
        """Запрос количества гостей"""
        return "Отлично! 📝 Сколько гостей планируется на мероприятие?"
    
    @staticmethod
    def ask_budget() -> str:
        """Запрос бюджета"""
        return "Хорошо! 💰 Какой бюджет вы планируете на мероприятие?"
    
    @staticmethod
    def confirmation(data: Dict[str, Any]) -> str:
        """Сообщение подтверждения"""
        return f"""🎯 Проверьте ваши данные:

👤 Имя: {data['client_name']}
📅 Дата: {data['date']}
👥 Гостей: {data['guests_count']}
💰 Бюджет: {data['budget']}

Все верно? Ответьте "Да" для подтверждения или "Нет" для изменений."""
    
    @staticmethod
    def success(restaurant_name: str, date: str) -> str:
        """Сообщение об успешной записи"""
        return f"""✅ Заявка успешно оформлена!

🎉 Мы ждем вас на консультацию {date}
📍 Наш менеджер свяжется с вами для подтверждения

Спасибо за обращение в {restaurant_name}! 🍽️"""
    
    @staticmethod
    def error_message() -> str:
        """Сообщение об ошибке"""
        return "❌ Произошла ошибка. Попробуйте позже или свяжитесь с нами напрямую."
    
    @staticmethod
    def reminder_message(client_name: str, date: str) -> str:
        """Сообщение напоминания"""
        return f"""🔔 Напоминание о консультации!

Уважаемый(ая) {client_name},
Напоминаем о вашей консультации сегодня ({date}).

Мы ждем вас! 🍽️"""
