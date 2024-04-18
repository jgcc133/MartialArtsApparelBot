
'''
.workflows.tele contains all the callback handlers as a chat bot
As more chat bots get created, the logic flow will reside here,
whereas common functions like taking in a message, buttons and text,
will take the data and function call to the respective callback handlers
i.e. one main.py file to control convo flow and UI,
but the individual files to make most use of the respective chat bots
'''

import yaml
import json
import uvicorn
import asyncio
import time

from dotenv import load_dotenv
from fastapi import FastAPI
from workflows import utils as ut
from workflows import tele as tl
from workflows import datatrawl as dt
from workflows.control import Control

load_dotenv()
control_file = 'user/control.yml'
control, trawler, telegram_interface = None, None, None

app = FastAPI()

@app.get("/")
async def display():
    return 200

@app.get("/api/v1/products/json")
async def displayProducts():    
    return trawler.trawlers['GoogleDrive'].pointers

@app.get("/api/v1/products/table")
async def displayProducts():    
    return list(trawler.trawlers['GoogleDrive'].productTable)

@app.get("/api/v1/products/{query_type}")
async def queryVariations(query_type: str = 'filter', q: str ='all'):
    full_product_list = None
    if query_type == 'filter':
        # return a list of products (min 0) that fit the tuple string fed in, with
        # filter?q=[%5B%28%27Handwraps%27%2C+%27Prize+Ri...
        if q == 'all':
            # call display all function from data trawler
            full_product_list, errors = trawler.trawlers['GoogleDrive'].getMediaFiles()                
        else:
            # parse tuple, and call display based on the tuples
            try:
                # identifier = {'categories':['Handwraps'],'products':['Prize Ring', 'Asics Matflex 7 Shoes'], 'variations': 'Black'}
                query = ut.extractObjFromURL(q)
                full_product_list, errors = trawler.trawlers['GoogleDrive'].getMediaFiles(query)
                print([e.args for e in errors])
            except:
                raise ValueError
    elif query_type == 'id':
        # return specifc products with given id?q=...
        # parse tuple and call display based on the tuple
        pass

    else:
        # return all as well
        # call display all function from data trawler
            pass
    return full_product_list

async def main(control, trawler, telegram_interface):    
    ut.clearLogs()
    # One round of update
    control = Control(control_file)
    trawler = dt.TrawlerSet(control.logic['ID'], control.logic['Source']['data'])

    # dump log pointers
    with open('user/sku.yml', 'w') as sku:
        yaml.dump(trawler.trawlers['GoogleDrive'].pointers, sku)
    
    # after trawler is set up, Control.update should be called to update control and
    # periodically listen for updates and synchronise between telegram and trawler
    # trawler is a periodic, completable cycle, whereas tele is a persistent, run till
    # updated or disconnected process

    control.update(trawler)
    with open(control_file, 'w') as file:
        yaml.dump(control.logic, file)

    # initialise settings for telegram chat bot
    telegram_interface = tl.Tele(control.logic)
    await telegram_interface.BOTS['b2d'].start(bot_token=telegram_interface.APIS['b2d'])
    await run_uvicorn(app)
       

async def update(control, trawler, telegram_interface):
    # time.sleep(30)
    trawler.trawlers['GoogleDrive'].update()
    control.update(trawler)
    with open(control_file, 'w') as file:
        yaml.dump(control.logic, file)


async def run_uvicorn(app, host='127.0.0.1', port=8000):
    config = uvicorn.Config(app=app, port=port, host=host)
    server = uvicorn.Server(config)
    await server.serve()

async def tasks():
    await asyncio.gather(
        await main(control=control,
                   trawler=trawler,
                   telegram_interface=telegram_interface)
        # await telegram_interface.BOTS['b2d'].run_until_disconnected()
                     )

if __name__=="__main__":
    asyncio.run(tasks())
                     
   