from app.agent_state import AgentState


def start_agent(task: str) -> AgentState:
    state = AgentState(
        current_task=task,
        status="running",
    )

    print("Agent started")
    return state


def add_tool_result(
    state: AgentState,
    tool_name: str,
    result: dict,
) -> None:
    state.tool_results.append(
        {
            "tool_name": tool_name,
            "result": result,
        }
    )


def finish_agent(state: AgentState) -> None:
    state.status = "completed"


def add_message(state: AgentState, role: str, content: str) -> None:
    state.messages.append(
        {
            "role": role,
            "content": content
        }
    )

state = start_agent("Create two tasks")

state.iteration += 1

add_tool_result(
    state,
    "create_task",
    {"id": 1, "title": "Learn Python"},
)

add_message(
    state,
    "user",
    "Create two tasks"
)

add_message(
    state,
    "assistant",
    "I will create two tasks."
)

finish_agent(state)


print("\nAgent state:")
print(state.model_dump())
