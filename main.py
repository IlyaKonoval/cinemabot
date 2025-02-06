import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
import api_file
from database import DataBaseHandler
from keyboard.main_keyboard import main_keyboard
from keyboard.deck_keyboard import deck_keyboard

BOT_TOKEN = api_file.BOT_TOKEN
KINOPOISK_API_KEY = api_file.KINOPOISK_API_KEY
GOOGLE_CX_KEY = api_file.GOOGLE_CX_KEY
GOOGLE_API_KEY = api_file.GOOGLE_API_KEY

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
DATABASE = DataBaseHandler(api_file.DATABASE_NAME)


def correct_film_title(title: str) -> str:
    corrections = {
        "как витька чеснок вез леху штыря в дом инвалидов": "Как Витька Чеснок вёз Лёху Штыря в дом инвалидов"
    }
    return corrections.get(title.lower().strip(), title)


@dp.message(CommandStart())
async def send_welcome(message: Message):
    await message.reply(
        "Привет! Я бот для поиска фильмов. Выбери нужную функцию:",
        reply_markup=main_keyboard()
    )


@dp.message(Command(commands=["help"]))
async def bot_help(message: Message):
    await message.reply('''
Отправьте название фильма или сериала для поиска.
/start - Перезапуск бота
/help - Помощь
/stats - Показать статистику поиска
/history - Показать историю поиска
''')


@dp.message(Command(commands=["stats"]))
async def user_stat(message: Message):
    stats = await DATABASE.user_stats(message.from_user.username)
    if stats:
        pairs = '\n'.join(f'{title}: {count}' for title, count in stats)
        await message.reply(pairs)
    else:
        await message.reply('No stats yet, make some requests please.')


@dp.message(Command(commands=["history"]))
async def user_search_history(message: Message):
    history_list = await DATABASE.user_search_history(message.from_user.username)
    if history_list:
        history_str = '\n'.join(title[0] for title in history_list)
        await message.reply(history_str)
    else:
        await message.reply('No history yet.')


async def get_film_info(title: str, session: aiohttp.ClientSession):
    corrected_title = correct_film_title(title)
    search_field = "alternativeName" if corrected_title.isascii() else "name"
    url = f'https://api.kinopoisk.dev/v1.3/movie?{search_field}={corrected_title}&limit=5'
    headers = {"X-API-KEY": KINOPOISK_API_KEY}
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            result = await response.json()
            if result.get("docs"):
                film = result["docs"][0]
                return {
                    "title": film.get("name"),
                    "rating": film.get("rating", {}).get("kp", "N/A"),
                    "poster": film.get("poster", {}).get("url", "N/A")
                }
        logging.error(f"Фильм не найден: {title}")
        return None


async def get_watch_links(title: str, session: aiohttp.ClientSession):
    params = {
        'q': f'{title} смотреть онлайн',
        'cx': GOOGLE_CX_KEY,
        'key': GOOGLE_API_KEY,
        'num': '2',
        'lr': 'lang_ru'
    }
    url = 'https://www.googleapis.com/customsearch/v1'
    async with session.get(url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            items = data.get('items', [])
            links = [item['link'] for item in items[:2]]
            return links if links else None
        return None


@dp.message(F.text)
async def handle_text(message: Message):
    text = message.text.strip()
    if text.lower() == "гвинт":
        await message.reply("Гвинт. Выбери колоду:", reply_markup=deck_keyboard())
    elif text.lower() == "история":
        await user_search_history(message)
    elif text.lower() == "статистика":
        await user_stat(message)
    elif text.lower() == "поиск фильма":
        await message.reply("Введите название фильма или сериала для поиска:")
    else:
        async with aiohttp.ClientSession() as session:
            film_info = await get_film_info(text, session)
            if film_info:
                await DATABASE.append(message.from_user.username, film_info['title'])
                links = await get_watch_links(film_info['title'], session)
                response_text = (
                    f"Название: {film_info['title']}\n"
                    f"Рейтинг: {film_info['rating']}\n"
                    f"Постер: {film_info['poster']}"
                )
                if links:
                    response_text += f"\nСсылки для просмотра:\n{chr(10).join(links)}"
                else:
                    response_text += "\nСсылки для просмотра не найдены."
                await message.reply(response_text)
            else:
                await message.reply("Фильм не найден. Попробуйте другое название.")


@dp.callback_query(lambda callback: callback.data and callback.data.startswith("deck:"))
async def process_deck(callback: types.CallbackQuery):
    data = callback.data.split("deck:")[1]
    deck_names = {
        "nil": "Нильфгард ⚔️",
        "ch": "Чудовища 👹",
        "ks": "Королевство Севера ❄️",
        "s": "Скоя’таэли 🔥"
    }
    comments = {
        "nil": "Спорю ты не из тех кто согласится на ничью",
        "ch": "Ведьмак и Чудовища? Хм. Интересно...",
        "ks": "А, понимаю. Патриот",
        "s": "Скоя’таэли — для тех, кто не привык мириться с несправедливостью!"
    }

    deck_name = deck_names.get(data, "Неизвестная колода")
    comment = comments.get(data, "")
    response_message = f"Вы выбрали колоду \"{deck_name}\"\n{comment}"

    await callback.message.answer(response_message)
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
