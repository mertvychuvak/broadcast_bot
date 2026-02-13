from aiogram import Router, F
from aiogram.types import (
    Message, KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
)
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database import (
    add_group, get_groups,
    add_broadcast, get_broadcasts,
    get_sent_messages,
    add_admin, get_admins,
    add_sent_message
)
from services import broadcast_message

router = Router()


# ----------------- FSM -----------------

class AdminStates(StatesGroup):
    editing = State()
    deleting = State()
    adding_admin = State()


async def is_admin(user_id: int):
    admins = await get_admins()
    return user_id in admins


# ----------------- START PANEL -----------------

@router.message(Command("start"))
async def start(message: Message):
    if not await is_admin(message.from_user.id):
        return

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="✏️ Редактировать рассылку")],
            [KeyboardButton(text="🗑 Удалить рассылку")],
            [KeyboardButton(text="➕ Добавить админа")]
        ],
        resize_keyboard=True
    )

    await message.answer("⚙️ Панель управления", reply_markup=kb)


# ----------------- ADD GROUP -----------------

@router.message(F.new_chat_members)
async def bot_added(message: Message):
    for member in message.new_chat_members:
        if member.id == message.bot.id:
            members = await message.bot.get_chat_member_count(message.chat.id)
            await add_group(message.chat.id, message.chat.title, members)


# ----------------- BROADCAST -----------------

@router.message()
async def broadcast(message: Message):
    if not await is_admin(message.from_user.id):
        return

    if message.text.startswith(("📊", "✏️", "🗑", "➕")):
        return

    broadcast_id, errors = await broadcast_message(message.bot, message.text)

    text = f"✔️ Рассылка ID={broadcast_id}"
    if errors:
        text += "\nОшибки:\n" + "\n".join(errors)

    await message.answer(text)


# ----------------- EDIT -----------------

@router.message(F.text == "✏️ Редактировать рассылку")
async def edit_menu(message: Message):
    broadcasts = await get_broadcasts()

    buttons = [
        [InlineKeyboardButton(
            text=f"ID {b[0]}",
            callback_data=f"edit_{b[0]}"
        )]
        for b in broadcasts[:5]
    ]

    await message.answer(
        "Выберите рассылку:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("edit_"))
async def edit_selected(callback: CallbackQuery, state: FSMContext):
    broadcast_id = int(callback.data.split("_")[1])
    await state.update_data(broadcast_id=broadcast_id)
    await state.set_state(AdminStates.editing)
    await callback.message.answer("Введите новый текст:")
    await callback.answer()


@router.message(AdminStates.editing)
async def edit_text(message: Message, state: FSMContext):
    data = await state.get_data()
    broadcast_id = data["broadcast_id"]

    messages = await get_sent_messages(broadcast_id)

    for group_id, message_id in messages:
        try:
            await message.bot.edit_message_text(
                chat_id=group_id,
                message_id=message_id,
                text=message.text
            )
        except:
            pass

    await message.answer("✔️ Сообщение обновлено")
    await state.clear()


# ----------------- DELETE -----------------

@router.message(F.text == "🗑 Удалить рассылку")
async def delete_menu(message: Message):
    broadcasts = await get_broadcasts()

    buttons = [
        [InlineKeyboardButton(
            text=f"ID {b[0]}",
            callback_data=f"del_{b[0]}"
        )]
        for b in broadcasts[:5]
    ]

    await message.answer(
        "Выберите для удаления:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("del_"))
async def delete_selected(callback: CallbackQuery):
    broadcast_id = int(callback.data.split("_")[1])
    messages = await get_sent_messages(broadcast_id)

    for group_id, message_id in messages:
        try:
            await callback.bot.delete_message(
                chat_id=group_id,
                message_id=message_id
            )
        except:
            pass

    await callback.message.answer("🗑 Удалено во всех группах")
    await callback.answer()


# ----------------- ADD ADMIN -----------------

@router.message(F.text == "➕ Добавить админа")
async def add_admin_start(message: Message, state: FSMContext):
    await state.set_state(AdminStates.adding_admin)
    await message.answer("Введите ID нового администратора:")


@router.message(AdminStates.adding_admin)
async def add_admin_process(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        await add_admin(user_id)
        await message.answer("✔️ Администратор добавлен")
    except:
        await message.answer("❗ Неверный формат ID")

    await state.clear()
