import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
import sqlite3

logging.basicConfig(level=logging.INFO)

bot = Bot(token="7618332820:AAGddQyYTTJqVZkibtrcwvAskWTdTAYzx3E")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


def get_db_connection():
    conn = sqlite3.connect('quiz.db')
    conn.row_factory = sqlite3.Row  # Для получения результатов в виде словарей
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
            types.KeyboardButton(text="Да, давайте!"),
            types.KeyboardButton(text="Нет, не стоит.")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Хотите начать игру?"
    )
    await message.answer("Привет! Хотите сыграть в квиз?", reply_markup=keyboard)


@dp.message(F.text == "Да, давайте!")
async def start_quiz(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Животные"),
            types.KeyboardButton(text="Космос"),
            types.KeyboardButton(text="Праздники"),
            types.KeyboardButton(text="Фильмы"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите категорию"
    )

    await message.reply("Отлично! Выберите категорию:", reply_markup=keyboard)


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
