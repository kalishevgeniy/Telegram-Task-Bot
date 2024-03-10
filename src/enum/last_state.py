from enum import Enum


class State(Enum):
    START = 'start'
    LOGIN = 'login'

    REGISTER_NAME = 'register_name'
    REGISTER_LOGIN = 'register_login'

    TASKS = 'tasks'
    TASKS_CREATE_NAME = 'tasks_create_name'
    TASKS_CREATE_DESCRIPTION = 'tasks_create_description'
    TASKS_UPDATE_NAME = 'tasks_update_name'
    TASKS_CHOOSE = 'tasks_choose'

    TASK_EDIT = 'tasks_edit'
    TASK_EDIT_NAME = 'tasks_edit_name'
    TASK_EDIT_DESCRIPTION = 'tasks_edit_description'
