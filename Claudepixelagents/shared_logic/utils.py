"""
Утилиты для работы с данными и валидации
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import json

class DataValidator:
    """Валидатор входных данных"""
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Валидация номера телефона"""
        # Удаляем все символы кроме цифр
        clean_phone = re.sub(r'[^\d]', '', phone)
        
        # Проверяем длину (10-15 цифр)
        return 10 <= len(clean_phone) <= 15
    
    @staticmethod
    def validate_date(date_str: str) -> tuple[bool, Optional[datetime]]:
        """Валидация даты в формате ДД.ММ.ГГГГ"""
        try:
            date_obj = datetime.strptime(date_str.strip(), "%d.%m.%Y")
            
            # Проверка, что дата не в прошлом
            if date_obj < datetime.now():
                return False, None
            
            return True, date_obj
        except ValueError:
            return False, None
    
    @staticmethod
    def validate_guests_count(guests_str: str) -> tuple[bool, Optional[int]]:
        """Валидация количества гостей"""
        try:
            guests = int(guests_str.strip())
            if guests < 1 or guests > 1000:
                return False, None
            return True, guests
        except ValueError:
            return False, None
    
    @staticmethod
    def validate_budget(budget_str: str) -> bool:
        """Базовая валидация бюджета"""
        # Проверяем, что строка не пустая и содержит цифры
        if not budget_str.strip():
            return False
        
        # Ищем цифры в строке
        return bool(re.search(r'\d', budget_str))

class BookingManager:
    """Менеджер заявок"""
    
    def __init__(self, sheets_client=None):
        self.sheets_client = sheets_client
    
    async def check_availability(self, date: str) -> bool:
        """Проверка доступности даты"""
        if not self.sheets_client:
            return True  # Если нет доступа к таблице, считаем доступной
        
        try:
            # Получение всех записей
            records = self.sheets_client.get_all_records()
            
            # Проверка, есть ли уже запись на эту дату
            for record in records:
                if record.get("Дата") == date:
                    return False
            
            return True
        except Exception as e:
            print(f"Error checking availability: {e}")
            return True
    
    async def save_booking(self, booking_data: Dict[str, Any]) -> bool:
        """Сохранение заявки"""
        if not self.sheets_client:
            return False
        
        try:
            # Формирование строки для таблицы
            row = [
                datetime.now().strftime("%d.%m.%Y %H:%M"),  # Время создания
                booking_data.get("client_name", ""),
                booking_data.get("phone", ""),
                booking_data.get("date", ""),
                booking_data.get("guests_count", ""),
                booking_data.get("budget", ""),
                "Новая",  # Статус
                booking_data.get("event_type", "банкет"),  # Тип мероприятия
                booking_data.get("notes", "")  # Примечания
            ]
            
            # Добавление строки в таблицу
            self.sheets_client.append_row(row)
            return True
        except Exception as e:
            print(f"Error saving booking: {e}")
            return False
    
    async def get_bookings_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Получение заявок по дате"""
        if not self.sheets_client:
            return []
        
        try:
            records = self.sheets_client.get_all_records()
            return [record for record in records if record.get("Дата") == date]
        except Exception as e:
            print(f"Error getting bookings: {e}")
            return []
    
    async def update_booking_status(self, row_index: int, status: str) -> bool:
        """Обновление статуса заявки"""
        if not self.sheets_client:
            return False
        
        try:
            # Находим колонку со статусом (обычно 7-я, индекс 6)
            status_column = 7
            self.sheets_client.update_cell(row_index, status_column, status)
            return True
        except Exception as e:
            print(f"Error updating status: {e}")
            return False

class ConversationState:
    """Управление состоянием диалога"""
    
    def __init__(self):
        self.states: Dict[str, Dict[str, Any]] = {}
    
    def get_state(self, phone: str) -> Dict[str, Any]:
        """Получение состояния пользователя"""
        return self.states.get(phone, {"step": "greeting", "data": {}})
    
    def set_state(self, phone: str, step: str, data: Dict[str, Any] = None):
        """Установка состояния пользователя"""
        self.states[phone] = {
            "step": step,
            "data": data or {},
            "updated_at": datetime.now()
        }
    
    def update_data(self, phone: str, key: str, value: Any):
        """Обновление данных в состоянии"""
        if phone in self.states:
            self.states[phone]["data"][key] = value
            self.states[phone]["updated_at"] = datetime.now()
    
    def reset_state(self, phone: str):
        """Сброс состояния пользователя"""
        self.states[phone] = {"step": "greeting", "data": {}}
    
    def cleanup_old_states(self, hours: int = 24):
        """Очистка старых состояний"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        phones_to_remove = []
        for phone, state in self.states.items():
            if state.get("updated_at", datetime.now()) < cutoff_time:
                phones_to_remove.append(phone)
        
        for phone in phones_to_remove:
            del self.states[phone]
        
        print(f"Cleaned up {len(phones_to_remove)} old conversation states")

class ConfigManager:
    """Менеджер конфигурации"""
    
    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        """Загрузка конфигурации из файла"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print(f"Error parsing config file: {config_path}")
            return {}
    
    @staticmethod
    def save_config(config: Dict[str, Any], config_path: str):
        """Сохранение конфигурации в файл"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    @staticmethod
    def get_env_config() -> Dict[str, Any]:
        """Получение конфигурации из переменных окружения"""
        import os
        
        return {
            "restaurant_name": os.getenv("RESTAURANT_NAME", "Ресторан"),
            "groq_api_key": os.getenv("GROQ_API_KEY"),
            "green_api_instance": os.getenv("GREEN_API_INSTANCE"),
            "green_api_token": os.getenv("GREEN_API_TOKEN"),
            "google_sheets_url": os.getenv("GOOGLE_SHEETS_URL"),
            "google_credentials_path": os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"),
            "trigger_api_key": os.getenv("TRIGGER_API_KEY"),
            "trigger_project_id": os.getenv("TRIGGER_PROJECT_ID")
        }

class Logger:
    """Простой логгер"""
    
    @staticmethod
    def log_message(phone: str, message: str, direction: str = "in"):
        """Логирование сообщения"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {direction.upper()} {phone}: {message}")
    
    @staticmethod
    def log_error(error: str, context: str = ""):
        """Логирование ошибки"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] ERROR {context}: {error}")
    
    @staticmethod
    def log_info(message: str):
        """Логирование информационного сообщения"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] INFO: {message}")

class MessageFormatter:
    """Форматирование сообщений"""
    
    @staticmethod
    def format_phone_number(phone: str) -> str:
        """Форматирование номера телефона"""
        # Удаляем все символы кроме цифр
        clean_phone = re.sub(r'[^\d]', '', phone)
        
        # Если номер начинается с 8, заменяем на +7
        if clean_phone.startswith('8') and len(clean_phone) == 11:
            clean_phone = '7' + clean_phone[1:]
        
        return clean_phone
    
    @staticmethod
    def format_currency(amount: str) -> str:
        """Форматирование суммы"""
        # Удаляем все символы кроме цифр
        clean_amount = re.sub(r'[^\d]', '', amount)
        
        if clean_amount:
            return f"{int(clean_amount):,} ₽".replace(',', ' ')
        return amount
    
    @staticmethod
    def truncate_message(message: str, max_length: int = 4000) -> str:
        """Обрезка сообщения до максимальной длины"""
        if len(message) <= max_length:
            return message
        
        return message[:max_length-3] + "..."
