
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


load_dotenv()
control_file = 'workflows/control.yml'

def loadControl(control_file = 'workflows/control.yml'):
    '''
    Loads control flow from control file (yml file) into the global const CONTROL
    '''    
    ut.pLog(f"Loading Control from {control_file}...")
    try:
        with open(control_file, 'r') as file:
            control = yaml.safe_load(file)            
        ut.pLog(f"Control has been loaded from {control_file}", p1=True)
        ut.logObj(control, "Control")
        return control
    except:
        ut.pLog(f"Unable to load control flow from {control_file}", p1=True)

def main():
    ut.clearLogs()
    CONTROL = loadControl()
    trawler = dt.TrawlerSet(CONTROL['ID'], CONTROL['Source']['data'])
    
    
    # Temporarily disabled for GDrive testing
    # telegram_interface = tl.Tele(CONTROL)
    

    

main()