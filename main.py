import os
import asyncio

from dotenv import load_dotenv

# Global Env Vars
from workflows import tele

def main():
    print("Hello World!")
    # print(API_TELE)
    telebot = tele.gram()
    telebot.p()

main()
# asyncio.run(main())