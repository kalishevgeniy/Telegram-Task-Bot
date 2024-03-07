from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

from orm.core import AsyncCore


@Client.on_message(filters.command(commands="start", prefixes='/'))
async def command_start(client: Client, message: Message):
    welcome_message = """
**Hello**! This is telegram bot for tasks management!
Please, make registration or enter in our account:
    """
    login_button = InlineKeyboardButton(
        text="Login",
        callback_data="login"
    )
    register_button = InlineKeyboardButton(
        text="Register",
        callback_data="register"
    )

    await client.send_message(
        message.chat.id,
        text=welcome_message,
        reply_markup=InlineKeyboardMarkup([[login_button, register_button]]),
        parse_mode=ParseMode.MARKDOWN
    )
    await AsyncCore().start(client, message)
