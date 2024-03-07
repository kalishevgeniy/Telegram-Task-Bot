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


@Client.on_callback_query(
    router_filter('register')
    &
    current_state_filter(State.START)
)
async def register_handler(client, callback_query: CallbackQuery):
    await client.send_message(
        chat_id=callback_query.message.chat.id,
        text="For create user, please enter login"
    )
    await AsyncCore().set_session_state(
        State.REGISTER_LOGIN,
        callback_query.from_user.id
    )


@Client.on_message(
    current_state_filter(State.REGISTER_LOGIN)
    &
    ~account_exist
)
async def registration_login_handler(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"User with login {message.text} create. Now enter your name."
    )

    await AsyncCore().create_account(
        login_account=message.text,
        user_tg_id=message.from_user.id
    )
    await AsyncCore().set_session_state(
        State.REGISTER_NAME,
        user_tg_id=message.chat.id,
        last_value=message.text
    )


@Client.on_message(
    current_state_filter(State.REGISTER_LOGIN)
    &
    account_exist
)
async def forbidden_registration_login_handler(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"Warning! User with login {message.text} already exist!"
    )
    # await asyncio.sleep(1)
    # await command_start(client, message)


@Client.on_message(current_state_filter(State.REGISTER_NAME))
async def registration_name_handler(client: Client, message: Message):
    curr_value = await AsyncCore().execute_current_state(
        user_tg_id=message.from_user.id,
    )
    await client.send_message(
        chat_id=message.chat.id,
        text=f"User {message.text} created!"
    )
    await AsyncCore().update_account(
        name_account=message.text,
        login_account=curr_value.last_value if curr_value else None
    )

    await AsyncCore().set_session_state(
        State.REGISTER_NAME,
        user_tg_id=message.chat.id,
        last_value=message.text
    )
    await command_start(client, message)
