from app.agent_state import AgentState
from app.agent.tool_executor import ToolExecutor


def test_idempotency():
    state = AgentState(
        current_task="Создать задачу",
        status="running",
    )

    executor = ToolExecutor()

    result1 = executor.execute_idempotently(
        state,
        "call_123",
        "create_task",
        {
            "title": "Изучить Python",
            "priority": "high",
        },
    )

    result2 = executor.execute_idempotently(
        state,
        "call_123",
        "create_task",
        {
            "title": "Изучить Python",
            "priority": "high",
        },
    )

    assert result1 == result2
    assert len(state.tool_results) == 1
