import asyncio
import json

import httpx

from app.agent_state import AgentState
from app.state_storage import save_state, load_state
from app.agent_recovery import get_saved_tool_result
from app.tools.task_tools import create_task, get_tasks

MODEL = "qwen3:1.7b"
OLLAMA_URL = "http://localhost:11434/api/chat"

MAX_ITERATIONS = 5

tasks = []


def create_agent_state(user_input: str) -> AgentState:
    return AgentState(
        current_task=user_input,
        status="running",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a task management assistant. "
                    "Use tools when necessary. "
                    "If the user asks to create a task and then "
                    "show tasks, perform both actions in that order. "
                    "After tool execution, explain the results."
                ),
            },
            {
                "role": "user",
                "content": user_input,
            },
        ],
    )

tools = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                    },
                },
                "required": ["title", "priority"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_tasks",
            "description": "Get all existing tasks",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]


def process_pending_tool_calls(state: AgentState):
    assistant_message = None

    for message in reversed(state.messages):
        if message.get("role") == "assistant":
            assistant_message = message
            break

    if assistant_message is None:
        return

    tool_calls = assistant_message.get("tool_calls", [])

    for tool_call in tool_calls:
        function = tool_call["function"]
        name = function["name"]
        arguments = function["arguments"]
        tool_call_id = tool_call["id"]

        already_added = any(
            message.get("role") == "tool"
            and message.get("tool_call_id") == tool_call_id
            for message in state.messages
        )

        if already_added:
            print(f"[TOOL] Already restored: {tool_call_id}")
            continue

        saved_result = get_saved_tool_result(state, tool_call_id)

        if saved_result is not None:
            print(f"[TOOL] Restoring result: {tool_call_id}")
            result = saved_result
        else:
            print(f"[TOOL] Executing missing tool: {name}")

            result = execute_tool(name, arguments)

            state.tool_results.append(
                {
                    "tool_call_id": tool_call_id,
                    "tool_name": name,
                    "result": result,
                }
            )

            save_state(state)

        state.messages.append(
            {
                "role": "tool",
                "content": json.dumps(result, ensure_ascii=False),
                "tool_name": name,
                "tool_call_id": tool_call_id,
            }
        )

        save_state(state)


def execute_tool(name: str, arguments: dict):
    if name == "create_task":
        return create_task(**arguments)

    if name == "get_tasks":
        return get_tasks()

    raise ValueError(f"Unknown tool: {name}")

def execute_tool_idempotently(
    state: AgentState,
    tool_call_id: str,
    tool_name: str,
    arguments: dict,
):
    saved_result = get_saved_tool_result(state, tool_call_id)

    if saved_result is not None:
        print(f"[IDEMPOTENCY] Reusing result: {tool_call_id}")
        return saved_result

    print(f"[IDEMPOTENCY] Executing tool: {tool_call_id}")

    result = execute_tool(tool_name, arguments)

    state.tool_results.append({
        "tool_call_id": tool_call_id,
        "tool_name": tool_name,
        "result": result,
    })

    save_state(state)

    return result


async def ask_llm(client, messages):
    response = await client.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "tools": tools,
            "stream": False,
        },
    )

    response.raise_for_status()

    return response.json()["message"]


async def resume_agent():

    state = load_state()

    if state is None:
        print("No saved state found.")
        return

    if state.status == "completed":
        print("Agent has already completed the task.")
        return

    if state.status == "failed":
        print("Recovering failed agent...")

    if state.status == "running":
        print("Resuming interrupted agent...")

    state.status = "running"

    save_state(state)

    process_pending_tool_calls(state)

    answer = await run_agent(state)

    print("\n--- RESUMED FINAL ANSWER ---")
    print(answer)


async def run_agent(state: AgentState):

    state.status = "running"

    async with httpx.AsyncClient(timeout=120.0) as client:

        try:

            for _ in range(MAX_ITERATIONS):

                state.iteration += 1

                print(f"\n--- Agent iteration {state.iteration} ---")

                message = await ask_llm(
                    client,
                    state.messages,
                )

                state.messages.append(message)

                save_state(state)

                tool_calls = message.get("tool_calls", [])

                if not tool_calls:
                    state.status = "completed"
                    save_state(state)

                    return message.get("content", "")

                for tool_call in tool_calls:

                    function = tool_call["function"]

                    name = function["name"]
                    arguments = function["arguments"]
                    tool_call_id = tool_call["id"]

                    saved_result = get_saved_tool_result(
                        state,
                        tool_call_id,
                    )

                    if saved_result is not None:
                        print(f"[TOOL] Restoring result: {tool_call_id}")
                        result = saved_result

                    else:
                        print(f"[TOOL] Executing: {name}")

                        result = execute_tool(name, arguments)

                        state.tool_results.append(
                            {
                                "tool_call_id": tool_call_id,
                                "tool_name": name,
                                "result": result,
                            }
                        )

                        save_state(state)

                    state.messages.append(
                        {
                            "role": "tool",
                            "content": json.dumps(
                                result,
                                ensure_ascii=False,
                            ),
                            "tool_name": name,
                            "tool_call_id": tool_call_id,
                        }
                    )

                    save_state(state)

            raise RuntimeError("Agent exceeded maximum iterations")

        except Exception:
            state.status = "failed"
            save_state(state)
            raise


async def main():
    user_input = """Создай две задачи:
    1. Изучить Python — высокий приоритет.
    2. Изучить Docker — низкий приоритет.
    После этого покажи все задачи."""

    state = create_agent_state(user_input)

    save_state(state)

    answer = await run_agent(state)

    print("\n--- FINAL ANSWER ---")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())
