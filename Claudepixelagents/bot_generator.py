import os
import asyncio
import shutil
from pathlib import Path
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# МЫ ИСПОЛЬЗУЕМ ТВОЙ ЦЕЛЫЙ КЛАСС БЕЗ СОКРАЩЕНИЙ
from bot_generator import BotGenerator

# === ТВОЙ ТОКЕН ===
TG_TOKEN = "ВСТАВЬ_СЮДА_ТОКЕН_ОТ_BOTFATHER"
# =================

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
generator = BotGenerator()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "🤖 **Мастер-Бот на связи!**\n\n"
        "Я использую твой движок `BotGenerator` на полную катушку.\n"
        "Напиши название ресторана — я создам папку, кастомизирую файлы и пришлю тебе ZIP."
    )

@dp.message()
async def handle_message(message: types.Message):
    restaurant_name = message.text.strip()
    
    await message.answer(f"🚀 Запускаю полный цикл генерации для: **{restaurant_name}**")

    # Конфиг, который твой BotGenerator ожидает на вход
    config = {
        'groq_api_key': "your_key",
        'green_api_instance': "your_instance",
        'green_api_token': "your_token",
        'google_sheets_url': "your_url",
        'trigger_api_key': "your_key",
        'trigger_project_id': "your_id"
    }

    try:
        # 1. ВЫЗЫВАЕМ ТВОЙ МЕТОД СО ВСЕМИ ЕГО ПРОВЕРКАМИ
        # Он создаст папки, скопирует шаблоны и создаст DEPLOYMENT.md
        full_path_str = generator.generate_bot(restaurant_name, config)
        bot_path = Path(full_path_str)
        
        # 2. АРХИВАЦИЯ (чтобы отправить тебе через ТГ)
        archive_name = f"bot_{bot_path.name}"
        # Делаем зип из той папки, которую создал твой генератор
        shutil.make_archive(archive_name, 'zip', bot_path)
        zip_file = f"{archive_name}.zip"

        # 3. ОТПРАВКА
        document = types.FSInputFile(zip_file)
        await message.answer_document(
            document, 
            caption=f"✅ Готово!\n\n📂 Путь на сервере: `{full_path_str}`\n"
                    f"📦 Лови архив с готовым ботом!"
        )

        # Чистим временный архив (папки в generated_bots останутся)
        if os.path.exists(zip_file):
            os.remove(zip_file)

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

async def main():
    print("🤖 Мастер-бот запущен. Жду названий ресторанов...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())