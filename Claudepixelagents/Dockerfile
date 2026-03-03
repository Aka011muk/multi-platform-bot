# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Flask для вебхука
RUN pip install Flask==2.3.3

# Копируем весь проект (код, генераторы, шаблоны)
COPY . .

# Создаем папку для генерации ботов и даем права доступа
RUN mkdir -p generated_bots && chmod 777 generated_bots

# Открываем порт для Render
EXPOSE 10000

# Запускаем вебхук бота для Render
CMD ["python", "render_webhook.py"]
