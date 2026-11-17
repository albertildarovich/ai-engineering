
import asyncio
import httpx


MODEL = "qwen3:4b"

SYSTEM_PROMPT = """
Ты — дружелюбный преподаватель Python.
Объясняй простыми словами на русском.
Учитывай предыдущие сообщения в диалоге.
"""


async def ask_llm(messages: list[dict[str, str]]) -> str:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "http://localhost:11434/api/chat",
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False,
            },
        )

        response.raise_for_status()

        data = response.json()

        return data["message"]["content"]


async def main():
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        messages.append({
            "role": "user",
            "content": user_input,
        })

        answer = await ask_llm(messages)

        messages.append({
            "role": "assistant",
            "content": answer,
        })

        print("\nAI:", answer)


if __name__ == "__main__":
    asyncio.run(main())
