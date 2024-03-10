from pyrogram.types import InlineKeyboardButton

login_button = InlineKeyboardButton(
    text="Log in",
    callback_data="login"
)
register_button = InlineKeyboardButton(
    text="Sign in",
    callback_data="signin"
)
