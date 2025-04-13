import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
import sqlite3

logging.basicConfig(level=logging.INFO)

bot = Bot(token="7618332820:AAGddQyYTTJqVZkibtrcwvAskWTdTAYzx3E")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

age = ["Меньше 6", "От 12 до 16", "От 16 до 18",
       "От 18 до 25", "От 25 до 35", "От 35 до 45",
       "От 45 до 60", "От 60 до 70", "От 70 до 80",
       "От 80 до 100", "Больше 100"]

country = [
    "🇺🇸 США", "🇷🇺 Россия", "🇵🇱 Польша", "🇨🇳 Китай", "🇦🇽 Швеция",
    "🇦🇲 Армения", "🇨🇿 Чехия", "🇩🇰 Дания", "🇯🇴 Палестина", "🇪🇪 Эстония",
    "🇪🇬 Египет", "🇧🇾 Беларусь", "🇧🇷 Бразилия", "🇨🇦 Канада", "🇫🇮 Финляндия",
    "🇫🇷 Франция", "🇬🇷 Греция", "🇩🇪 Германия", "🇬🇪 Грузия", "🇧🇬 Болгария",
    "🇷🇴 Румыния", "🇹🇷 Турция", "🇮🇹 Италия", "🇸🇰 Словакия", "🇸🇦 Саудовская аравия"
]

gender = ["♂ Мужчина", "♀ Женщина"]


def get_db_connection():
    conn = sqlite3.connect('quiz.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_random_question(theme):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
        SELECT id, question_text, correct_answer FROM questions
        WHERE theme = ? ORDER BY RANDOM() LIMIT 1
        ''', (theme,))
        question = cursor.fetchone()

        if question:
            question_id, question_text, correct_answer = question

            cursor.execute('''
            SELECT option_text FROM options WHERE question_id = ?
            ''', (question_id,))
            options = [row['option_text'] for row in cursor.fetchall()]

            conn.close()
            return {
                'question': question_text,
                'options': options,
                'correct_answer': correct_answer
            }
        conn.close()
        return None
    except Exception as e:
        logging.error(f"Ошибка при получении вопроса: {e}")
        return None


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Да"),
            types.KeyboardButton(text="Нет")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Заполняем анкету"
    )
    await message.answer("Привет! Перед тем,как начать игру давайте заполним анкету для статистики",
                         reply_markup=keyboard)


@dp.message(F.text == "Да")
async def age_quiz(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text=("Меньше 6")))
    builder.add(types.KeyboardButton(text=("От 6 до 12")))
    builder.add(types.KeyboardButton(text=("От 12 до 16")))
    builder.add(types.KeyboardButton(text=("От 16 до 18")))
    builder.add(types.KeyboardButton(text=("От 18 до 25")))
    builder.add(types.KeyboardButton(text=("От 25 до 35")))
    builder.add(types.KeyboardButton(text=("От 35 до 45")))
    builder.add(types.KeyboardButton(text=("От 45 до 60")))
    builder.add(types.KeyboardButton(text=("От 60 до 70")))
    builder.add(types.KeyboardButton(text=("От 70 до 80")))
    builder.add(types.KeyboardButton(text=("От 80 до 100")))
    builder.add(types.KeyboardButton(text=("Больше 100")))
    builder.adjust(4)
    await message.answer(
        "Какой у Вас возраст?",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.message(F.text == "Нет")
async def age_quiz(message: types.Message):
    await message.reply("Если все-таки зохотите поиграть, с нетерпением ждем Вас!",
                        reply_markup=types.ReplyKeyboardRemove())


@dp.message(F.text.in_(age))
async def countries_quiz(message: types.Message):
    countries = [
        {'emoji': '🇺🇸', 'name': 'США'}, {'emoji': '🇷🇺', 'name': 'Россия'},
        {'emoji': '🇵🇱', 'name': 'Польша'}, {'emoji': '🇨🇳', 'name': 'Китай'},
        {'emoji': '🇦🇽', 'name': 'Швеция'}, {'emoji': '🇦🇲', 'name': 'Армения'},
        {'emoji': '🇨🇿', 'name': 'Чехия'}, {'emoji': '🇩🇰', 'name': 'Дания'},
        {'emoji': '🇯🇴', 'name': 'Палестина'}, {'emoji': '🇪🇪', 'name': 'Эстония'},
        {'emoji': '🇪🇬', 'name': 'Египет'}, {'emoji': '🇧🇾', 'name': 'Беларусь'},
        {'emoji': '🇧🇷', 'name': 'Бразилия'}, {'emoji': '🇨🇦', 'name': 'Канада'},
        {'emoji': '🇫🇮', 'name': 'Финляндия'}, {'emoji': '🇫🇷', 'name': 'Франция'},
        {'emoji': '🇬🇷', 'name': 'Греция'}, {'emoji': '🇩🇪', 'name': 'Германия'},
        {'emoji': '🇬🇪', 'name': 'Грузия'}, {'emoji': '🇧🇬', 'name': 'Болгария'},
        {'emoji': '🇷🇴', 'name': 'Румыния'}, {'emoji': '🇹🇷', 'name': 'Турция'},
        {'emoji': '🇮🇹', 'name': 'Италия'}, {'emoji': '🇸🇰', 'name': 'Словакия'},
        {'emoji': '🇸🇦', 'name': 'Саудовская аравия'}
    ]

    builder = ReplyKeyboardBuilder()
    for contry in countries:
        builder.add(types.KeyboardButton(text=f"{contry['emoji']} {contry['name']}"))
    builder.adjust(5)

    await message.answer(
        "Выберете из Вы какой страны",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.message(F.text.in_(country))
async def countries_quiz(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="♂ Мужчина"))
    builder.add(types.KeyboardButton(text="♀ Женщина"))
    await message.answer("Какого Вы пола? ", reply_markup=builder.as_markup(one_time_keyboard=True))


@dp.message(F.text.in_(gender))
async def countries_quiz(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Да, давайте!"),
            types.KeyboardButton(text="Нет, не стоит.")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Хотите начать игру?"
    )
    await message.answer("Поздравляем! Опрос окончен, можем перейти к игре", reply_markup=keyboard)


@dp.message(F.text == "Да, давайте!")
async def start_quiz(message: types.Message):
    builder = ReplyKeyboardBuilder()
    for i in ["Животные", "Космос", "Праздники", "Фильмы", "Подведем итоги"]:
        builder.add(types.KeyboardButton(text=str(i)))
    builder.adjust(4)
    await message.answer(
        "Выберите категорию или узнайте о своих результатах:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


"""@dp.message(F.text == "Подведем итоги")
async def start_quiz(message: types.Message):"""


@dp.message(F.text.in_(["Животные", "Космос", "Праздники", "Фильмы"]))
async def category_selected(message: types.Message, state: FSMContext):
    theme = message.text

    await state.update_data(theme=theme)

    await ask_question(message, state)


async def ask_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    theme = data.get("theme")

    question_data = get_random_question(theme)

    if question_data:
        question_text = question_data['question']
        options = question_data['options']

        builder = InlineKeyboardBuilder()
        for option in options:
            builder.add(InlineKeyboardButton(text=option, callback_data=f"answer:{option}"))
        builder.adjust(1)

        await state.update_data(correct_answer=question_data['correct_answer'])

        await message.answer(f"Вопрос: {question_text}", reply_markup=builder.as_markup())
    else:
        await message.answer("Вопросы по этой категории закончились! Спасибо за игру!")
        await state.clear()


@dp.callback_query(lambda c: c.data.startswith("answer:"))
async def process_answer(callback_query: types.CallbackQuery, state: FSMContext):
    user_answer = callback_query.data.split(":")[1]

    data = await state.get_data()
    correct_answer = data.get("correct_answer")

    if user_answer == correct_answer:
        await callback_query.message.answer("Правильно!")
    else:
        await callback_query.message.answer(f"Неправильно! Правильный ответ: {correct_answer}")

    await ask_question(callback_query.message, state)


@dp.message(F.text == "Нет, не стоит.")
async def without_puree(message: types.Message):
    await message.reply("Ты многое упускаешь!",
                        reply_markup=types.ReplyKeyboardRemove())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
