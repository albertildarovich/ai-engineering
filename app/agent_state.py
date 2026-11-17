from typing import Any, Literal

from pydantic import BaseModel, Field


AgentStatus = Literal[
    "idle",
    "running",
    "completed",
    "failed",
]


class AgentState(BaseModel):
    messages: list[dict[str, Any]] = Field(default_factory=list)

    current_task: str = ""

    tool_results: list[dict[str, Any]] = Field(default_factory=list)

    iteration: int = 0

    status: AgentStatus = "idle"
