import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

from orm.core import AsyncCore
from src.enum.last_state import State
from src.filters.account import account_exist
from src.filters.router import router_filter
from src.filters.state import current_state_filter
from src.plugins.start import command_start
from src.plugins.task import start_tasks


@Client.on_message(
    filters.command(commands="login", prefixes='/')
    &
    current_state_filter(State.START)
)
async def login_handler(client: Client, message: Message):
    await client.send_message(message.chat.id, text="Enter your login")
    await AsyncCore().set_session_state(
        user_tg_id=message.chat.id,
        state=State.LOGIN
    )


@Client.on_callback_query(
    router_filter('login')
    &
    current_state_filter(State.START)
)
async def login_handler_inline(client: Client, callback_query: CallbackQuery):
    await client.send_message(
        chat_id=callback_query.message.chat.id,
        text="Enter your login"
    )
    await AsyncCore().set_session_state(
        user_tg_id=callback_query.from_user.id,
        state=State.LOGIN
    )


@Client.on_message(
    current_state_filter(State.LOGIN)
    &
    account_exist
)
async def enter_handler(client: Client, message: Message):
    account = await AsyncCore().execute_account(message.text)
    await client.send_message(
        chat_id=message.chat.id,
        text=f"Hello {account.name}!"
    )
    await AsyncCore().set_session_state(
        account_id=account.id,
        user_tg_id=message.chat.id,
        state=State.TASKS
    )
    await asyncio.sleep(1)
    await start_tasks(client, message)
