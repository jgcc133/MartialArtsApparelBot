import os

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.tl.custom import Button

# Global Env Vars
load_dotenv()
API_TELE_BOT = os.environ.get('API_TELE_BOT')
API_TELE_APP_ID  = os.environ.get('API_TELE_APP_ID')
API_TELE_APP_HASH = os.environ.get('API_TELE_APP_HASH')
client = TelegramClient('bot_session', API_TELE_APP_ID, API_TELE_APP_HASH).start(bot_token=API_TELE_BOT)


async def send_hello_message():
    chat_id = 63144080
    message = 'Hello from your bot!'

    await client.send_message(chat_id, message)

@client.on(events.NewMessage)
async def handle_new_message(event):
    sender = await event.get_sender()
    message = event.message.text

    print(f"Received a message from {sender.username} ({sender.id}): {message}")

@client.on(events.NewMessage(pattern='/start'))
async def handle_start_command(event):
    sender = await event.get_sender()
    chat_id = event.message.peer_id
    print(chat_id)
    if isinstance(chat_id, (PeerUser, PeerChat, PeerChannel)):
        await client.send_message(
            chat_id,
            'Welcome to the bot! What would you like to do today?',
            buttons=[
                Button.inline('Find Product', 'test-return'),
                Button.inline('Another Button', 'another-button')
                ]
            )



# Run the event loop to start receiving messages
client.run_until_disconnected()