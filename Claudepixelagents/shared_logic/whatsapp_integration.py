"""
Интеграция с WhatsApp через Green-API
Полная функциональность для работы с WhatsApp
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
import httpx
from datetime import datetime
import base64
import mimetypes

class WhatsAppIntegration:
    """Основной класс для интеграции с WhatsApp"""
    
    def __init__(self, instance_id: str, token: str):
        self.instance_id = instance_id
        self.token = token
        self.base_url = f"https://api.green-api.com/waInstance{instance_id}"
        self.client = None
        self.webhook_url = None
    
    async def initialize(self, webhook_url: str = None):
        """Инициализация клиента и настройка вебхука"""
        self.client = httpx.AsyncClient()
        self.webhook_url = webhook_url
        
        # Настройка вебхука если указан
        if webhook_url:
            await self.set_webhook(webhook_url)
    
    async def set_webhook(self, webhook_url: str) -> bool:
        """Установка URL для вебхука"""
        try:
            url = f"{self.base_url}/setWebHook/{self.token}"
            payload = {"webhookUrl": webhook_url}
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("result", False)
        except Exception as e:
            print(f"Error setting webhook: {e}")
            return False
    
    async def send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Отправка текстового сообщения"""
        try:
            url = f"{self.base_url}/sendMessage/{self.token}"
            payload = {
                "chatId": f"{phone}@c.us",
                "message": message
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error sending message: {e}")
            return {"error": str(e)}
    
    async def send_image(self, phone: str, image_url: str, caption: str = "") -> Dict[str, Any]:
        """Отправка изображения"""
        try:
            url = f"{self.base_url}/sendFileByUrl/{self.token}"
            payload = {
                "chatId": f"{phone}@c.us",
                "urlFile": image_url,
                "fileName": "image.jpg",
                "caption": caption
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error sending image: {e}")
            return {"error": str(e)}
    
    async def send_file(self, phone: str, file_url: str, file_name: str, caption: str = "") -> Dict[str, Any]:
        """Отправка файла"""
        try:
            url = f"{self.base_url}/sendFileByUrl/{self.token}"
            payload = {
                "chatId": f"{phone}@c.us",
                "urlFile": file_url,
                "fileName": file_name,
                "caption": caption
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error sending file: {e}")
            return {"error": str(e)}
    
    async def send_location(self, phone: str, latitude: float, longitude: float, name: str, address: str) -> Dict[str, Any]:
        """Отправка геолокации"""
        try:
            url = f"{self.base_url}/sendLocation/{self.token}"
            payload = {
                "chatId": f"{phone}@c.us",
                "latitude": latitude,
                "longitude": longitude,
                "name": name,
                "address": address
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error sending location: {e}")
            return {"error": str(e)}
    
    async def send_contact(self, phone: str, contact_name: str, contact_phone: str) -> Dict[str, Any]:
        """Отправка контакта"""
        try:
            url = f"{self.base_url}/sendContact/{self.token}"
            payload = {
                "chatId": f"{phone}@c.us",
                "contact": {
                    "name": contact_name,
                    "phone": contact_phone
                }
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error sending contact: {e}")
            return {"error": str(e)}
    
    async def get_instance_info(self) -> Dict[str, Any]:
        """Получение информации об инстансе"""
        try:
            url = f"{self.base_url}/getInstanceInfo/{self.token}"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error getting instance info: {e}")
            return {"error": str(e)}
    
    async def get_chat_history(self, phone: str, count: int = 100) -> List[Dict[str, Any]]:
        """Получение истории чата"""
        try:
            url = f"{self.base_url}/getChatHistory/{self.token}"
            payload = {
                "chatId": f"{phone}@c.us",
                "count": count
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []
    
    async def qr_code(self) -> Dict[str, Any]:
        """Получение QR кода для подключения WhatsApp"""
        try:
            url = f"{self.base_url}/qrCode/{self.token}"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error getting QR code: {e}")
            return {"error": str(e)}
    
    async def logout(self) -> bool:
        """Выход из WhatsApp"""
        try:
            url = f"{self.base_url}/logout/{self.token}"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            result = response.json()
            return result.get("result", False)
        except Exception as e:
            print(f"Error logging out: {e}")
            return False
    
    async def close(self):
        """Закрытие HTTP клиента"""
        if self.client:
            await self.client.aclose()

class WhatsAppMessageHandler:
    """Обработчик входящих сообщений WhatsApp"""
    
    def __init__(self, whatsapp_integration: WhatsAppIntegration):
        self.whatsapp = whatsapp_integration
        self.message_handlers = {}
    
    def register_handler(self, message_type: str, handler_func):
        """Регистрация обработчика для типа сообщения"""
        self.message_handlers[message_type] = handler_func
    
    async def handle_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Обработка входящего вебхука"""
        try:
            # Извлечение данных сообщения
            messages = webhook_data.get("messages", [])
            
            for message in messages:
                message_type = message.get("typeMessage", "text")
                sender = message.get("senderId", "").replace("@c.us", "")
                
                # Обработка в зависимости от типа сообщения
                if message_type == "text":
                    await self._handle_text_message(sender, message)
                elif message_type == "image":
                    await self._handle_image_message(sender, message)
                elif message_type == "document":
                    await self._handle_document_message(sender, message)
                elif message_type == "location":
                    await self._handle_location_message(sender, message)
                elif message_type == "contact":
                    await self._handle_contact_message(sender, message)
                else:
                    await self._handle_unknown_message(sender, message)
            
            return True
        except Exception as e:
            print(f"Error handling webhook: {e}")
            return False
    
    async def _handle_text_message(self, sender: str, message: Dict[str, Any]):
        """Обработка текстового сообщения"""
        text_content = message.get("textMessage", "")
        
        if "text" in self.message_handlers:
            await self.message_handlers["text"](sender, text_content)
    
    async def _handle_image_message(self, sender: str, message: Dict[str, Any]):
        """Обработка изображения"""
        image_data = message.get("imageMessage", {})
        caption = image_data.get("caption", "")
        
        if "image" in self.message_handlers:
            await self.message_handlers["image"](sender, image_data, caption)
    
    async def _handle_document_message(self, sender: str, message: Dict[str, Any]):
        """Обработка документа"""
        document_data = message.get("documentMessage", {})
        
        if "document" in self.message_handlers:
            await self.message_handlers["document"](sender, document_data)
    
    async def _handle_location_message(self, sender: str, message: Dict[str, Any]):
        """Обработка геолокации"""
        location_data = message.get("locationMessage", {})
        
        if "location" in self.message_handlers:
            await self.message_handlers["location"](sender, location_data)
    
    async def _handle_contact_message(self, sender: str, message: Dict[str, Any]):
        """Обработка контакта"""
        contact_data = message.get("contactMessage", {})
        
        if "contact" in self.message_handlers:
            await self.message_handlers["contact"](sender, contact_data)
    
    async def _handle_unknown_message(self, sender: str, message: Dict[str, Any]):
        """Обработка неизвестного типа сообщения"""
        if "unknown" in self.message_handlers:
            await self.message_handlers["unknown"](sender, message)

class WhatsAppBotTemplates:
    """Шаблоны сообщений для WhatsApp бота"""
    
    @staticmethod
    def welcome_message(restaurant_name: str) -> str:
        """Приветственное сообщение"""
        return f"""🍽️ *Добро пожаловать в {restaurant_name}!*

Я ваш персональный ассистент по организации мероприятий.

Я помогу вам:
✅ Записаться на консультацию
✅ Узнать о наших услугах
✅ Получить расчет стоимости

Давайте начнем! Как вас зовут?"""
    
    @staticmethod
    def menu_message() -> str:
        """Сообщение с меню"""
        return """📋 *Чем я могу помочь?*

1️⃣ Записаться на консультацию
2️⃣ Узнать о банкетных пакетах
3️⃣ Получить прайс-лист
4️⃣ Связаться с менеджером

Выберите номер или напишите свой вопрос:"""
    
    @staticmethod
    def packages_message() -> str:
        """Информация о пакетах"""
        return """🎉 *Наши банкетные пакеты:*

💎 *Премиум* - от 5000₽/чел
• Полный сервис
• Индивидуальное меню
• Декор и флористика

🌟 *Стандарт* - от 3000₽/чел
• Банкетное меню
• Базовый декор
• Координатор

🎈 *Эконом* - от 1500₽/чел
• Фуршет
• Минимальный сервис

Хотите подробную консультацию по пакету?"""
    
    @staticmethod
    def booking_confirmation(data: Dict[str, Any]) -> str:
        """Подтверждение бронирования"""
        return f"""✅ *Ваша заявка принята!*

📋 *Детали консультации:*
👤 Имя: {data['client_name']}
📅 Дата: {data['date']}
👥 Гостей: {data['guests_count']}
💰 Бюджет: {data['budget']}

Наш менеджер свяжется с вами в течение 15 минут для подтверждения.

Спасибо за выбор нашего ресторана! 🍽️"""
    
    @staticmethod
    def quick_replies() -> List[str]:
        """Быстрые ответы"""
        return [
            "Записаться на консультацию",
            "Узнать о пакетах",
            "Прайс-лист",
            "Связаться с менеджером"
        ]
    
    @staticmethod
    def format_phone_number(phone: str) -> str:
        """Форматирование номера телефона для WhatsApp"""
        # Удаляем все символы кроме цифр
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Если номер начинается с 8, заменяем на 7
        if clean_phone.startswith('8') and len(clean_phone) == 11:
            clean_phone = '7' + clean_phone[1:]
        
        return clean_phone
