import os
import asyncio
import logging
import time

from dotenv import load_dotenv
from telethon import Button, TelegramClient, events, utils
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from workflows import utils as ut

# Global Env Vars
# from workflows import tele

load_dotenv()
API_TELE_BOT = os.environ.get('API_TELE_BOT')
API_TELE_APP_ID  = os.environ.get('API_TELE_APP_ID')
API_TELE_APP_HASH = os.environ.get('API_TELE_APP_HASH')
CHAT_ID = os.environ.get('CHAT_ID') # Chat ID between myself and the bot, purely for debugging purposes

client = TelegramClient(
        'bot_session',
        API_TELE_APP_ID,
        API_TELE_APP_HASH
        ).start(bot_token=API_TELE_BOT)

COMMANDS = ['/start', '/help', '/products', '/viewing', '/others']

@client.on(events.NewMessage(pattern='/start'))
async def msg_handler_start(msg):
    '''
    Completely new user. Returns a start welcome message based on the chat user ID
    For channels, the flow and context will be handled separately
    '''
    try:
        # Obtaining username
        chat_from = msg.chat if msg.chat else (await msg.get_chat())
        chat_username = utils.get_display_name(chat_from)
        chat_id = utils.get_peer_id(chat_from)
        ut.pLog(chat_id, chat_username, "Sent a /start message")
        
        response = await client.send_message(
            entity=chat_id,
            message="Welcome to Martial Arts Apparel Bot! What services would you like to take a look at?",
            buttons=[
                [Button.inline('Product Enquiry', 'msg_handler_product')],
                [Button.inline('Arrange Viewing', 'msg_handler_viewing')],
                [Button.inline('Other Services', 'msg_handler_others')]
                ])
        ut.pLog(chat_id, chat_username, "Start Message sent to User")
    except:
        print("msg_handler_start encountered an error")

@client.on(events.NewMessage())
async def typical_control_flow(msg):
    '''
    Sends a message to ask if user is referring to a previous query (on services not products),
    or to a new one.
    Under a new query, start handler is triggered
    '''
    print("Setting up handler number 2")
    try:
        conv = await msg.get_chat()
        chat_from = msg.chat if msg.chat else (await msg.get_chat())
        chat_text = msg.message if msg.message else (await msg.get_message())
        
        if chat_text.message not in COMMANDS:            
            chat_username = utils.get_display_name(chat_from)
            chat_id = utils.get_peer_id(chat_from)
            ut.pLog(chat_id, chat_username, f"Sent <'{chat_text.message}'>, a message that's not an existing command")

            await client.send_message(
                entity=chat_id,
                message='Resume previous enquiry?',
                buttons=[
                    Button.inline('New Enquiry', b'start'),
                    Button.inline('Previous Enquiry', b'previous_query')
                    ])
    
    except:
        print("typical_control_flow encountered an error")





# sets of functions only triggered by buttons
# inaccessible by commands

@client.on(events.CallbackQuery(data=b'start'))
async def handler(event):
    await msg_handler_start(event)

@client.on(events.CallbackQuery(data=b'previous_query'))
async def msg_handler_query_previous(msg):
    '''
    When this function is called, bot will query the last choice
    that the user has selected, on a Service level query
    (View  Products / shop, vs arrange viewing vs other services)
    And resume USER's selection
    data object is stored as a _ _ _?
    '''
    pass

client.run_until_disconnected()