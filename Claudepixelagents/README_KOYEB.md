# 🚀 Koyeb Deployment Guide

## 🆓 Бесплатный 24/7 хостинг на Koyeb

### 📋 **Что нужно:**
1. Koyeb аккаунт (бесплатный)
2. GitHub репозиторий
3. Твой код бота

### 🚀 **Шаги развертывания:**

#### 1. **Создай репозиторий на GitHub**
```bash
git init
git add .
git commit -m "Multi-Platform Bot for Koyeb"
git branch -M main
git remote add origin https://github.com/username/multi-platform-bot.git
git push -u origin main
```

#### 2. **Создай приложение на Koyeb**
1. Зайди в [koyeb.com](https://koyeb.com)
2. Нажми "Create App"
3. Выбери "Docker"
4. Подключи GitHub репозиторий
5. Загрузи `koyeb.yaml` конфигурацию

#### 3. **Настрой переменные окружения**
В Koyeb App → Settings → Environment Variables:
```
PORT=8080
TELEGRAM_BOT_TOKEN=твой_токен
GROQ_API_KEY=твой_groq_ключ
```

#### 4. **Запуск приложения**
1. Нажми "Deploy"
2. Koyeb соберет Docker образ
3. Приложение запустится автоматически

### ✅ **Преимущества Koyeb:**
- 🆓 **Полностью бесплатно** (nano instance)
- 🔄 **Автоматический перезапуск**
- 📊 **Мониторинг и логи**
- 🌍 **Глобальный CDN**
- 🔧 **GitHub интеграция**
- 📱 **Работает 24/7**

### 🎯 **Конфигурация:**

#### **koyeb.yaml:**
```yaml
name: multi-platform-bot
app:
  name: multi-platform-bot
  type: docker
  dockerfile: Dockerfile
  port: 8080
  health_check:
    path: /health
    interval: 30s
```

#### **Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "koyeb_deploy.py"]
```

### 🔍 **Проверка развертывания:**

#### **Логи в Koyeb:**
```
🚀 Запуск на Koyeb...
🌐 Порт: 8080
✅ Бот запущен на Koyeb!
* Running on http://0.0.0.0:8080
```

#### **Health Check:**
- Открой `https://твой-app.koyeb.app/health`
- Должен показать: `{"status": "healthy", "bot_running": true}`

### 💰 **Бизнес-модель на Koyeb:**

```
📱 Создаешь ботов для ресторанов:
• Telegram Bot - $100-200
• Instagram Bot - $150-300
• Multi-Platform - $300-500

🔄 Твои расходы на Koyeb:
• Хостинг - $0 (бесплатный план)
• API ключи - платит клиент
• Твоё время - создаешь ботов

💸 Прибыль:
• 1 бот в день = $100-500
• 10 ботов в месяц = $1000-5000
• Полностью пассивный доход
```

### 🎮 **Тестирование:**

1. **Разверни на Koyeb**
2. **Проверь /health эндпоинт**
3. **Протестируй бота в Telegram**
4. **Создай первого клиента**

### 🛠️ **Отладка:**

#### **Если бот не запускается:**
1. Проверь логи в Koyeb
2. Убедись что переменные окружения настроены
3. Проверь Health Check статус

#### **Перезапуск:**
1. В Koyeb App → Actions
2. Нажми "Redeploy"
3. Приложение перезапустится

### 🎯 **Результат:**
- **Твой бот работает 24/7 бесплатно на Koyeb**
- **Создаешь ботов для клиентов**
- **Клиенты платят за настройку**
- **Твои расходы = $0**

**Готово! Твой бот будет работать бесплатно всегда на Koyeb!** 🚀
