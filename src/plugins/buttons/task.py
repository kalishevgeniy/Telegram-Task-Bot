from pyrogram.types import InlineKeyboardButton

get_list_tasks_button = InlineKeyboardButton(
    text="Get current tasks",
    callback_data="current_tasks"
)
create_task_button = InlineKeyboardButton(
    text="Create new tasks",
    callback_data="create_task"
)
choose_task_button = InlineKeyboardButton(
    text="Choose task",
    callback_data="choose_task"
)
logout_button = InlineKeyboardButton(
    text="Logout",
    callback_data="logout"
)

# ###########################################################################

edit_button = InlineKeyboardButton(
    text="Edit task",
    callback_data="edit_task"
)
delete_button = InlineKeyboardButton(
    text="Delete task",
    callback_data="delete_task"
)
change_status_button = InlineKeyboardButton(
    text="I haven't done task =(",
    callback_data="change_status_task"
)
back_button = InlineKeyboardButton(
    text="Back",
    callback_data="back_task"
)

# ##########################################################################

edit_name_button = InlineKeyboardButton(
    text="Name",
    callback_data="edit_task_name"
)
edit_description_button = InlineKeyboardButton(
    text="Description",
    callback_data="edit_task_description"
)
back_to_task_button = InlineKeyboardButton(
    text="Back",
    callback_data="back_to_chosen_task"
)
