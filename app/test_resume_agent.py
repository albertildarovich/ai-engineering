import asyncio
from app.multi_step_agent import resume_agent

async def main():
    await resume_agent()

if __name__ == "__main__":
    asyncio.run(main())