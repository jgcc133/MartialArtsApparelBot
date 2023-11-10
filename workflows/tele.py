import os
import asyncio

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.tl.custom import Button

# Global Env Vars
load_dotenv()
API_TELE_BOT = os.environ.get('API_TELE_BOT')
API_TELE_APP_ID  = os.environ.get('API_TELE_APP_ID')
API_TELE_APP_HASH = os.environ.get('API_TELE_APP_HASH')

CHAT_ID = 63144080
client = TelegramClient(
        'bot_session',
        API_TELE_APP_ID,
        API_TELE_APP_HASH,
        ).start(bot_token=API_TELE_BOT)

print("Client Initialised and Running")
    


# Run the event loop to start receiving messages
client.run_until_disconnected()