from pyrogram import Client
from config import settings

plugins = dict(
    root="src/plugins/controllers"
)

app = Client(
    name="my_account",
    plugins=plugins,
    api_id=settings.API_ID,
    api_hash=settings.API_HASH,
    bot_token=settings.BOT_TOKEN
)

print('Starting bot...')
app.run()
print('Bot stopped.')
