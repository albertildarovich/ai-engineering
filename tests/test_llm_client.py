import asyncio

from app.agent.llm_client import LLMClient


async def main():
    client = LLMClient()

    try:
        response = await client.chat([
            {
                "role": "user",
                "content": "Привет!",
            }
        ])

        print(response["content"])

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())