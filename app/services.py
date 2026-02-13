from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from database import get_groups, add_broadcast, add_sent_message


async def broadcast_message(bot: Bot, text: str):
    groups = await get_groups()
    broadcast_id = await add_broadcast(text)
    errors = []

    for group in groups:
        group_id = group[0]
        title = group[1]

        try:
            msg = await bot.send_message(group_id, text)
            await add_sent_message(broadcast_id, group_id, msg.message_id)
        except TelegramForbiddenError:
            errors.append(f"Нет прав: {title} ({group_id})")

    return broadcast_id, errors
