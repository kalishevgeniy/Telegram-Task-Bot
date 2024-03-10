from pyrogram import Client
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardMarkup
from pyrogram.enums import ParseMode
from pyrogram.types import BotCommand

from orm.core import AsyncCore
from src.plugins.buttons.start import login_button, register_button
from src.plugins.messages.start import welcome_message


async def start_handler(client: Client, message: Message):
    await client.send_message(
        message.chat.id,
        text=welcome_message,
        reply_markup=InlineKeyboardMarkup([[login_button, register_button]]),
        parse_mode=ParseMode.MARKDOWN
    )

    await client.set_bot_commands([
        BotCommand("start", "Start bot"),
        BotCommand("login", "log in"),
        BotCommand("signin", "sign in")]
    )
    await client.delete_bot_commands()

    await AsyncCore().start(
        user_tg_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
