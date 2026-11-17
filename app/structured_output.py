
import asyncio
import httpx

from app.schemas import Task


MODEL = "qwen3:4b"


async def generate_task(user_input: str) -> Task:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "http://localhost:11434/api/chat",
            json={
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Ты преобразуешь запросы пользователя "
                            "в задачи. Определи название задачи "
                            "и её приоритет. Если приоритет не указан, "
                            "используй medium. completed всегда false."
                        ),
                    },
                    {
                        "role": "user",
                        "content": user_input,
                    },
                ],
                "format": Task.model_json_schema(),
                "stream": False,
            },
        )

        response.raise_for_status()

        data = response.json()

        content = data["message"]["content"]

        task = Task.model_validate_json(content)

        return task


async def main():
    task = await generate_task(
        "Срочно разобраться с Docker."
    )

    print("Task object:", task)
    print("Task JSON:", task.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
