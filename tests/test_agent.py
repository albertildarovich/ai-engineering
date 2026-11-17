import asyncio

from app.agent.agent import Agent
from app.agent.llm_client import LLMClient
from app.agent.tool_executor import ToolExecutor
from app.agent_state import AgentState
from app.agent.recovery import Recovery


async def main():
    executor = ToolExecutor()
    recovery = Recovery(executor)
    llm_client = LLMClient()

    agent = Agent(
        llm_client=llm_client,
        tool_executor=executor,
        recovery=recovery,
    )

    state = AgentState(
        current_task="Создать две задачи и показать их список",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a task management assistant. "
                    "Use tools to create tasks and retrieve them. "
                    "Always use get_tasks after creating tasks."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Создай две задачи: "
                    "'Изучить Python' с высоким приоритетом "
                    "и 'Изучить FastAPI' со средним приоритетом. "
                    "Затем покажи список задач."
                ),
            },
        ],
    )

    try:
        result = await agent.start(state)

        print("\n--- FINAL ANSWER ---")
        print(result)

        print("\n--- AGENT STATUS ---")
        print(state.status)

        print("\n--- TOOL RESULTS ---")
        print(state.tool_results)

    finally:
        await llm_client.close()


if __name__ == "__main__":
    asyncio.run(main())