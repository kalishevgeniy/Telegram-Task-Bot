from typing import Optional
from pydantic import BaseModel

from src.enum.last_state import State


class UsersPydantic(BaseModel):
    id: int
    tg_id: int
    first_name: str
    last_name: str


class AccountsPydantic(BaseModel):
    id: int
    name: Optional[str]
    login: str


class SessionsPydantic(BaseModel):
    id: int
    user_id: int
    account_id: Optional[int]
    last_state: State
    last_value: Optional[str]


class TasksPydantic(BaseModel):
    id: int
    account_id: int
    name: str
    description: Optional[str]
    is_complete: bool
