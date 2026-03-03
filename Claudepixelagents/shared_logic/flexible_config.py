"""
Flexible Configuration Module
Гибкая настройка данных, API и интеграций для ресторанных ботов
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

# Опциональные импорты
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

@dataclass
class DataSource:
    """Источник данных"""
    type: str  # google_sheets, api, database, file
    config: Dict[str, Any]
    credentials: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    last_sync: Optional[datetime] = None

@dataclass
class APIIntegration:
    """API интеграция"""
    name: str
    endpoint: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    auth_type: str = "none"  # none, api_key, bearer, oauth
    credentials: Dict[str, Any] = field(default_factory=dict)
    rate_limit: int = 100  # запросов в минуту
    timeout: int = 30

@dataclass
class BotPersonality:
    """Персональность бота"""
    name: str
    greeting_style: str  # formal, casual, luxury, friendly
    communication_tone: str  # professional, enthusiastic, calm, energetic
    language_style: str  # formal, informal, mixed
    emoji_usage: str  # minimal, moderate, heavy
    response_length: str  # short, medium, long
    specialties: List[str] = field(default_factory=list)

class FlexibleConfigManager:
    """Менеджер гибкой конфигурации"""
    
    def __init__(self):
        self.data_sources: List[DataSource] = []
        self.api_integrations: List[APIIntegration] = []
        self.personality: BotPersonality = None
        self.custom_responses: Dict[str, str] = {}
        self.sales_config: Dict[str, Any] = {}
        
    def load_from_file(self, config_path: str) -> bool:
        """Загрузка конфигурации из файла"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Загрузка источников данных
            for ds_config in config.get("data_sources", []):
                data_source = DataSource(**ds_config)
                self.data_sources.append(data_source)
            
            # Загрузка API интеграций
            for api_config in config.get("api_integrations", []):
                api_integration = APIIntegration(**api_config)
                self.api_integrations.append(api_integration)
            
            # Загрузка персональности
            if "personality" in config:
                self.personality = BotPersonality(**config["personality"])
            
            # Загрузка кастомных ответов
            self.custom_responses = config.get("custom_responses", {})
            
            # Загрузка sales конфигурации
            self.sales_config = config.get("sales_config", {})
            
            return True
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    def save_to_file(self, config_path: str) -> bool:
        """Сохранение конфигурации в файл"""
        try:
            config = {
                "data_sources": [
                    {
                        "type": ds.type,
                        "config": ds.config,
                        "credentials": ds.credentials,
                        "enabled": ds.enabled,
                        "last_sync": ds.last_sync.isoformat() if ds.last_sync else None
                    }
                    for ds in self.data_sources
                ],
                "api_integrations": [
                    {
                        "name": api.name,
                        "endpoint": api.endpoint,
                        "method": api.method,
                        "headers": api.headers,
                        "auth_type": api.auth_type,
                        "credentials": api.credentials,
                        "rate_limit": api.rate_limit,
                        "timeout": api.timeout
                    }
                    for api in self.api_integrations
                ],
                "personality": {
                    "name": self.personality.name,
                    "greeting_style": self.personality.greeting_style,
                    "communication_tone": self.personality.communication_tone,
                    "language_style": self.personality.language_style,
                    "emoji_usage": self.personality.emoji_usage,
                    "response_length": self.personality.response_length,
                    "specialties": self.personality.specialties
                } if self.personality else None,
                "custom_responses": self.custom_responses,
                "sales_config": self.sales_config
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def add_data_source(self, data_source: DataSource):
        """Добавление источника данных"""
        self.data_sources.append(data_source)
    
    def add_api_integration(self, api_integration: APIIntegration):
        """Добавление API интеграции"""
        self.api_integrations.append(api_integration)
    
    def set_personality(self, personality: BotPersonality):
        """Установка персональности"""
        self.personality = personality
    
    def add_custom_response(self, trigger: str, response: str):
        """Добавление кастомного ответа"""
        self.custom_responses[trigger] = response
    
    def get_data_source_by_type(self, source_type: str) -> List[DataSource]:
        """Получение источников данных по типу"""
        return [ds for ds in self.data_sources if ds.type == source_type and ds.enabled]

class DataConnector:
    """Коннектор данных"""
    
    def __init__(self, config_manager: FlexibleConfigManager):
        self.config_manager = config_manager
        self.session = None
    
    async def initialize(self):
        """Инициализация"""
        if AIOHTTP_AVAILABLE:
            self.session = aiohttp.ClientSession()
        else:
            print("Warning: aiohttp not available, some features will be limited")
    
    async def get_menu_data(self) -> List[Dict[str, Any]]:
        """Получение данных меню"""
        all_menu_data = []
        
        # Google Sheets
        google_sources = self.config_manager.get_data_source_by_type("google_sheets")
        for source in google_sources:
            data = await self.fetch_google_sheets_data(source)
            all_menu_data.extend(data)
        
        # API
        api_sources = self.config_manager.get_data_source_by_type("api")
        for source in api_sources:
            data = await self.fetch_api_data(source)
            all_menu_data.extend(data)
        
        # Файлы
        file_sources = self.config_manager.get_data_source_by_type("file")
        for source in file_sources:
            data = await self.fetch_file_data(source)
            all_menu_data.extend(data)
        
        return all_menu_data
    
    async def fetch_google_sheets_data(self, source: DataSource) -> List[Dict[str, Any]]:
        """Получение данных из Google Sheets"""
        if not GSPREAD_AVAILABLE:
            print("Warning: gspread not available, skipping Google Sheets")
            return []
            
        try:
            # Аутентификация
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                source.credentials, scope
            )
            client = gspread.authorize(creds)
            
            # Открытие таблицы
            spreadsheet = client.open_by_key(source.config["spreadsheet_id"])
            worksheet = spreadsheet.worksheet(source.config.get("worksheet", "Sheet1"))
            
            # Получение данных
            records = worksheet.get_all_records()
            
            # Обработка данных
            processed_data = []
            for record in records:
                processed_data.append({
                    "name": record.get("Название", record.get("Name", "")),
                    "price": record.get("Цена", record.get("Price", "")),
                    "description": record.get("Описание", record.get("Description", "")),
                    "category": record.get("Категория", record.get("Category", "")),
                    "available": record.get("Доступно", record.get("Available", "Да")).lower() == "да"
                })
            
            source.last_sync = datetime.now()
            return processed_data
            
        except Exception as e:
            print(f"Error fetching Google Sheets data: {e}")
            return []
    
    async def fetch_api_data(self, source: DataSource) -> List[Dict[str, Any]]:
        """Получение данных из API"""
        if not AIOHTTP_AVAILABLE or not self.session:
            print("Warning: aiohttp not available, skipping API fetch")
            return []
            
        try:
            url = source.config["url"]
            method = source.config.get("method", "GET")
            headers = source.config.get("headers", {})
            
            # Добавление аутентификации
            if source.auth_type == "api_key":
                api_key = source.credentials.get("api_key")
                header_name = source.credentials.get("header_name", "X-API-Key")
                headers[header_name] = api_key
            elif source.auth_type == "bearer":
                token = source.credentials.get("token")
                headers["Authorization"] = f"Bearer {token}"
            
            async with self.session.request(method, url, headers=headers) as response:
                data = await response.json()
                
                # Обработка данных в зависимости от структуры
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    # Попытка найти массив данных
                    for key in ["data", "items", "results", "menu"]:
                        if key in data and isinstance(data[key], list):
                            return data[key]
                
                return []
                
        except Exception as e:
            print(f"Error fetching API data: {e}")
            return []
    
    async def fetch_file_data(self, source: DataSource) -> List[Dict[str, Any]]:
        """Получение данных из файла"""
        try:
            file_path = source.config["path"]
            
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            
            elif file_path.endswith('.csv'):
                import csv
                data = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        data.append(dict(row))
                return data
            
            elif file_path.endswith('.xlsx'):
                import pandas as pd
                df = pd.read_excel(file_path)
                return df.to_dict('records')
            
            else:
                print(f"Unsupported file format: {file_path}")
                return []
                
        except Exception as e:
            print(f"Error fetching file data: {e}")
            return []
    
    async def get_pricing_data(self) -> List[Dict[str, Any]]:
        """Получение данных о ценах"""
        # Логика аналогична get_menu_data, но для цен
        return await self.get_menu_data()
    
    async def get_customer_data(self) -> List[Dict[str, Any]]:
        """Получение данных о клиентах"""
        customer_data = []
        
        # Поиск источников с данными о клиентах
        for source in self.data_sources:
            if source.config.get("data_type") == "customers":
                if source.type == "google_sheets":
                    data = await self.fetch_google_sheets_data(source)
                elif source.type == "api":
                    data = await self.fetch_api_data(source)
                elif source.type == "file":
                    data = await self.fetch_file_data(source)
                
                customer_data.extend(data)
        
        return customer_data
    
    async def sync_all_sources(self):
        """Синхронизация всех источников данных"""
        tasks = []
        
        for source in self.data_sources:
            if source.enabled:
                if source.type == "google_sheets":
                    tasks.append(self.fetch_google_sheets_data(source))
                elif source.type == "api":
                    tasks.append(self.fetch_api_data(source))
                elif source.type == "file":
                    tasks.append(self.fetch_file_data(source))
        
        await asyncio.gather(*tasks)
    
    async def close(self):
        """Закрытие сессии"""
        if self.session and AIOHTTP_AVAILABLE:
            await self.session.close()

class SalesStrategyManager:
    """Менеджер sales-стратегий"""
    
    def __init__(self):
        self.strategies = {
            "consultative": {
                "name": "Консультативные продажи",
                "approach": "expert_recommendations",
                "techniques": ["needs_analysis", "solution_selling", "value_proposition"],
                "triggers": ["консультация", "рекомендация", "помощь в выборе"],
                "conversion_focus": "trust_building"
            },
            "impulse": {
                "name": "Импульсивные продажи",
                "approach": "urgency_creation",
                "techniques": ["limited_offers", "social_proof", "fear_of_missing_out"],
                "triggers": ["акция", "скидка", "ограниченное предложение"],
                "conversion_focus": "quick_decision"
            },
            "premium": {
                "name": "Премиум-продажи",
                "approach": "exclusivity_emphasis",
                "techniques": ["luxury_positioning", "personalization", "white_glove_service"],
                "triggers": ["премиум", "эксклюзив", "vip"],
                "conversion_focus": "status_appeal"
            },
            "partnership": {
                "name": "Партнерские продажи",
                "approach": "relationship_building",
                "techniques": ["loyalty_programs", "referral_incentives", "cross_selling"],
                "triggers": ["постоянный клиент", "партнер", "программа лояльности"],
                "conversion_focus": "long_term_value"
            }
        }
    
    def get_strategy(self, strategy_name: str) -> Dict[str, Any]:
        """Получение стратегии"""
        return self.strategies.get(strategy_name, self.strategies["consultative"])
    
    def generate_sales_message(self, strategy: str, context: Dict[str, Any]) -> str:
        """Генерация sales-сообщения"""
        strategy_config = self.get_strategy(strategy)
        
        if strategy == "consultative":
            return self._generate_consultative_message(context)
        elif strategy == "impulse":
            return self._generate_impulse_message(context)
        elif strategy == "premium":
            return self._generate_premium_message(context)
        elif strategy == "partnership":
            return self._generate_partnership_message(context)
        
        return "Давайте я помогу вам с выбором!"
    
    def _generate_consultative_message(self, context: Dict[str, Any]) -> str:
        """Генерация консультативного сообщения"""
        return """Я помогу вам сделать лучший выбор! 

Расскажите о ваших предпочтениях, и я подберу идеальный вариант специально для вас.

🎯 Моя экспертиза поможет вам:
• Найти блюда по вкусу
• Оптимизировать бюджет
• Учесть все детали мероприятия

Давайте вместе создадим идеальный опыт!"""
    
    def _generate_impulse_message(self, context: Dict[str, Any]) -> str:
        """Генерация импульсивного сообщения"""
        return """🔥 УСПЕЙТЕ ЗАХВАТИТЬ ПРЕИМУЩЕСТВО!

⚡ Ограниченное предложение действует только сегодня!
💰 Специальные цены - только для вас!
🎉 Бонусы при быстром бронировании!

Не упустите шанс получить максимум выгоды!"""
    
    def _generate_premium_message(self, stratezy: Dict[str, Any]) -> str:
        """Генерация премиум сообщения"""
        return """💎 Добро пожаловать в мир эксклюзивности!

Для вас открыт доступ к:
• Персональному консьерж-сервису
• Эксклюзивным предложениям
• VIP-условиям

Ваш комфорт - наш главный приоритет."""
    
    def _generate_partnership_message(self, context: Dict[str, Any]) -> str:
        """Генерация партнерского сообщения"""
        return """🤝 Ценим наше партнерство!

Для постоянных гостей:
• Специальные условия
• Бонусная программа
• Персональные скидки

Давайте сделаем наше сотрудничество еще выгоднее!"""

class DynamicResponseGenerator:
    """Генератор динамических ответов"""
    
    def __init__(self, config_manager: FlexibleConfigManager, sales_manager: SalesStrategyManager):
        self.config_manager = config_manager
        self.sales_manager = sales_manager
    
    async def generate_response(self, user_input: str, context: Dict[str, Any]) -> str:
        """Генерация ответа на основе входных данных"""
        
        # Анализ намерения пользователя
        intent = self._analyze_intent(user_input)
        
        # Проверка кастомных ответов
        for trigger, response in self.config_manager.custom_responses.items():
            if trigger.lower() in user_input.lower():
                return response
        
        # Генерация ответа на основе намерения
        if intent == "menu_inquiry":
            return await self._generate_menu_response(context)
        elif intent == "pricing_inquiry":
            return await self._generate_pricing_response(context)
        elif intent == "booking_inquiry":
            return await self._generate_booking_response(context)
        elif intent == "sales_opportunity":
            strategy = self.config_manager.sales_config.get("strategy", "consultative")
            return self.sales_manager.generate_sales_message(strategy, context)
        else:
            return await self._generate_general_response(user_input, context)
    
    def _analyze_intent(self, user_input: str) -> str:
        """Анализ намерения пользователя"""
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["меню", "блюдо", "еда", "кухня"]):
            return "menu_inquiry"
        elif any(word in user_input_lower for word in ["цена", "стоимость", "руб", "бюджет"]):
            return "pricing_inquiry"
        elif any(word in user_input_lower for word in ["бронь", "запись", "резерв", "столик"]):
            return "booking_inquiry"
        elif any(word in user_input_lower for word in ["купить", "заказать", "акция", "скидка"]):
            return "sales_opportunity"
        
        return "general_inquiry"
    
    async def _generate_menu_response(self, context: Dict[str, Any]) -> str:
        """Генерация ответа о меню"""
        # Здесь будет логика получения актуального меню
        return """🍽️ Наше меню:

🥗 Салаты и закуски
🍲 Горячие блюда  
🍰 Десерты
🍷 Напитки

Полное меню с ценами и описаниями я могу отправить вам в файле или рассказать о конкретных позициях.

Что вас интересует?"""
    
    async def _generate_pricing_response(self, context: Dict[str, Any]) -> str:
        """Генерация ответа о ценах"""
        return """💰 Наши цены:

• Бизнес-ланч: 300-500 ₽
• Основные блюда: 600-1500 ₽
• Десерты: 200-400 ₽
• Напитки: 150-800 ₽

Средний чек: 800-1200 ₽

Для мероприятий и банкетов действуют специальные условия. Хотите узнать подробнее?"""
    
    async def _generate_booking_response(self, context: Dict[str, Any]) -> str:
        """Генерация ответа о бронировании"""
        return """📅 Бронирование столика:

Рад забронировать для вас столик!

Пожалуйста, сообщите:
• Дату и время
• Количество гостей
• Желаемую зону (терраса/зал)

📞 Также можно позвонить: +7 (XXX) XXX-XX-XX

Какая дата вам подходит?"""
    
    async def _generate_general_response(self, user_input: str, context: Dict[str, Any]) -> str:
        """Генерация общего ответа"""
        personality = self.config_manager.personality
        
        if personality and personality.communication_tone == "friendly":
            return f"""😊 Здравствуйте! Рад помочь вам!

{user_input.capitalize()} - отличный вопрос! 

Чем еще могу быть полезен? Могу рассказать о меню, ценах, забронировать столик или помочь с выбором блюд."""
        
        return f"""Здравствуйте! Спасибо за ваш вопрос.

{user_input.capitalize()} - я могу помочь вам с этим. 

Доступные опции:
• Меню и блюда
• Цены и акции
• Бронирование столиков
• Организация мероприятий

Что вас интересует подробнее?"""
