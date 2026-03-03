"""
Hugging Face Spaces Entry Point
Запуск мульти-платформенного бота для бесплатного хостинга 24/7
"""

import os
import logging
from multi_platform_bot import main

# Настройка логирования для Hugging Face
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == "__main__":
    print("🤗 Hugging Face Spaces - Multi-Platform Bot Architect")
    print("🚀 Запуск бота на бесплатном хостинге 24/7")
    print("📱 Поддерживаемые платформы: Telegram, Instagram, WhatsApp")
    print("💰 Бизнес-модель: $100-500 за настройку ботов")
    print("🔑 Переменные окружения загружены из Hugging Face Secrets")
    
    main()
