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
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token="7618332820:AAGddQyYTTJqVZkibtrcwvAskWTdTAYzx3E")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Ваш API-ключ от Unsplash
UNSPLASH_API_KEY = "AXg_aECrE8IObZN_wwtYlXFLGtX7_1oyeDe3sfOC5t8"


def get_image_url(query):
    try:
        # Добавляем контекст к запросу
        if query.lower() in ["меркурий", "венера", "земля", "марс"]:
            query = f"планета {query}"
        elif query.lower() in ["тигр", "лев", "леопард"]:
            query = f"животное {query}"

        url = "https://api.unsplash.com/search/photos"
        headers = {
            "Authorization": f"Client-ID {UNSPLASH_API_KEY}"
        }
        params = {
            "query": query,  # Ключевое слово для поиска
            "per_page": 1,   # Только одно изображение
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        # Отладочный вывод
        logging.info(f"Результат запроса к Unsplash API: {data}")

        if data.get("results"):
            return data["results"][0]["urls"]["regular"]  # URL изображения среднего размера
        else:
            return None
    except Exception as e:
        logging.error(f"Ошибка при запросе к Unsplash API: {e}")
        return None


age = ["Меньше 6", "От 6 до 12", "От 12 до 16", "От 16 до 18",
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

person = []

right_answer = 0
wrong_answer = 0


def get_db_connection():
    conn = sqlite3.connect('quiz.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_random_question(theme, used_questions):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем случайный вопрос, исключая уже заданные
        if used_questions:
            placeholders = ','.join('?' for _ in used_questions)
            query = f'''
            SELECT id, question_text, correct_answer FROM questions
            WHERE theme = ? AND id NOT IN ({placeholders})
            ORDER BY RANDOM() LIMIT 1
            '''
            cursor.execute(query, (theme, *used_questions))
        else:
            cursor.execute('''
            SELECT id, question_text, correct_answer FROM questions
            WHERE theme = ?
            ORDER BY RANDOM() LIMIT 1
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
                'id': question_id,
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
    await message.answer("Привет! Перед тем, как начать игру, давайте заполним анкету для статистики",
                         reply_markup=keyboard)


@dp.message(F.text == "Да")
async def age_quiz(message: types.Message):
    builder = ReplyKeyboardBuilder()
    for age_option in age:
        builder.add(types.KeyboardButton(text=age_option))
    builder.adjust(4)
    await message.answer(
        "Какой у Вас возраст?",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.message(F.text == "Нет")
async def age_quiz(message: types.Message):
    await message.reply("Если все-таки захотите поиграть, с нетерпением ждем Вас!",
                        reply_markup=types.ReplyKeyboardRemove())


@dp.message(F.text.in_(age))
async def countries_quiz(message: types.Message):
    person.append(str(message.text))
    builder = ReplyKeyboardBuilder()
    for country_option in country:
        builder.add(types.KeyboardButton(text=country_option))
    builder.adjust(5)
    await message.answer(
        "Из какой Вы страны?",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.message(F.text.in_(country))
async def gender_quiz(message: types.Message):
    person.append(str(message.text))
    builder = ReplyKeyboardBuilder()
    for gender_option in gender:
        builder.add(types.KeyboardButton(text=gender_option))
    builder.adjust(2)
    await message.answer("Какого Вы пола?", reply_markup=builder.as_markup(one_time_keyboard=True))


@dp.message(F.text.in_(gender))
async def start_game(message: types.Message):
    person.append(str(message.text))
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
    for category in ["Животные", "Космос", "Праздники", "Фильмы", "Подведем итоги", "Ответы в опросе"]:
        builder.add(types.KeyboardButton(text=category))
    builder.adjust(4)
    await message.answer(
        "Выберите категорию или узнайте о своих результатах:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.message(F.text == "Ответы в опросе")
async def show_survey_results(message: types.Message):
    await message.answer(f"Так Вы ответили в анкете: \n"
                         f"Возраст: {person[0]} \n"
                         f"Страна: {person[1]} \n"
                         f"Пол: {person[2]}")


@dp.message(F.text == "Подведем итоги")
async def show_results(message: types.Message):
    await message.answer(f"Ваш результат: \n"
                         f"Правильных ответов: {right_answer} \n"
                         f"Неправильных ответов: {wrong_answer}")


@dp.message(F.text.in_(["Животные", "Космос", "Праздники", "Фильмы"]))
async def category_selected(message: types.Message, state: FSMContext):
    theme = message.text

    # Сохраняем выбранную категорию и пустой список заданных вопросов
    await state.update_data(theme=theme, used_questions=[])

    await ask_question(message, state)


async def ask_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    theme = data.get("theme")
    used_questions = data.get("used_questions", [])

    # Отладочный вывод для проверки состояния
    logging.info(f"Текущая тема: {theme}, Заданные вопросы: {used_questions}")

    # Получаем случайный вопрос, исключая уже заданные
    question_data = get_random_question(theme, used_questions)

    if question_data:
        question_text = question_data['question']
        options = question_data['options']

        # Создание инлайн-клавиатуры с вариантами ответов
        builder = InlineKeyboardBuilder()
        for option in options:
            builder.add(InlineKeyboardButton(text=option, callback_data=f"answer:{option}"))
        builder.adjust(1)

        # Обновляем список заданных вопросов
        used_questions.append(question_data['id'])
        await state.update_data(used_questions=used_questions)

        # Сохраняем правильный ответ в состоянии
        await state.update_data(correct_answer=question_data['correct_answer'])

        await message.answer(f"Вопрос: {question_text}", reply_markup=builder.as_markup())
    else:
        await message.answer("Вопросы по этой категории закончились! Спасибо за игру!")
        await state.clear()


@dp.callback_query(lambda c: c.data.startswith("answer:"))
async def process_answer(callback_query: types.CallbackQuery, state: FSMContext):
    user_answer = callback_query.data.split(":")[1]  # Ответ пользователя

    data = await state.get_data()
    correct_answer = data.get("correct_answer")

    if user_answer == correct_answer:
        await callback_query.message.answer("Правильно!")
    else:
        await callback_query.message.answer(f"Неправильно! Правильный ответ: {correct_answer}")

    # Получаем изображение для правильного ответа
    image_url = get_image_url(correct_answer)

    if image_url:
        await callback_query.message.answer_photo(
            photo=image_url,
            caption=f"Вот изображение для '{correct_answer}':"
        )
    else:
        await callback_query.message.answer("Извините, не удалось найти изображение.")

    # Задаем следующий вопрос
    await ask_question(callback_query.message, state)


@dp.message(F.text == "Нет, не стоит.")
async def without_puree(message: types.Message):
    await message.reply("Ты многое упускаешь!",
                        reply_markup=types.ReplyKeyboardRemove())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
