import os
import asyncio
import math
import yaml

from dotenv import load_dotenv
from telethon import Button, TelegramClient, events, utils
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from workflows import utils as ut
from workflows import control_flow

AUTH = {}

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
    try:
        control_file = 'workflows/control.yml'
        with open(control_file, 'r') as file:
            Control = yaml.safe_load(file)
            
        Commands = Control["Flow"]["data"]["commands"]
        Callbacks = Control["Flow"]["data"]["callbacks"]
        Default = Control["Flow"]["data"]["default"]
        ut.pLog(f"Control has been loaded from {control_file}")
    except:
        ut.pLog("Unable to load control flow from control.yml")
    
    try:        
        @Client.on(events.NewMessage())
        async def handler(event):
            # Obtaining username
            chat_from = event.chat if event.chat else (await event.get_chat())
            chat_username = utils.get_display_name(chat_from)
            chat_id = utils.get_peer_id(chat_from)                
            text = event.raw_text
            ut.pLog(f"Sent a <{text}> message.",chat_id, chat_username)
        
            if text in Commands.keys():
                try:                
                    buttons = None if len(Commands[text]["btn"]) == 0 else beauButtons(Commands[text]["btn"])
                    await Client.send_message(
                        entity=chat_id,
                        message=Commands[text]["msg"],
                        buttons=buttons)
                    ut.pLog(f"Sent a <{text}> message to user from events.NewMessage", chat_id, chat_username)
                except:
                    ut.pLog(f"Failed to send <{text}> command from events.NewMessage")
            else:
                print("Fire off a /start to Client or future talking")
                ut.pLog(f"Sent a <{text}> command that has not been added to the Config list.",chat_id, chat_username)
                buttons = beauButtons(Default["btn"])
                await Client.send_message(
                        entity=chat_id,
                        message=Default["msg"],
                        buttons=buttons)
        
        @Client.on(events.CallbackQuery())
        async def handler(event):
            # Obtaining username
            chat_from = event.chat if event.chat else (await event.get_chat())
            chat_username = utils.get_display_name(chat_from)
            chat_id = utils.get_peer_id(chat_from)
            
            # Obtain message details to subsequently append response and clear buttons
            msg_id = event.message_id
            msg = await event.get_message()
            
            data = str(event.data, encoding='utf-8')
            ut.pLog(f"Clicked on [{data}]",chat_id, chat_username)
            
            if data in Callbacks.keys():
                try:
                    # Send message based on control flow
                    buttons = None if len(Callbacks[data]["btn"]) == 0 else beauButtons(Callbacks[data]["btn"]) 
                    await Client.send_message(
                        entity=chat_id,
                        message=Callbacks[data]["msg"],
                        buttons=buttons)
                    ut.pLog(f"Sent [{data}] message to user", chat_id, chat_username)

                    # Append response and clear buttons
                    new_text = msg.text + "\n\n__**" + str(event.data, encoding='utf-8') + "**__"
                    await Client.edit_message(
                        entity=event.sender_id,
                        message=msg_id,
                        text=new_text,
                        buttons=Button.clear())
                except:
                    ut.pLog(f"Failed to send [{data}] message from events.CallbackQuery to user")
            else:
                ut.pLog(f"Clicked on [{data}] button that has not been added to the Config list.",chat_id, chat_username)
                buttons = beauButtons(Default["btn"])
                await Client.send_message(
                        entity=chat_id,
                        message=Default["msg"],
                        buttons=buttons)
    except:
        ut.pLog("Failed to load handlers...")

load_dotenv()
setKeys()
Client = TelegramClient(
        'bot_session',
        AUTH["API_TELE_APP_ID"],
        AUTH["API_TELE_APP_HASH"]
        ).start(bot_token=AUTH["API_TELE_BOT"])

addHandler()

Client.run_until_disconnected()