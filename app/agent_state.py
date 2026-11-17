from typing import Any, Literal

from pydantic import BaseModel, Field

AgentStatus = Literal[
    "idle",
    "running",
    "waiting_for_approval",
    "completed",
    "failed",
]


class PendingApproval(BaseModel):
    tool_call_id: str
    tool_name: str
    arguments: dict[str, Any]


class AgentState(BaseModel):
    messages: list[dict[str, Any]] = Field(default_factory=list)

    current_task: str = ""

    tool_results: list[dict[str, Any]] = Field(default_factory=list)

    iteration: int = 0

    status: AgentStatus = "idle"

    pending_approval: PendingApproval | None = None
