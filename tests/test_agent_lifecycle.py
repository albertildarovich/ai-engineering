
import pytest
from unittest.mock import AsyncMock

from app.agent.agent import Agent
from app.agent_state import AgentState


def create_agent():
    agent = Agent.__new__(Agent)
    agent._run_loop = AsyncMock(return_value="Agent finished")
    return agent


@pytest.mark.asyncio
async def test_idle_state():
    agent = create_agent()
    state = AgentState(status="idle")

    result = await agent.start(state)

    assert result == "Agent finished"
    agent._run_loop.assert_awaited_once_with(state)


@pytest.mark.asyncio
async def test_completed_state_cannot_start():
    agent = create_agent()
    state = AgentState(status="completed")

    with pytest.raises(RuntimeError):
        await agent.start(state)


@pytest.mark.asyncio
async def test_running_state_cannot_start():
    agent = create_agent()
    state = AgentState(status="running")

    with pytest.raises(RuntimeError):
        await agent.start(state)
