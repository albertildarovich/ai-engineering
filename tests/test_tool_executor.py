from app.agent.tool_executor import ToolExecutor
from app.agent_state import AgentState


def main():
    executor = ToolExecutor()

    print(executor.requires_approval("get_tasks"))
    print(executor.requires_approval("create_task"))
    print(executor.requires_approval("delete_task"))
    state = AgentState(status="running")

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

    print("Results are equal:", result1 == result2)

    print("All tasks:", executor.execute_tool("get_tasks", {}))


if __name__ == "__main__":
    main()