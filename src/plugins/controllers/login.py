from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

from src.enum.last_state import State
from src.filters.account import account_exist
from src.filters.router import router_filter
from src.filters.state import current_state_filter
from src.plugins.services.login import (
    login_handler,
    login_enter_handler,
    login_failed_enter_handler
)


@Client.on_message(
    filters.command(commands="login", prefixes='/')
)
async def login_controller(
        client: Client,
        message: Message
):
    """
    Start logging process after command /login
    """
    await login_handler(
        client=client,
        user_tg_id=message.from_user.id,
        chat_id=message.chat.id
    )


@Client.on_callback_query(
    router_filter('login')
)
async def login_inline_controller(
        client: Client,
        callback_query: CallbackQuery
):
    """
    Start logging process after inline command button "login"
    """
    await login_handler(
        client=client,
        user_tg_id=callback_query.from_user.id,
        chat_id=callback_query.from_user.id
    )
    await client.answer_callback_query(callback_query.id)


@Client.on_message(
    current_state_filter(State.LOGIN)
    &
    account_exist
)
async def login_enter_controller(
        client: Client,
        message: Message
):
    """
    Enter in account by user telegram id and change state
    """
    await login_enter_handler(
        client=client,
        message=message
    )


@Client.on_message(
    current_state_filter(State.LOGIN)
    &
    ~account_exist
)
async def login_failed_enter_controller(
        client: Client,
        message: Message
):
    """
    Failed enter in account (account doesn't exist)
    """
    await login_failed_enter_handler(
        client=client,
        message=message
    )

