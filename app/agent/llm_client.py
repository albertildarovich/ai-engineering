import httpx

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:1.7b"


class LLMClient:

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=120.0)

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict:
        payload: dict = {
            "model": MODEL,
            "messages": messages,
            "stream": False,
        }

        if tools:
            payload["tools"] = tools

        response = await self.client.post(
            OLLAMA_URL,
            json=payload,
        )

        response.raise_for_status()

        data = response.json()

        return data["message"]

    async def close(self):
        await self.client.aclose()