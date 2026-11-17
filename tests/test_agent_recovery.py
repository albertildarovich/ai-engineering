import asyncio

from app.agent.agent import Agent
from app.agent.llm_client import LLMClient
from app.agent.tool_executor import ToolExecutor
from app.agent.recovery import Recovery
from app.agent_state import AgentState
from app.state_storage import save_state, load_state


async def main():
    executor = ToolExecutor()
    recovery = Recovery(executor)
    llm_client = LLMClient()

    agent = Agent(
        llm_client=llm_client,
        tool_executor=executor,
        recovery=recovery,
    )

    # 1. Создаём состояние, в котором LLM уже запросила три инструмента.
    state = AgentState(
        status="running",
        current_task="Создать две задачи и показать их список",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a task management assistant. "
                    "Use tools to create tasks and retrieve them."
                ),
            },
            {
                "role": "user",
                "content": "Создай две задачи и покажи список.",
            },
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

    try:
        # 2. Имитируем выполнение первого инструмента.
        first_result = executor.execute_idempotently(
            state,
            "call_001",
            "create_task",
            {
                "title": "Изучить Python",
                "priority": "high",
            },
        )

        state.messages.append(
            {
                "role": "tool",
                "content": str(first_result),
                "tool_name": "create_task",
                "tool_call_id": "call_001",
            }
        )

        # 3. Сохраняем состояние перед условным падением.
        save_state(state)

        print("\n--- Application interrupted ---")

        # 4. Загружаем состояние заново из JSON.
        restored_state = load_state()

        if restored_state is None:
            raise RuntimeError("Could not restore agent state")

        print("\n--- State restored from JSON ---")

        # 5. Запускаем Agent с восстановленным состоянием.
        # Recovery должен выполнить только call_002 и call_003.
        result = await agent.resume(restored_state)

        print("\n--- FINAL ANSWER ---")
        print(result)

        print("\n--- AGENT STATUS ---")
        print(restored_state.status)

        print("\n--- TOOL RESULTS ---")
        print(restored_state.tool_results)

    finally:
        await llm_client.close()


if __name__ == "__main__":
    asyncio.run(main())
