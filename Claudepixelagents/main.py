"""
AI Bot Architect - Главный файл системы
Запуск генератора ботов для ресторанов
"""

import os
import sys
from pathlib import Path

# Добавляем текущую директорию в Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from generators.bot_generator import BotGenerator

def main():
    """Главная функция запуска системы"""
    print("🤖 AI Bot Architect - Система генерации чат-ботов для ресторанов")
    print("=" * 70)
    print()
    print("🎯 Наша система создает готовых WhatsApp ботов для ресторанов")
    print("📋 Боты умеют:")
    print("   • Записывать клиентов на консультации")
    print("   • Сохранять заявки в Google Sheets")
    print("   • Отправлять напоминания через Trigger.dev")
    print("   • Работать с AI через Groq (Llama 3.3)")
    print()
    print("🚀 Бизнес-модель:")
    print("   1. Вводите название ресторана")
    print("   2. Получаете готового бота")
    print("   3. Разворачиваете на Trigger.dev")
    print("   4. Ресторан получает автоматическую запись клиентов")
    print()
    
    # Проверяем структуру папок
    required_dirs = ["templates", "generators", "shared_logic"]
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not (current_dir / dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ Отсутствуют папки: {', '.join(missing_dirs)}")
        print("Пожалуйста, убедитесь, что все компоненты системы на месте.")
        return
    
    print("✅ Структура системы проверена")
    print()
    
    # Запуск генератора
    try:
        generator = BotGenerator()
        generator.main()
    except KeyboardInterrupt:
        print("\n👋 Работа системы завершена")
    except Exception as e:
        print(f"❌ Ошибка в работе системы: {e}")
        print("Пожалуйста, проверьте конфигурацию и повторите попытку")

if __name__ == "__main__":
    main()
