import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

logging.basicConfig(level=logging.INFO)
bot = Bot(token="7618332820:AAGddQyYTTJqVZkibtrcwvAskWTdTAYzx3E")
dp = Dispatcher()


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
    await message.answer("Привет", reply_markup=keyboard)


@dp.message(F.text == "Да, давайте!")
async def with_puree(message: types.Message):
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
        input_field_placeholder="Категория"
    )

    await message.reply("Тогда начнем!",
                        reply_markup=types.ReplyKeyboardRemove())
    await message.reply("Какую категорию вопросов Вы выберете?", reply_markup=keyboard)


@dp.message(F.text == "Нет, не стоит.")
async def without_puree(message: types.Message):
    await message.reply("Ты многое упускаешь!",
                        reply_markup=types.ReplyKeyboardRemove())


'''@dp.message(F.text == "Животные")
async def with_puree(message: types.Message):
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
        input_field_placeholder="Категория"
    )

    await message.reply("Тогда начнем!",
                        reply_markup=types.ReplyKeyboardRemove())
    await message.reply("Какую категорию вопросов Вы выберете?", reply_markup=keyboard)'''


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
