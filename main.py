import os
import asyncio

from dotenv import load_dotenv

# Global Env Vars
from workflows import tele

async def main():
    print("Hello World!")
    # print(API_TELE)
    telebot = await tele.main()

main()
# asyncio.run(main())