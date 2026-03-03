"""
AI Bot Architect - Quick Start Script
Быстрый запуск Telegram бота для создания ресторанных ботов
"""

import os
import subprocess
import sys
from pathlib import Path

def check_requirements():
    """Проверка требований"""
    print("🔍 Проверка требований...")
    
    # Проверка Python
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        return False
    
    # Проверка Docker
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker найден")
    except:
        print("❌ Docker не найден. Установите Docker: https://docs.docker.com/get-docker/")
        return False
    
    # Проверка Docker Compose
    try:
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        print("✅ Docker Compose найден")
    except:
        print("❌ Docker Compose не найден")
        return False
    
    return True

def setup_environment():
    """Настройка окружения"""
    print("\n⚙️ Настройка окружения...")
    
    # Проверка .env файла
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Файл .env не найден")
        print("📝 Создайте .env файл на основе .env.example")
        return False
    
    # Проверка обязательных переменных
    required_vars = ["TELEGRAM_BOT_TOKEN"]
    missing_vars = []
    
    with open(env_file, 'r') as f:
        env_content = f.read()
        
    for var in required_vars:
        if f"{var}=your_" in env_content or f"{var}=" not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Заполните переменные в .env: {', '.join(missing_vars)}")
        print("💡 Получите токен у @BotFather в Telegram")
        return False
    
    print("✅ Окружение настроено")
    return True

def build_and_run():
    """Сборка и запуск"""
    print("\n🔨 Сборка и запуск бота...")
    
    try:
        # Сборка образа
        print("📦 Сборка Docker образа...")
        subprocess.run(["docker-compose", "build"], check=True)
        
        # Запуск
        print("🚀 Запуск контейнера...")
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        
        print("✅ Бот запущен!")
        
        # Показ логов
        print("\n📋 Логи бота:")
        subprocess.run(["docker-compose", "logs", "-f", "telegram-bot-architect"])
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

def show_status():
    """Показать статус"""
    print("\n📊 Статус бота:")
    
    try:
        # Проверка статуса контейнера
        result = subprocess.run(
            ["docker-compose", "ps"], 
            capture_output=True, 
            text=True
        )
        print(result.stdout)
        
        # Health check
        print("\n🔍 Проверка здоровья:")
        result = subprocess.run(
            ["curl", "-f", "http://localhost:8000/health"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Бот отвечает на запросы")
        else:
            print("❌ Бот не отвечает")
            
    except Exception as e:
        print(f"❌ Ошибка проверки статуса: {e}")

def stop_bot():
    """Остановка бота"""
    print("\n🛑 Остановка бота...")
    
    try:
        subprocess.run(["docker-compose", "down"], check=True)
        print("✅ Бот остановлен")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка остановки: {e}")

def main():
    """Главная функция"""
    print("🤖 AI Bot Architect - Quick Start")
    print("=" * 50)
    
    while True:
        print("\n📋 Меню:")
        print("1. 🚀 Запустить бота")
        print("2. 📊 Показать статус")
        print("3. 🛑 Остановить бота")
        print("4. 📋 Показать логи")
        print("5. 🚪 Выход")
        
        choice = input("\nВыберите опцию (1-5): ").strip()
        
        if choice == "1":
            if check_requirements() and setup_environment():
                build_and_run()
        elif choice == "2":
            show_status()
        elif choice == "3":
            stop_bot()
        elif choice == "4":
            print("\n📋 Логи бота:")
            subprocess.run(["docker-compose", "logs", "-f", "telegram-bot-architect"])
        elif choice == "5":
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверная опция")

if __name__ == "__main__":
    main()
