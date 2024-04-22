import os
import math
import telethon.sync

from telethon import Button, TelegramClient, events, utils
from workflows import utils as ut
from workflows.control import Control

class Tele:

    def __init__(self, control: Control):
        '''init takes in a control dict obj from Main and creates an instance of chat bot session'''

        self.AUTH = {}
        self.APIS = {}
        self.BOTS = {}
        self.__target_coro = {}

        self.getKeys(control)
        self.createBots()
        pass
    """
    async def start(self):
        '''
        Starts the various telegram bots within self.BOTS
        (For projects with more than one chatbot)        
        '''
        try:
            for bot in self.BOTS:
                # self.BOTS[bot].start(bot_token=self.APIS[bot])
                await self.BOTS[bot].run_until_disconnected()
                async with self.BOTS[bot] as client:
                    await client.run_until_disconnected()
        except:
            ut.pLog("Telegram Chat Bot failed to start", p1=True)

    
    async def stop(self):
        '''
        Stops the various telegram bots within self.BOTS
        (For projects with more than one chatbot)        
        '''
        try:
            for bot in self.BOTS:
                async with self.BOTS[bot] as client:
                    await client.disconnect()
        except:
            ut.pLog("Telegram Chat Bot failed to stop", p1=True)
    """
    
    def getKeys(self, control) -> None:
        '''
        Loads keys from environment variables based on configuration provided in control.yml

        Variables:
        control - control dictionary loaded from control.yml

        returns None (self.AUTH and self.APIS are set without any return value)
        '''
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

    def createBots(self):
        '''
        Creates a Telegram Bot based on API key provided in the environment variables
        Calls addB2DHandlers based on B2DFlow in control.yml

        Variables:
        control - control dictionary loaded from control.yml

        returns self.BOTS[<platform>] = telegram bot client, which can be called to start
        '''
        ut.pLog("Imbuing Telegram Bot with Logic Flow...")
        try:
            for api_k, api_v in self.APIS.items():
                if api_k != '' and not None:
                    Client = TelegramClient(
                        'bot_session',
                        self.AUTH["AUTH_TELE_APP_ID"],
                        self.AUTH["AUTH_TELE_APP_HASH"]
                        )
                    # self.addB2DHandlers(control, Client)
                    ut.pLog("Telegram Chat Bot Logic Flow Created!", p1=True)
                    self.BOTS[api_k] = Client
            return Client
        except:
            ut.pLog("Failed to create bots")

    async def update(self, control):
        
        self.__addB2DHandlers(control)
        await self.__uploadMedia(control)


    async def __uploadMedia(self, control):
        Client = self.BOTS['b2d']
        media_list = control['MediaList']['data']
        media_prefix = control['Source']['data']['GoogleDrive']['storage']
        for file_name in media_list.keys():
            # For dev: TODO - remove this limiter of 4 files (2 photos, 2 pdfs)
            if file_name in ["1081A051_020_SB_BT_GLB.png"]:

                with open(media_prefix + file_name, "rb") as media:
                    self.__target_coro[file_name]= await Client.send_file(
                        entity = 63144080,
                        file=media,
                        file_name=file_name,
                        )
            # TODO And remove indentation of with block and await block as well
            
                await Client.send_message(
                                entity=63144080,
                                message=f"[File {len(self.__target_coro)} out of {len(media_list.keys())}] {file_name} uploaded!")
                            
        ut.pLog("Telegram Chat Bot Media Uploaded!", p1=True)
        
    def __addB2DHandlers(self, control) -> None:
        '''
        Adds callback handlers (for buttons) and commands (for shortcut commands)
        to one individual Telegram Bot. Logs as event.newMessage. Default category is a
        catchall for error messages to deal with when users send a message that the client
        has not been programmed with.

        Variables:
        control - control dictionary loaded from control.yml
        Client - instance of telegram client as initialised
        '''
        
        Commands = control["B2DFlow"]["data"]["commands"]
        Callbacks = control["B2DFlow"]["data"]["callbacks"]
        Default = control["B2DFlow"]["data"]["default"]
        Client = self.BOTS["b2d"]
        
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
                        if Callbacks[data]['tag'] == 'variation':
                            buttons = None if len(Callbacks[data]["btn"]) == 0 else self.beauButtons(Callbacks[data]["btn"]) 
                            await Client.send_message(
                                entity=chat_id,
                                message='Please wait while we retrieve the product images...')
                            
                            # Paired with setup: first upload all files in setup and store ID of each of the media file in
                            # trawler.Trawler.mediaList, then retrieve here accordingly
                            ut.pLog(f"Sending Media for [{data}] to user", chat_id, chat_username)
                            # TODO swap back the declaration of media_file_names
                            # media_file_names = Callbacks[data]['media']
                            media_file_names = ["1081A051_020_SB_BT_GLB.png"]
                            
                            photo_coros = [self.__target_coro[key] for key in media_file_names if key[-4:] != '.pdf']
                            pdf_coros = [self.__target_coro[key] for key in media_file_names if key[-4:] == '.pdf']
                                                        
                            if len(photo_coros) > 0 :
                                await Client.send_file(
                                    entity=chat_id,
                                    file=photo_coros,
                                    caption=Callbacks[data]['msg']
                                )
                            if len(pdf_coros) > 0:
                                await Client.send_file(
                                    entity=chat_id,
                                    file=pdf_coros
                                )

                            if len(photo_coros) > 0 or len(pdf_coros) > 0:
                                # If any media or file has been sent at all
                                await Client.send_message(
                                    entity=chat_id,
                                    message=Callbacks[data]["msg"],
                                    buttons=buttons
                                )
                            else:
                                await Client.send_message(
                                    entity=chat_id,
                                    message=Callbacks[data]["msg"],
                                    buttons=buttons
                                )
                            ut.pLog(f"Sent media of [{data}] to user", chat_id, chat_username)

                        else:                                
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