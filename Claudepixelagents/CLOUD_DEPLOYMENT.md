# ☁️ Облачное развертывание AI Bot Architect

## 🚀 Развертывание на облачном хостинге

### 📋 План развертывания:
1. **Подготовка облака** (DigitalOcean, AWS, Heroku)
2. **Настройка окружения**
3. **Docker развертывание**
4. **SSL и домен**
5. **Мониторинг**

---

## 🌟 Варианты хостинга

### 1. DigitalOcean (Рекомендуемый)
**Цена:** $6-20/месяц
**Преимущества:** Простой, быстрый, надежный

```bash
# Создание дроплета
# Ubuntu 22.04, 2GB RAM, 1 CPU
# Регион: выберите ближайший к клиентам
```

### 2. Heroku (Free tier)
**Цена:** Бесплатно + $7/месяц для dyno
**Преимущества:** Простой деплой через Git

### 3. AWS EC2
**Цена:** $10-50/месяц
**Преимущества:** Масштабируемость

### 4. Render.com
**Цена:** Бесплатно + $7/месяц
**Преимущества:** Современный, Docker-ready

---

## 🛠️ Пошаговая инструкция (DigitalOcean)

### Шаг 1: Создание сервера

```bash
# 1. Регистрация на DigitalOcean
# 2. Создание Droplet
#    - Ubuntu 22.04 LTS
#    - 2GB RAM, 1 CPU, 25GB SSD
#    - Выберите регион
#    - Добавить SSH ключ
```

### Шаг 2: Подключение к серверу

```bash
ssh root@your_server_ip
```

### Шаг 3: Установка Docker

```bash
# Обновление системы
apt update && apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установка Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Проверка установки
docker --version
docker-compose --version
```

### Шаг 4: Развертывание бота

```bash
# Клонирование репозитория
git clone <your-repo-url>
cd AI-Bot-Architect

# Настройка .env файла
cp .env .env.production
nano .env.production
```

### Шаг 5: Запуск

```bash
# Сборка и запуск
docker-compose -f docker-compose.yml --env-file .env.production up -d

# Проверка статуса
docker-compose ps
docker-compose logs telegram-bot-architect
```

---

## 🔧 Конфигурация .env

```bash
# Обязательно заполните:
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GREEN_API_INSTANCE=123456
GREEN_API_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Опционально:
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/...
TRIGGER_API_KEY=trigger_xxxxxxxxxxxxxx
TRIGGER_PROJECT_ID=proj_xxxxxxxxxxxxxx
```

---

## 🌐 Настройка домена и SSL

### Шаг 1: Настройка DNS

```bash
# В панели домена добавьте A запись:
# A @ your_server_ip
# A www your_server_ip
```

### Шаг 2: Установка Nginx + SSL

```bash
# Установка Nginx
apt install nginx -y

# Установка Certbot
apt install certbot python3-certbot-nginx -y

# Получение SSL сертификата
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Шаг 3: Конфигурация Nginx

```nginx
# /etc/nginx/sites-available/ai-bot-architect
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📊 Мониторинг и логирование

### Просмотр логов

```bash
# Логи контейнера
docker-compose logs -f telegram-bot-architect

# Системные логи
journalctl -u docker.service -f
```

### Health Check

```bash
# Проверка работы бота
curl http://localhost:8000/health

# Статус контейнера
docker-compose ps
```

### Автоматический перезапуск

```yaml
# docker-compose.yml (уже настроено)
restart: unless-stopped
```

---

## 🔒 Безопасность

### Базовая безопасность

```bash
# Создание пользователя
adduser botuser
usermod -aG sudo botuser

# Настройка файрвола
ufw allow ssh
ufw allow 80
ufw allow 443
ufw enable

# Отключение root доступа
nano /etc/ssh/sshd_config
# PermitRootLogin no
# PasswordAuthentication no

systemctl restart ssh
```

### Резервное копирование

```bash
# Скрипт бэкапа
#!/bin/bash
# /home/botuser/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/botuser/backups"

# Создание бэкапа
docker-compose exec telegram-bot-architect tar -czf /tmp/bot_backup_$DATE.tar.gz /app/generated_bots

# Копирование в бэкап директорию
mkdir -p $BACKUP_DIR
cp /tmp/bot_backup_$DATE.tar.gz $BACKUP_DIR/

# Удаление старых бэкапов (старше 7 дней)
find $BACKUP_DIR -name "bot_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

---

## 🚀 Heroku развертывание

### Шаг 1: Подготовка

```bash
# Установка Heroku CLI
npm install -g heroku

# Логин
heroku login
```

### Шаг 2: Создание приложения

```bash
# Создание приложения
heroku create your-ai-bot-architect

# Добавление buildpacks
heroku buildpacks:set heroku/python

# Настройка переменных
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set GROQ_API_KEY=your_groq_key
heroku config:set GREEN_API_INSTANCE=your_instance
heroku config:set GREEN_API_TOKEN=your_green_token
```

### Шаг 3: Деплой

```bash
# Добавление Heroku remote
git remote add heroku https://git.heroku.com/your-ai-bot-architect.git

# Деплой
git push heroku main

# Проверка
heroku logs --tail
```

---

## 📱 Render.com развертывание

### Шаг 1: Подготовка репозитория

```bash
# Создание render.yaml
version: "1"
services:
  ai-bot-architect:
    type: web
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        value: "your_token"
      - key: GROQ_API_KEY
        value: "your_groq_key"
      - key: GREEN_API_INSTANCE
        value: "your_instance"
      - key: GREEN_API_TOKEN
        value: "your_green_token"
```

### Шаг 2: Деплой

1. Подключите GitHub репозиторий к Render
2. Выберите "New Web Service"
3. Настройте переменные окружения
4. Deploy!

---

## 🔧 Troubleshooting

### Проблема: Бот не запускается

```bash
# Проверка логов
docker-compose logs telegram-bot-architect

# Проверка переменных окружения
docker-compose exec telegram-bot-architect env | grep TELEGRAM
```

### Проблема: Нет доступа к API

```bash
# Проверка сети
docker-compose exec telegram-bot-architect ping api.telegram.org

# Проверка токена
curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe
```

### Проблема: Память

```bash
# Проверка использования памяти
docker stats

# Очистка
docker system prune -a
```

---

## 📈 Масштабирование

### Нагрузочный тест

```bash
# Тест нагрузки
ab -n 1000 -c 10 https://yourdomain.com/health
```

### Горизонтальное масштабирование

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  telegram-bot-architect:
    scale: 3
    # ... остальная конфигурация
```

---

## 💰 Стоимость обслуживания

### DigitalOcean (рекомендуемый)
- **Сервер:** $6/месяц
- **Домен:** $12/год
- **SSL:** Бесплатно
- **Итого:** ~$84/год

### Heroku
- **Dyno:** $7/месяц
- **Итого:** ~$84/год

### Render.com
- **Бесплатный tier** + $7/месяц при нагрузке
- **Итого:** ~$84/год

---

## 🎯 Рекомендации

1. **Начните с DigitalOcean** - лучший баланс цены/качества
2. **Настройте мониторинг** - следите за работой
3. **Сделайте бэкапы** - защищайте данные
4. **Оптимизируйте** - следите за ресурсами
5. **Масштабируйте** - при росте нагрузки

---

## 📞 Поддержка

При проблемах с развертыванием:
1. Проверьте логи контейнера
2. Убедитесь в правильности .env
3. Проверьте доступность API
4. Напишите в поддержку хостинга

---

**🚀 Готово! Ваш AI Bot Architect работает в облаке!**

*Создан для автоматизации ресторанного бизнеса*
