from app.agent.recovery import Recovery
from app.agent.tool_executor import ToolExecutor
from app.agent_state import AgentState


def main():
    executor = ToolExecutor()
    recovery = Recovery(executor)

    state = AgentState(
        status="running",
        messages=[
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_001",
                        "function": {
                            "name": "create_task",
                            "arguments": {
                                "title": "Изучить Python",
                                "priority": "high",
                            },
                        },
                    },
                    {
                        "id": "call_002",
                        "function": {
                            "name": "create_task",
                            "arguments": {
                                "title": "Изучить FastAPI",
                                "priority": "medium",
                            },
                        },
                    },
                    {
                        "id": "call_003",
                        "function": {
                            "name": "get_tasks",
                            "arguments": {},
                        },
                    },
                ],
            },
        ],
    )

    # Имитируем ситуацию:
    # первый инструмент уже выполнился,
    # но два других ещё нет.

    first_result = executor.execute_idempotently(
        state,
        "call_001",
        "create_task",
        {
            "title": "Изучить Python",
            "priority": "high",
        },
    )

    state.messages.append({
        "role": "tool",
        "content": str(first_result),
        "tool_name": "create_task",
        "tool_call_id": "call_001",
    })

    print("\n--- Simulating application restart ---")

    recovery.process_pending_tool_calls(state)

    print("\n--- Recovery results ---")

    for message in state.messages:
        if message.get("role") == "tool":
            print(
                message["tool_call_id"],
                message["tool_name"],
            )


if __name__ == "__main__":
    main()