from aiogram import Router, types, F, html
from config import ADMIN_ID
from data.tickets import TicketManager
from datetime import datetime
import pytz

router = Router()
ticket_manager = TicketManager()

KIEV_TZ = pytz.timezone("Europe/Kiev")

@router.message(F.text == "Поддержка")
async def support_request(message: types.Message):
    ticket_id = ticket_manager.start_ticket(message.from_user.id, message.from_user.username)
    await message.answer("Напишите свой вопрос для поддержки.")

@router.message(F.text, F.chat.id != ADMIN_ID)
async def forward_to_admin(message: types.Message):
    ticket_id = ticket_manager.get_ticket_id(message.from_user.id)
    if not ticket_id:
        await message.answer("Используйте кнопку 'Поддержка' перед отправкой сообщения.")
        return

    kiev_time = datetime.now(KIEV_TZ).strftime('%H:%M - %d.%m.%Y')

    formatted_message = (
        f"Бот: Поддержка MiningGear\n\n"
        f"Дата: {kiev_time}\n\n"
        f"Номер обращения: #{ticket_id}\n\n"
        f"Имя тг клиента: @{message.from_user.username}\n\n"
        f"ID клиента: {message.from_user.id}\n\n\n\n"
        f"Сообщение:\n{message.text}"
    )

    # Отправляем админу
    sent_msg = await message.bot.send_message(ADMIN_ID, formatted_message)

    # Сохраняем сообщение в истории
    ticket_manager.store_message(ticket_id, message.from_user, message.text, "Клиент")

    # Подтверждаем пользователю
    await message.answer(
        "✅ Отправили сообщение!\n\n"
        f'⏳ Ответим как можно быстрее. \n\nЧтобы отправить ещё одно сообщение, сделайте это через кнопку "Поддержка".'
    )

@router.message(F.reply_to_message, F.chat.id == ADMIN_ID)
async def reply_to_user(message: types.Message):
    ticket_id = ticket_manager.extract_ticket_id(message.reply_to_message.text)
    if not ticket_id:
        await message.answer("Ошибка: обращение не найдено.")
        return

    user_id = ticket_manager.get_user_by_ticket(ticket_id)
    if not user_id:
        await message.answer("Ошибка: клиент не найден.")
        return

    # Отправляем ответ клиенту
    await message.bot.send_message(user_id, f"📩 Ответ от поддержки:\n\n{message.text}")

    # Сохраняем ответ в историю
    ticket_manager.store_message(ticket_id, "Поддержка", message.text, "Поддержка")

@router.message(F.text.startswith("/delete_ticket"), F.chat.id == ADMIN_ID)
async def delete_ticket(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Используйте команду /delete_ticket <номер>")
        return

    ticket_id = parts[1]
    user_id = ticket_manager.get_user_by_ticket(ticket_id)

    if not user_id:
        await message.answer(f"Ошибка: обращение #{ticket_id} не найдено.")
        return

    # Закрываем обращение
    ticket_manager.close_ticket(ticket_id)

    # Уведомляем клиента
    await message.bot.send_message(user_id, "❌ Ваше обращение закрыто!")

    # Подтверждаем админу
    await message.answer(f"Обращение #{ticket_id} закрыто.")
