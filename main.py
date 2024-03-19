
'''
.workflows.tele contains all the callback handlers as a chat bot
As more chat bots get created, the logic flow will reside here,
whereas common functions like taking in a message, buttons and text,
will take the data and function call to the respective callback handlers
i.e. one main.py file to control convo flow and UI,
but the individual files to make most use of the respective chat bots
'''

import yaml

from dotenv import load_dotenv
from fastapi import FastAPI
from workflows import utils as ut
from workflows import tele as tl
from workflows import datatrawl as dt
from workflows.control import Control


load_dotenv()
control_file = 'user/control.yml'

def main():
    global trawler, telegram_interface
    ut.clearLogs()
    CONTROL = Control(control_file)
    trawler = dt.TrawlerSet(CONTROL.logic['ID'], CONTROL.logic['Source']['data'])
    with open('user/sku.yml', 'w') as sku:
        yaml.dump(trawler.trawlers['GoogleDrive'].pointers, sku)
    
    # Temporarily disabled for GDrive testing
    telegram_interface = tl.Tele(CONTROL.logic)
    return trawler, telegram_interface

    
trawler, telegram_interface = main()
app = FastAPI()

@app.get("/")
def display():
    pass

@app.get("/api/v1/products/json")
async def displayProducts(trawl_cache = trawler):    
    return trawl_cache.trawlers['GoogleDrive'].pointers

@app.get("/api/v1/products/table")
async def displayProducts(trawl_cache = trawler):    
    return trawl_cache.trawlers['GoogleDrive'].productTable