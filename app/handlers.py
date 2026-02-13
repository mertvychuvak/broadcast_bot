from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command
from config import ADMINS
from database import add_group, get_groups
from services import broadcast_message

router = Router()


def is_admin(user_id: int):
    return user_id in ADMINS


@router.message(Command("start"))
async def start(message: Message):
    if not is_admin(message.from_user.id):
        return

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📊 Статистика")]],
        resize_keyboard=True
    )

    await message.answer("Админ панель", reply_markup=kb)


@router.message(F.new_chat_members)
async def bot_added(message: Message):
    for member in message.new_chat_members:
        if member.id == message.bot.id:
            members = await message.bot.get_chat_member_count(message.chat.id)
            await add_group(message.chat.id, message.chat.title, members)


@router.message(F.text == "📊 Статистика")
async def stats(message: Message):
    if not is_admin(message.from_user.id):
        return

    groups = await get_groups()
    total = sum(g[2] for g in groups)

    text = "📊 Статистика:\n\n"
    for g in groups:
        text += f"{g[1]} — {g[2]} участников\n"

    text += f"\nВсего участников: {total}"

    await message.answer(text)


@router.message()
async def broadcast(message: Message):
    if not is_admin(message.from_user.id):
        return

    broadcast_id, errors = await broadcast_message(message.bot, message.text)

    response = f"✔️ Рассылка ID={broadcast_id}"

    if errors:
        response += "\n\nОшибки:\n" + "\n".join(errors)

    await message.answer(response)
