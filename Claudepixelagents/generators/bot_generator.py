"""
AI Bot Architect - Генератор чат-ботов для ресторанов
Создает кастомизированного бота на основе шаблона
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

class BotGenerator:
    """Генератор чат-ботов для ресторанов"""
    
    def __init__(self):
        self.templates_dir = Path("templates")
        self.output_dir = Path("generated_bots")
        
    def generate_bot(self, restaurant_name: str, config: Dict[str, Any]) -> str:
        """
        Генерирует бота для указанного ресторана
        
        Args:
            restaurant_name: Название ресторана
            config: Конфигурация с API ключами и настройками
            
        Returns:
            Путь к сгенерированному боту
        """
        # Создание директории для бота
        bot_name = self._sanitize_name(restaurant_name)
        bot_dir = self.output_dir / bot_name
        bot_dir.mkdir(parents=True, exist_ok=True)
        
        # Копирование шаблона
        self._copy_template(bot_dir)
        
        # Кастомизация файлов
        self._customize_bot(bot_dir, restaurant_name, config)
        
        # Создание deployment инструкций
        self._create_deployment_guide(bot_dir, restaurant_name)
        
        print(f"✅ Бот для '{restaurant_name}' успешно сгенерирован!")
        print(f"📁 Путь: {bot_dir.absolute()}")
        print(f"🚀 Следующие шаги смотрите в {bot_dir}/DEPLOYMENT.md")
        
        return str(bot_dir.absolute())
    
    def _sanitize_name(self, name: str) -> str:
        """Очистка названия для использования в имени папки"""
        return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    
    def _copy_template(self, bot_dir: Path):
        """Копирование файлов шаблона"""
        template_files = [
            "restaurant_bot_template.py",
            "requirements.txt",
            ".env.example"
        ]
        
        for file in template_files:
            src = self.templates_dir / file
            dst = bot_dir / file
            
            if src.exists():
                shutil.copy2(src, dst)
                print(f"📋 Скопирован: {file}")
    
    def _customize_bot(self, bot_dir: Path, restaurant_name: str, config: Dict[str, Any]):
        """Кастомизация файлов бота"""
        
        # Кастомизация основного файла бота
        bot_file = bot_dir / "restaurant_bot_template.py"
        if bot_file.exists():
            content = bot_file.read_text(encoding='utf-8')
            
            # Замена названия ресторана в умолчаниях
            content = content.replace(
                '"Ресторан"',
                f'"{restaurant_name}"'
            )
            
            # Добавление кастомного заголовка
            custom_header = f'''"""
{restaurant_name} - Чат-бот для записи на консультации
Сгенерировано AI Bot Architect: {datetime.now().strftime("%d.%m.%Y %H:%M")}
"""
'''
            
            content = custom_header + content
            
            bot_file.write_text(content, encoding='utf-8')
        
        # Создание .env файла с настройками
        env_file = bot_dir / ".env"
        env_content = f"""# {restaurant_name} - Конфигурация бота
# Сгенерировано AI Bot Architect

# Название ресторана
RESTAURANT_NAME={restaurant_name}

# Groq API
GROQ_API_KEY={config.get('groq_api_key', 'your_groq_api_key_here')}

# Green-API (WhatsApp)
GREEN_API_INSTANCE={config.get('green_api_instance', 'your_green_api_instance')}
GREEN_API_TOKEN={config.get('green_api_token', 'your_green_api_token')}

# Google Sheets
GOOGLE_SHEETS_URL={config.get('google_sheets_url', 'your_google_sheets_url')}
GOOGLE_CREDENTIALS_PATH=credentials.json

# Trigger.dev
TRIGGER_API_KEY={config.get('trigger_api_key', 'your_trigger_api_key')}
TRIGGER_PROJECT_ID={config.get('trigger_project_id', 'your_trigger_project_id')}
"""
        
        env_file.write_text(env_content, encoding='utf-8')
        
        # Переименование основного файла
        new_bot_file = bot_dir / f"{self._sanitize_name(restaurant_name).lower().replace(' ', '_')}_bot.py"
        bot_file.rename(new_bot_file)
        
        print(f"🔧 Файлы кастомизированы для '{restaurant_name}'")
    
    def _create_deployment_guide(self, bot_dir: Path, restaurant_name: str):
        """Создание инструкции по развертыванию"""
        deployment_content = f'''# Развертывание бота для {restaurant_name}

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка окружения
1. Скопируйте `.env.example` в `.env`:
```bash
cp .env.example .env
```

2. Заполните API ключи в файле `.env`:
- `GROQ_API_KEY`: Получите на https://groq.com/
- `GREEN_API_INSTANCE` и `GREEN_API_TOKEN`: Зарегистрируйтесь на https://green-api.com/
- `GOOGLE_SHEETS_URL`: Создайте Google Sheet и получите URL
- `TRIGGER_API_KEY`: Зарегистрируйтесь на https://trigger.dev/

### 3. Настройка Google Sheets
1. Создайте новую Google Таблицу с колонками:
   - Время создания
   - Имя клиента
   - Телефон
   - Дата консультации
   - Количество гостей
   - Бюджет
   - Статус

2. Получите JSON файл с ключами сервисного аккаунта Google Cloud
3. Переименуйте его в `credentials.json` и положите в папку с ботом

### 4. Запуск бота
```bash
python {self._sanitize_name(restaurant_name).lower().replace(' ', '_')}_bot.py
```

### 5. Настройка вебхука
После запуска бот будет доступен на `http://localhost:8000`

Настройте вебхук в Green-API:
- URL: `http://your-domain.com/webhook/whatsapp`
- Метод: POST

## 🐳 Docker развертывание

Создайте `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "{self._sanitize_name(restaurant_name).lower().replace(' ', '_')}_bot.py"]
```

Запуск:
```bash
docker build -t {self._sanitize_name(restaurant_name).lower().replace(' ', '_')}-bot .
docker run -p 8000:8000 {self._sanitize_name(restaurant_name).lower().replace(' ', '_')}-bot
```

## ☁️ Развертывание на Trigger.dev

1. Установите Trigger.dev CLI:
```bash
npm install -g @trigger.dev/cli
```

2. Инициализация проекта:
```bash
trigger init
```

3. Развертывание:
```bash
trigger deploy
```

## 📊 Мониторинг

- Health check: `GET /health`
- Логи бота доступны в консоли
- Данные клиентов сохраняются в Google Sheets

## 🔧 Troubleshooting

### Проблемы с WhatsApp
- Убедитесь, что Green-API аккаунт активен
- Проверьте баланс и лимиты
- Вебхук должен быть доступен извне

### Проблемы с Google Sheets
- Проверьте права доступа к таблице
- Убедитесь, что файл `credentials.json` корректен
- API Google Sheets должен быть включен

### Проблемы с Groq
- Проверьте валидность API ключа
- Убедитесь, что у вас есть доступ к моделям Llama

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи бота
2. Убедитесь, что все API ключи корректны
3. Проверьте подключение к интернету

---
Сгенерировано AI Bot Architect {datetime.now().strftime("%d.%m.%Y %H:%M")}
'''
        
        deployment_file = bot_dir / "DEPLOYMENT.md"
        deployment_file.write_text(deployment_content, encoding='utf-8')
        
        print(f"📖 Инструкция по развертыванию создана")

def main():
    """Интерактивный режим генератора"""
    print("🤖 AI Bot Architect - Генератор чат-ботов для ресторанов")
    print("=" * 60)
    
    generator = BotGenerator()
    
    # Ввод названия ресторана
    restaurant_name = input("\n🍽️ Введите название ресторана: ").strip()
    if not restaurant_name:
        print("❌ Название ресторана не может быть пустым!")
        return
    
    # Ввод API ключей
    print("\n🔑 Введите API ключи (нажмите Enter для использования значений по умолчанию):")
    
    config = {}
    
    config['groq_api_key'] = input("Groq API Key: ").strip() or "your_groq_api_key_here"
    config['green_api_instance'] = input("Green-API Instance: ").strip() or "your_green_api_instance"
    config['green_api_token'] = input("Green-API Token: ").strip() or "your_green_api_token"
    config['google_sheets_url'] = input("Google Sheets URL: ").strip() or "your_google_sheets_url"
    config['trigger_api_key'] = input("Trigger.dev API Key: ").strip() or "your_trigger_api_key"
    config['trigger_project_id'] = input("Trigger.dev Project ID: ").strip() or "your_trigger_project_id"
    
    # Генерация бота
    print("\n🔨 Генерация бота...")
    bot_path = generator.generate_bot(restaurant_name, config)
    
    print(f"\n🎉 Готово! Ваш бот находится в папке:")
    print(f"📁 {bot_path}")
    print(f"\n📋 Следующие шаги:")
    print(f"1. Откройте папку с ботом")
    print(f"2. Прочитайте файл DEPLOYMENT.md")
    print(f"3. Настройте API ключи в .env файле")
    print(f"4. Запустите бота и настройте вебхук")

if __name__ == "__main__":
    main()
