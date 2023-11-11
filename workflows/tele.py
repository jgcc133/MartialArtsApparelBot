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
        API_TELE_APP_HASH
        ).start(bot_token=API_TELE_BOT)

print("Client Initialised and Running")


@client.on(events.NewMessage())
async def typical_control_flow(event):
    '''
    Sends a message to ask if user is referring to a previous query, or to a new one
    '''
    client.send_message('me','test typical control flow')

@client.on(events.NewMessage(pattern='/start'))
async def msg_handler_start():
    '''
    Completely new user
    '''
    print("New User initialising")
    try:
        response = await client.send_message(
            entity=CHAT_ID,
            message="Welcome to Martial Arts Apparel Bot! What services would you like to take a look at?",
            buttons=[
                Button.inline('Enquire about products', 'msg_handler_product'),
                Button.inline('Arrange for viewing', 'msg_handler_viewing'),
                Button.inline('Other Services', 'msg_handler_others')
                ])
        print("New User initialised")
    except:
        print("error")


# Run the event loop to start receiving messages
client.run_until_disconnected()