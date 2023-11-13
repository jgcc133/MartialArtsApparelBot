import os
import asyncio
import math

from dotenv import load_dotenv
from telethon import Button, TelegramClient, events, utils
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from workflows import utils as ut
from workflows import control_flow

AUTH = {}
COMMANDS = {}
CALLBACKS = {}

def setKeys():
    '''
    Setting the authentication unique to tele
    '''
    
    ut.pLog("Obtaining Authentication...")
    
    try:
        AuthRequired = control_flow.main()["Auth"]["data"]["tele"]
        for key in AuthRequired:
            AUTH[key] = os.environ.get(key)
        ut.pLog("Authenticated.")
    except:
        ut.pLog("Failed to load Authentication.")

def beauButtons(button_list: list = []):
    '''
    Button layout designer.
    1 , 4, 9 (Squares design concept):
    Once the number of buttons exceed the number of squares,
    Just use the higher number of squares and append accordingly
    leaving the last row blank from the right
    '''
    min_square = math.ceil(math.sqrt(len(button_list)))
    
    buttons=[]
    while True:
        for i in range(0, min_square):
            row = []
            for j in range(0,min_square):
                row.append(Button.inline(
                    button_list[i*min_square + j],
                    button_list[i*min_square + j]))
                if i*min_square+j == len(button_list)-1:
                    break
            buttons.append(row)
            if i*min_square+j == len(button_list)-1:
                return buttons

def addHandler():
    '''
    Setting the commands to be added as event.newMessage
    '''
    
    ut.pLog("Obtaining Commands from control_flow...")
    try:
        ut.pLog("List of Commands:")
        Commands = control_flow.main()["Flow"]["data"]["commands"]
        Callbacks = control_flow.main()["Flow"]["data"]["callbacks"]
        ut.pObj(Commands)
        
        @Client.on(events.NewMessage())
        async def handler(event):
            # Obtaining username
            chat_from = event.chat if event.chat else (await event.get_chat())
            chat_username = utils.get_display_name(chat_from)
            chat_id = utils.get_peer_id(chat_from)                
            text = event.raw_text
            ut.pLog(chat_id, chat_username, "Sent a /start message")
        
            if text in Commands.keys():
                ut.pLog(f"Executing {text} command in events.NewMessage")
                try:
                    chat_from = event.chat if event.chat else (await event.get_chat())
                    chat_username = utils.get_display_name(chat_from)
                    chat_id = utils.get_peer_id(chat_from)
                
                    buttons = beauButtons(Commands[text]["btn"])
                    await Client.send_message(
                        entity=chat_id,
                        message=Commands[text]["msg"],
                        buttons=buttons)
                except:
                    ut.pLog(f"Failed try block for {command} command to events.NewMessage")
            else:
                        print("Fire off a /start to Client")
                
    except:
        ut.pLog("Failed to load Commands...")

def addCallbacks():
    '''
    Setting the button callbacks to be added as CallbackQuery
    '''
    print("adding callbacks")

load_dotenv()
setKeys()
Client = TelegramClient(
        'bot_session',
        AUTH["API_TELE_APP_ID"],
        AUTH["API_TELE_APP_HASH"]
        ).start(bot_token=AUTH["API_TELE_BOT"])

addHandler()

Client.run_until_disconnected()