from pyrogram import Client, idle
# from pyrogram.types import BotCommand

from orm.config import settings

plugins = dict(root="src/plugins")
app = Client(
    name="my_account",
    plugins=plugins,
    api_id=settings.api_id,
    api_hash=settings.api_hash,
    bot_token=settings.bot_token
)

print('Starting bot...')
app.start()
# app.set_bot_commands(bot_commands)
idle()
app.stop()
print('Bot stopped.')
