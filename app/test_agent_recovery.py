from app.multi_step_agent import create_agent_state
from app.state_storage import save_state


def main():
    user_input = "Создай две задачи и покажи их."

    state = create_agent_state(user_input)

    state.iteration = 1
    state.status = "running"

    state.messages.append({
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "id": "call_123",
                "function": {
                    "name": "create_task",
                    "arguments": {
                        "title": "Изучить Python",
                        "priority": "high",
                    },
                },
            },
            {
                "id": "call_456",
                "function": {
                    "name": "create_task",
                    "arguments": {
                        "title": "Изучить Docker",
                        "priority": "low",
                    },
                },
            },
        ],
    })

    state.tool_results.append({
        "tool_call_id": "call_123",
        "tool_name": "create_task",
        "result": {
            "id": 1,
            "title": "Изучить Python",
            "priority": "high",
            "completed": False,
        },
    })

    save_state(state)

    print("Simulated interrupted agent!")
    print(f"Status: {state.status}")
    print(f"Iteration: {state.iteration}")
    print(f"Saved tool results: {len(state.tool_results)}")


if __name__ == "__main__":
    main()