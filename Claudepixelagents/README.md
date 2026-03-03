# 🤖 AI Bot Architect

**Система для генерации чат-ботов ресторанов с записью на консультации**

AI Bot Architect - это мета-агент на Python, который автоматически создает готовых чат-ботов для ресторанов. Боты умеют записывать клиентов на консультации по банкетам и мероприятиям, интегрироваться с Google Sheets и отправлять напоминания через Trigger.dev.

## 🚀 Возможности

### Для ресторанов:
- 📝 **Запись на консультации** - Сбор данных: дата, количество гостей, бюджет, телефон
- 📊 **Google Sheets интеграция** - Автоматическое сохранение заявок в таблицу
- ⏰ **Умные напоминания** - Trigger.dev для напоминаний за 2 часа до консультации
- 💬 **WhatsApp интеграция** - Работа через Green-API
- 🤖 **AI ассистент** - Groq (Llama 3.3) для интеллектуальных ответов

### Для разработчиков:
- 🔧 **Генератор ботов** - Создание кастомных ботов под любой ресторан
- 📁 **Модульная архитектура** - Переиспользуемые компоненты
- 🐳 **Docker готовность** - Легкий деплой
- 📖 **Полная документация** - Подробные инструкции

## 📋 Стек технологий

- **Backend**: FastAPI
- **AI**: Groq (Llama 3.3)
- **WhatsApp**: Green-API
- **База данных**: Google Sheets API
- **Фоновые задачи**: Trigger.dev
- **Язык**: Python 3.11+

## 🏗️ Структура проекта

```
AI Bot Architect/
├── templates/                 # Шаблоны ботов
│   ├── restaurant_bot_template.py
│   ├── requirements.txt
│   └── .env.example
├── generators/               # Генераторы
│   └── bot_generator.py
├── shared_logic/            # Общая логика
│   ├── api_clients.py
│   ├── utils.py
│   └── whatsapp_integration.py
└── README.md                # Этот файл
```

## 🚀 Быстрый старт

### 1. Клонирование и установка

```bash
git clone <repository-url>
cd AI-Bot-Architect
pip install -r requirements.txt
```

### 2. Генерация бота для вашего ресторана

Запустите генератор:

```bash
python generators/bot_generator.py
```

Следуйте инструкциям:
- Введите название ресторана
- Добавьте API ключи
- Получите готового бота в папке `generated_bots/`

### 3. Настройка API ключей

Получите необходимые API ключи:

#### Groq API
1. Зарегистрируйтесь на [groq.com](https://groq.com/)
2. Получите API ключ в дашборде
3. Добавьте в `.env` файл

#### Green-API (WhatsApp)
1. Зарегистрируйтесь на [green-api.com](https://green-api.com/)
2. Создайте инстанс WhatsApp
3. Получите `instance_id` и `token`

#### Google Sheets
1. Создайте Google Таблицу
2. Настройте Google Cloud Service Account
3. Получите URL таблицы и credentials.json

#### Trigger.dev
1. Зарегистрируйтесь на [trigger.dev](https://trigger.dev/)
2. Создайте проект
3. Получите API ключ и ID проекта

### 4. Запуск бота

```bash
cd generated_bots/ваш-ресторан
pip install -r requirements.txt
python ваш_бот.py
```

## 📱 Пример работы бота

### Диалог с клиентом:

```
🍽️ Добро пожаловать в Ресторан Зенит!

Я помогу вам записаться на консультацию по организации банкета или мероприятия.

Для начала, представьтесь, пожалуйста:
📝 Как вас зовут?

> Иван

Приятно познакомиться, Иван! 🎉

Теперь выберите желаемую дату консультации:
📅 Введите дату в формате ДД.ММ.ГГГГ

> 15.03.2026

Отлично! 📝 Сколько гостей планируется на мероприятии?

> 25

Хорошо! 💰 Какой бюджет вы планируете на мероприятие?

> 150000

🎯 Проверьте ваши данные:
👤 Имя: Иван
📅 Дата: 15.03.2026
👥 Гостей: 25
💰 Бюджет: 150000

Все верно? Ответьте "Да" для подтверждения или "Нет" для изменений.

> Да

✅ Заявка успешно оформлена!
🎉 Мы ждем вас на консультацию 15.03.2026
📍 Наш менеджер свяжется с вами для подтверждения

Спасибо за обращение в Ресторан Зенит! 🍽️
```

## 🐳 Docker развертывание

Создайте `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "restaurant_bot.py"]
```

Запуск:

```bash
docker build -t restaurant-bot .
docker run -p 8000:8000 restaurant-bot
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

## 🔧 Конфигурация

### Переменные окружения (.env)

```bash
# Название ресторана
RESTAURANT_NAME=Ресторан Зенит

# Groq API
GROQ_API_KEY=your_groq_api_key

# Green-API (WhatsApp)
GREEN_API_INSTANCE=your_instance_id
GREEN_API_TOKEN=your_token

# Google Sheets
GOOGLE_SHEETS_URL=your_sheet_url
GOOGLE_CREDENTIALS_PATH=credentials.json

# Trigger.dev
TRIGGER_API_KEY=your_trigger_api_key
TRIGGER_PROJECT_ID=your_project_id
```

### Настройка Google Sheets

Создайте таблицу со следующими колонками:
1. Время создания
2. Имя клиента
3. Телефон
4. Дата консультации
5. Количество гостей
6. Бюджет
7. Статус
8. Тип мероприятия
9. Примечания

## 📊 Мониторинг и аналитика

### Health check
```bash
curl http://localhost:8000/health
```

### Логи
Бот логирует все действия в консоль:
- Входящие сообщения
- Ответы бота
- Ошибки API
- Сохранение заявок

### Метрики
- Количество обработанных диалогов
- Конверсия в заявки
- Время ответа
- Ошибки интеграций

## 🛠️ Кастомизация

### Изменение диалога

Редактируйте шаблоны сообщений в `shared_logic/api_clients.py`:

```python
class MessageTemplates:
    @staticmethod
    def greeting(restaurant_name: str) -> str:
        return f"Ваше приветствие для {restaurant_name}"
```

### Добавление новых шагов диалога

В файле бота добавьте новые методы:

```python
async def handle_collect_event_type(self, phone: str, message: str) -> str:
    # Обработка типа мероприятия
    pass
```

### Интеграция с другими сервисами

Добавьте новых клиентов в `shared_logic/api_clients.py`:

```python
class CustomAPIClient:
    async def send_data(self, data):
        # Ваша логика
        pass
```

## 🔒 Безопасность

### Рекомендации:
1. **Храните API ключи** в переменных окружения
2. **Используйте HTTPS** для вебхуков
3. **Валидируйте входящие данные**
4. **Ограничьте доступ** к API эндпоинтам
5. **Логируйте подозрительные активности**

### Безопасность данных:
- Все данные шифруются при передаче
- Телефоны хранятся в формате хеша
- История диалогов не сохраняется

## 🐞 Troubleshooting

### Проблемы с WhatsApp
- **Ошибка**: Webhook не принимается
- **Решение**: Проверьте доступность URL и Green-API настройки

### Проблемы с Google Sheets
- **Ошибка**: Permission denied
- **Решение**: Проверьте права доступа Service Account

### Проблемы с Groq
- **Ошибка**: Rate limit exceeded
- **Решение**: Добавьте задержки между запросами

## 📞 Поддержка

При возникновении проблем:

1. **Проверьте логи** бота
2. **Проверьте API ключи** в `.env`
3. **Проверьте подключение** к интернету
4. **Посмотрите документацию** API провайдеров

### Полезные ссылки:
- [Groq Documentation](https://groq.com/docs)
- [Green-API Documentation](https://green-api.com/docs)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Trigger.dev Documentation](https://trigger.dev/docs)

## 🤝 Бизнес-модель

### Как это работает:

1. **Входные данные**: Вы вводите название ресторана
2. **Генерация**: AI Bot Architect создает готового бота
3. **Деплой**: Вы разворачиваете бота на Trigger.dev
4. **Результат**: У ресторана работает бот в WhatsApp

### Преимущества для ресторанов:
- ✅ Автоматическая запись на консультации
- ✅ Сбор данных о клиентах
- ✅ Увеличение конверсии
- ✅ Экономия времени менеджеров
- ✅ Работа 24/7

## 📄 Лицензия

MIT License - свободное использование и модификация

## 🙏 Благодарности

- Groq за мощный AI API
- Green-API за WhatsApp интеграцию
- Trigger.dev для фоновых задач
- FastAPI за быстрый backend

---

**Создано с ❤️ для автоматизации ресторанного бизнеса**

*Сгенерировано AI Bot Architect - вашим помощником в создании чат-ботов*
