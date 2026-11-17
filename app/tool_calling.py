
import asyncio
import json
import httpx


MODEL = "qwen3:4b"

OLLAMA_URL = "http://localhost:11434/api/chat"


def create_task(title: str, priority: str):
    print("\n[TOOL] Creating task...")

    return {
        "success": True,
        "title": title,
        "priority": priority,
    }



tools = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                    },
                },
                "required": ["title", "priority"],
            },
        },
    }
]


def execute_tool(tool_call):
    function_name = tool_call["function"]["name"]
    arguments = tool_call["function"]["arguments"]

    if function_name == "create_task":
        return create_task(**arguments)

    raise ValueError(f"Unknown tool: {function_name}")



async def run_agent(user_input: str):

    messages = [
        {
            "role": "system",
            "content": (
                "You are a task management assistant. "
                "Use create_task when the user asks to create a task. "
                "After receiving the tool result, explain the result."
            ),
        },
        {
            "role": "user",
            "content": user_input,
        },
    ]

    async with httpx.AsyncClient(timeout=120.0) as client:

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

        message = response.json()["message"]

        messages.append(message)

        tool_calls = message.get("tool_calls", [])

        if not tool_calls:
            return message.get("content", "")

        for tool_call in tool_calls:

            result = execute_tool(tool_call)

            messages.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_name": tool_call["function"]["name"],
            })

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

        final_message = response.json()["message"]

        return final_message.get("content", "")


async def main():

    answer = await run_agent(
        "Create a task: Learn Docker, low priority."
    )

    print("\n[FINAL ANSWER]")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())
