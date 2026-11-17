import pytest
from unittest.mock import AsyncMock

from app.agent.agent import Agent
from app.agent_state import AgentState
from app.agent.tool_executor import ToolExecutor
from app.agent.recovery import Recovery
from app.agent.llm_client import LLMClient
from app.tools.task_tools import tasks, create_task


@pytest.mark.asyncio
async def test_dangerous_tool_requires_approval():
    llm_client = LLMClient()
    tool_executor = ToolExecutor()
    recovery = Recovery(tool_executor)

    agent = Agent(
        llm_client=llm_client,
        tool_executor=tool_executor,
        recovery=recovery,
    )

    llm_client.chat = AsyncMock(
        return_value={
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call_123",
                    "function": {
                        "name": "delete_task",
                        "arguments": {"task_id": 1},
                    },
                }
            ],
        }
    )

    state = AgentState(messages=[{"role": "user", "content": "Delete task 1"}])

    result = await agent.start(state)

    assert result == "Waiting for human approval"
    assert state.status == "waiting_for_approval"
    assert state.pending_approval is not None
    assert state.pending_approval.tool_name == "delete_task"


@pytest.mark.asyncio
async def test_approve_executes_dangerous_tool():
    tasks.clear()
    task = create_task("Test task", "high")

    llm_client = LLMClient()
    tool_executor = ToolExecutor()
    recovery = Recovery(tool_executor)

    agent = Agent(llm_client, tool_executor, recovery)

    llm_client.chat = AsyncMock(
        side_effect=[
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_456",
                        "function": {
                            "name": "delete_task",
                            "arguments": {"task_id": task["id"]},
                        },
                    }
                ],
            },
            {
                "role": "assistant",
                "content": "Task deleted successfully",
            },
        ]
    )

    state = AgentState(messages=[{"role": "user", "content": "Delete the task"}])

    await agent.start(state)

    assert len(tasks) == 1
    assert state.status == "waiting_for_approval"

    result = await agent.approve(state)

    assert len(tasks) == 0
    assert state.status == "completed"
    assert result == "Task deleted successfully"


@pytest.mark.asyncio
async def test_reject_dangerous_tool():
    tasks.clear()
    task = create_task("Important task", "high")

    llm_client = LLMClient()
    tool_executor = ToolExecutor()
    recovery = Recovery(tool_executor)
    agent = Agent(llm_client, tool_executor, recovery)

    llm_client.chat = AsyncMock(
        side_effect=[
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_789",
                        "function": {
                            "name": "delete_task",
                            "arguments": {"task_id": task["id"]},
                        },
                    }
                ],
            },
            {
                "role": "assistant",
                "content": "I will keep the task.",
            },
        ]
    )

    state = AgentState(messages=[{"role": "user", "content": "Delete the task"}])

    await agent.start(state)

    assert state.status == "waiting_for_approval"
    assert len(tasks) == 1

    result = await agent.reject(state)

    assert len(tasks) == 1
    assert state.status == "completed"
    assert result == "I will keep the task."
