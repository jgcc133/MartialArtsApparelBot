import os
import math

from telethon import Button, TelegramClient, events, utils
from workflows import utils as ut
from workflows.control import Control

class Tele:

    def __init__(self, control: Control):
        '''init takes in a control dict obj from Main and creates an instance of chat bot session'''

        self.AUTH = {}
        self.APIS = {}
        self.BOTS = {}

        self.getKeys(control)
        self.createBots(control)

    def start(self):
        try:
            for bot in self.BOTS:
                self.BOTS[bot].start(bot_token=self.APIS[bot])
                ut.pLog("Telegram Chat Bots are online!", p1=True)
                self.BOTS[bot].run_until_disconnected()
        except:
            ut.pLog("Telegram Chat Bot failed to start", p1=True)
    
    def getKeys(self, control) -> None:
        ut.pLog("Obtaining Authentication for Telegram...")
        try:
            AuthRequired = control["Auth"]["data"]["tele"]["app"]
            for key in AuthRequired:
                self.AUTH[key] = os.environ.get(key)
            BotsRequired = control["Auth"]["data"]["tele"]["bots"]
            for key in BotsRequired:
                self.APIS[key] = os.environ.get(BotsRequired[key])
            ut.pLog("Authentication for Telegram Complete.", p1=True) 
        except:
            ut.pLog("Failed to load Authentication for Telegram.", p1=True)

    def createBots(self, control) -> None:
        '''
        untested with connection to telegram server
        '''
        ut.pLog("Imbuing Telegram Bot with Logic Flow...")
        try:
            for api in self.APIS:
                if api != '' and not None:
                    Client = TelegramClient(
                        'bot_session',
                        self.AUTH["AUTH_TELE_APP_ID"],
                        self.AUTH["AUTH_TELE_APP_HASH"]
                        )
                    self.addB2DHandlers(control, Client)
                    ut.pLog("Telegram Chat Bot Logic Flow Created!", p1=True)
                    self.BOTS[api] = Client
        except:
            ut.pLog("Failed to add handlers")

    def addB2DHandlers(self, control, Client) -> None:
        '''
        Setting the commands to be added as event.newMessage
        '''
        
        Commands = control["B2DFlow"]["data"]["commands"]
        Callbacks = control["B2DFlow"]["data"]["callbacks"]
        Default = control["B2DFlow"]["data"]["default"]
        Client = Client
        
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
                        buttons = None if len(Commands[text]["btn"]) == 0 else self.beauButtons(Commands[text]["btn"])
                        await Client.send_message(
                            entity=chat_id,
                            message=Commands[text]["msg"],
                            buttons=buttons)
                        ut.pLog(f"Sent a <{text}> message to user from events.NewMessage", chat_id, chat_username)
                    except:
                        ut.pLog(f"Failed to send <{text}> command from events.NewMessage", p1=True)
                else:
                    print("Fire off a /start to Client or future talking")
                    ut.pLog(f"Sent a <{text}> command that has not been added to the Config list.",chat_id, chat_username)
                    buttons = self.beauButtons(Default["btn"])
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
                        buttons = None if len(Callbacks[data]["btn"]) == 0 else self.beauButtons(Callbacks[data]["btn"]) 
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
                        ut.pLog(f"Failed to send [{data}] message from events.CallbackQuery to user", p1=True)
                else:
                    ut.pLog(f"Clicked on [{data}] button that has not been added to the Config list.",chat_id, chat_username, p1=True)
                    buttons = self.beauButtons(Default["btn"])
                    await Client.send_message(
                            entity=chat_id,
                            message=Default["msg"],
                            buttons=buttons)
        except:
            ut.pLog("Failed to load handlers...", p1=True)

    def beauButtons(self, button_list: list = []) -> list:
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