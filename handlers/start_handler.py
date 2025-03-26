from aiogram import Router, types, html
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(CommandStart())
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Поддержка")]],
        resize_keyboard=True
    )
    await message.answer(f"Привет {html.bold(message.from_user.username)}!\n\nРады приветствовать в Telegram магазине {html.bold('MiningGear')}", reply_markup=keyboard)