from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

from src.enum.last_state import State
from src.filters.router import router_filter
from src.filters.state import current_state_filter
from src.plugins.services.task import (
    start_task_handler,
    logout_task_handler,
    create_task_handler,
    create_task_name_handler,
    create_task_description_handler,
    get_task_handler,
    choose_task_handler,
    work_with_task_handler,
    back_task_handler,
    delete_task_handler,
    change_status_task_handler,
    edit_task_handler,
    back_task_edit_handler,
    name_task_edit_handler,
    enter_name_task_edit_handler,
    description_task_edit_handler,
    enter_description_task_edit_handler
)


@Client.on_message(
    filters.command(commands="tasks", prefixes='/')
    &
    current_state_filter(State.TASKS)
)
async def start_task_inline_controller(
        client: Client,
        message: Message
):
    """
    Start management task after log in account
    """
    await start_task_handler(
        client=client,
        message=message
    )


@Client.on_callback_query(
    router_filter('logout')
    &
    current_state_filter(State.TASKS)
)
async def logout_task_controller(client: Client, callback_query):
    """
    Inside task management do logout
    This is inline method of command button
    Return to state of login/signin
    """
    await logout_task_handler(
        client=client,
        message=callback_query.message
    )
    await client.answer_callback_query(callback_query.id)


@Client.on_message(
    filters.command(commands="logout", prefixes='/')
    &
    current_state_filter(State.TASKS)
)
async def logout_task_inline_controller(
        client: Client,
        callback_query: CallbackQuery
):
    """
    Inside task management do logout
    This is method of command /logout
    Return to state of login/signin
    """
    await logout_task_handler(
        client=client,
        message=callback_query.message
    )
    await client.answer_callback_query(callback_query.id)


@Client.on_callback_query(
    router_filter('create_task')
    &
    current_state_filter(State.TASKS)
)
async def create_task_controller(
        client: Client,
        callback_query: CallbackQuery
):
    """
    Create new task inside account
    """
    await create_task_handler(
        client=client,
        callback_query=callback_query
    )


@Client.on_message(current_state_filter(State.TASKS_CREATE_NAME))
async def create_task_name_controller(
        client: Client,
        message: Message
):
    """
    Create new task inside account
    Set name
    """
    await create_task_name_handler(
        client=client,
        message=message
    )


@Client.on_message(current_state_filter(State.TASKS_CREATE_DESCRIPTION))
async def create_task_description_controller(
        client: Client,
        message: Message
):
    """
    Create new task inside account
    Set description
    """
    await create_task_description_handler(
        client=client,
        message=message
    )


@Client.on_callback_query(
    router_filter('current_tasks')
    &
    current_state_filter(State.TASKS)
)
async def get_task_controller(
        client: Client,
        callback_query: CallbackQuery
):
    """
    Return list of current tasks
    """
    await get_task_handler(
        client=client,
        callback_query=callback_query
    )


@Client.on_callback_query(
    router_filter('choose_task')
    &
    current_state_filter(State.TASKS)
)
async def choose_task_controller(
        client: Client,
        callback_query: CallbackQuery
):
    """
    Choose task by task id
    #todo use inline button
    """
    await choose_task_handler(
        client=client,
        callback_query=callback_query
    )


@Client.on_message(current_state_filter(State.TASKS_CHOOSE))
async def work_with_task_controller(
        client: Client,
        message: Message
):
    """
    Search task by task id entered by user
    """
    await work_with_task_handler(
        client=client,
        message=message
    )


@Client.on_callback_query(
    router_filter('back_task')
    &
    current_state_filter(State.TASKS_CHOOSE)
)
async def back_task_controller(
        client: Client,
        callback_query: CallbackQuery
):
    """
    Back to all task management from current task
    """
    await back_task_handler(
        client=client,
        callback_query=callback_query
    )


@Client.on_callback_query(
    router_filter('delete_task')
    &
    current_state_filter(State.TASKS_CHOOSE)
)
async def delete_task_controller(
        client: Client,
        callback_query: CallbackQuery
):
    """
    Delete current task by task id
    Task id saved by last session user
    """
    await delete_task_handler(
        client=client,
        callback_query=callback_query
    )


@Client.on_callback_query(
    router_filter('change_status_task')
    &
    current_state_filter(State.TASKS_CHOOSE)
)
async def change_status_task_controller(
        client: Client,
        callback_query: CallbackQuery
):
    """
    Change current task status by inline button
    """
    await change_status_task_handler(
        client=client,
        callback_query=callback_query
    )


@Client.on_callback_query(
    router_filter('edit_task')
    &
    current_state_filter(State.TASKS_CHOOSE)
)
async def edit_task_controller(
        client: Client,
        callback_query: CallbackQuery
):
    """
    Edit current task status by inline button
    """
    await edit_task_handler(
        client=client,
        callback_query=callback_query
    )


@Client.on_callback_query(
    router_filter('back_to_chosen_task')
    &
    current_state_filter(State.TASK_EDIT)
)
async def back_task_edit_controller(
        client: Client,
        callback_query: CallbackQuery
):
    """
    Back to chosen task edit
    """
    await back_task_edit_handler(
        client=client,
        callback_query=callback_query
    )


@Client.on_callback_query(
    router_filter('edit_task_name')
    &
    current_state_filter(State.TASK_EDIT)
)
async def name_task_edit_controller(
        client: Client,
        callback_query: CallbackQuery
):
    """
    Edit task name by inline button
    """
    await name_task_edit_handler(
        client=client,
        callback_query=callback_query
    )


@Client.on_message(current_state_filter(State.TASK_EDIT_NAME))
async def enter_name_task_edit_controller(
        client: Client,
        message: Message
):
    """
    Enter new task name
    """
    await enter_name_task_edit_handler(
        client=client,
        message=message
    )


@Client.on_callback_query(
    router_filter('edit_task_description')
    &
    current_state_filter(State.TASK_EDIT)
)
async def description_task_edit_controller(
        client: Client,
        callback_query: CallbackQuery
):
    """
    Edit task description by inline button
    """
    await description_task_edit_handler(
        client=client,
        callback_query=callback_query
    )


@Client.on_message(
    current_state_filter(State.TASK_EDIT_DESCRIPTION)
)
async def enter_description_task_edit_controller(
        client: Client,
        message: Message
):
    """
    Enter task description by inline button
    """
    await enter_description_task_edit_handler(
        client=client,
        message=message
    )
