
'''
.workflows.tele contains all the callback handlers as a chat bot
As more chat bots get created, the logic flow will reside here,
whereas common functions like taking in a message, buttons and text,
will take the data and function call to the respective callback handlers
i.e. one main.py file to control convo flow and UI,
but the individual files to make most use of the respective chat bots
'''

import os
import asyncio
import yaml

from dotenv import load_dotenv
from workflows import utils as ut
from workflows import tele as tl
from workflows import datatrawl as dt
from workflows.control import Control


load_dotenv()
control_file = 'user/control.yml'

def main() -> None:
    ut.clearLogs()
    CONTROL = Control(control_file)
    trawler = dt.TrawlerSet(CONTROL.logic['ID'], CONTROL.logic['Source']['data'])
    with open('user/sku.yml', 'w') as sku:
        yaml.dump(trawler.trawlers['GoogleDrive'].pointers, sku)
    
    # Temporarily disabled for GDrive testing
    telegram_interface = tl.Tele(CONTROL.logic)
    

if __name__ == "__main__":
    main()