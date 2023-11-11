import os
import asyncio
import logging
import time

from dotenv import load_dotenv
from telethon import Button, TelegramClient, events, utils


# Global Env Vars
# from workflows import tele

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

@client.on(events.NewMessage(pattern='/start'))
async def msg_handler_start(msg):
    '''
    Completely new user
    '''
    print("New User initialising")
    try:
        current_chat_id = await msg.get_peer_id()
        print(current_chat_id)
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


@client.on(events.NewMessage())
async def typical_control_flow(event):
    '''
    Sends a message to ask if user is referring to a previous query, or to a new one
    '''
    await client.send_message(entity=CHAT_ID, message='test typical control flow')

client.run_until_disconnected()