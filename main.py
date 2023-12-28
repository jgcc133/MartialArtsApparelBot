
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
    try:
        with open(control_file, 'r') as file:
            control = yaml.safe_load(file)            
        ut.pLog(f"Control has been loaded from {control_file}")
        return control
    except:
        ut.pLog(f"Unable to load control flow from {control_file}")

def main():
    
    CONTROL = loadControl()    
    # trawler = dt.Trawler("https://docs.google.com/spreadsheets/d/1wQ-Z7mAVcpHC1p4DdcBs1sD_ipkC6lGqohOOzpa28Ls/edit#gid=0").accessHTTP()
    # ut.pObj(trawler.accessHTTP())
    
    
    # Temporarily disabled for GDrive testing
    # telegram_interface = tl.Tele(CONTROL)
    
    trawler = dt.TrawlerSet(CONTROL['ID'], CONTROL['Source']['data'])

    

main()