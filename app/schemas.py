
from typing import Literal

from pydantic import BaseModel


class Task(BaseModel):
    title: str
    priority: Literal["low", "medium", "high"]
    completed: bool
