from pyrogram import Client, filters
from pyrogram.types import Message

from src.plugins.services.start import start_handler


@Client.on_message(filters.command(commands="start", prefixes='/'))
async def start_controller(client: Client, message: Message):
    """
    First state in FSM.
    Create new user by telegram id and set state
    """
    return await start_handler(client=client, message=message)
