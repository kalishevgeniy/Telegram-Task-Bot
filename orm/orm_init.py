import asyncio
from core import AsyncCore


async def main():
    await AsyncCore.create_tables()


if __name__ == "__main__":
    asyncio.run(main())
