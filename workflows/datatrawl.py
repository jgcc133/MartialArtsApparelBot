'''
Creates an instance of a class object to trawl data on product catalogue
Currently, this is a hard coded process. I.e. we decide it goes by the 'tags' and 'metadata' file,
all products are to adhere to it. In future, we may want to abstract it to control.yml
Meaning:
Through the dict that we define in control yml, it determines where the bot trawls through, or 
even what is the trawling procedure (depend on which file as metadata, etc)
One trawler to many drives

Trawler.initialPull() returns a dictionary IDs of the files, in self.pointer

if there are differences to the directory IDs, we will then initiate a full download of tags
and photos, and push a change to metadata g sheets
'''

import os
import gspread
import json
import urllib3
import pandas as pd

import google.auth.transport.urllib3

from workflows import utils as ut

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


from googleapiclient.errors import HttpError


class Trawler:
    '''
    Single Trawler Class. I.e. a trawlers instance is made up of multiple trawler
    '''
    def __init__(self, trawl_for, key_dict):

        '''
        wh stands for webhook. Every Trawler can only have one webhook (or URL endpoint, such
        as GDrive root URL)
        pan indicates the pan that we use to sieve for gold. It is the current blob of data that
        we're working on.
        vault inidicates storage. Anything once deemed of value, can be stored in self.vault

        Each Trawler has a trawling protocol
        '''
        
        self.url = key_dict["url"]
        self.trawl_for = trawl_for # By platform name / type
        self.SCOPES = key_dict["apiUse"]["scopes"]
        self.driveId = key_dict["apiUse"]["driveId"]
        self.metaId = key_dict["apiUse"]["metaId"]
        self.creds = None
        self.drive_client = None
        self.spreadsheet_client = None

        self.pointers = {}
        self.metaHeaders = {
            "Category_ID": 0,
            "Product_ID": 1,
            "Common_Media_ID": 2,
            "Variation_ID": 3,
            "Media_ID": 4,
            "Tags": 5,
            "Category": 6,
            "Product": 7,
            "Variation": 8,
            "Sizes": 9,
            "Inventory": 10
        }
        self.productTable = pd.DataFrame(columns=self.metaHeaders.keys())

        self.svcID = None
        self.svckey = None
                        
        self.setCreds()
        self.initialIDPull()
        self.metaTablePull()
        self.compareMD2Dict()


    def setCreds(self):
        ut.pLog(f"Setting Credentials for {self.trawl_for}...")
        try:
            '''
            load token from os.environ.
            If token exists with all the fields, call refresh token
            else, load credentials from os.environ
            and ask user to authenticate.
            if that fails (no credentials or credentials expired),
            then error msg and exit.

            subsequently, build the builds
            
            '''
            stored_token = os.environ.get("GOOGLE_TOKEN")
            try:
                stored_token=json.loads(stored_token)
                self.creds = Credentials(
                    token=stored_token['token'],
                    refresh_token=stored_token['refresh_token'],
                    token_uri=stored_token['token_uri'],
                    client_id=stored_token['client_id'],
                    client_secret=stored_token['client_secret'],
                    scopes=stored_token['scopes']
                )
                http = urllib3.PoolManager()
                request = google.auth.transport.urllib3.Request(http)
                self.creds.refresh(request)
            except:
                ut.pLog(f"No Token Found. Please get token from your existing Credentials")
                stored_creds=os.environ.get("GOOGLE_CREDENTIALS")
                if stored_creds != None or stored_creds != '':
                    stored_creds = json.loads(stored_creds)
                    flow = InstalledAppFlow.from_client_config(stored_creds, scopes=self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                else:
                    ut.pLog("No credentials found (Require at least 1). Please contact administrator.", p1=True)
                    return None
        
            self.drive_client = build("drive", "v3", credentials=self.creds)
            self.spreadsheet_client = gspread.authorize(self.creds)
            ut.pLog(f"Expiry for token is {self.creds.expiry}")
            ut.pLog(f"Credentials for {self.trawl_for} successfully set.", p1=True)
        except:
            ut.pLog(f"Credentials for {self.trawl_for} could not be set", p1=True)

    def initialIDPull(self):
        '''
        Initial pull method. Also to pull every single file and endpoint to display.
        Shortened form of pullFiles.
        Causes self.pointers to be filled with a dict object of ids that we can use to
        pull and download photos.
        Note: This function only returns IDs as pointers to later download the files.

        To reduce the need for complexity of GDrive structure to be listed on control.yml
        or a metadata doc, it is recommended that the folder structure is standardised at
        four levels deep:
        
        Root (For Chatbot)
        |           |           |
        Category1   Category2   Category3
        |
        Prod11___________________
        |-tags                  |
        |-media(usually PDF)    |
        Variation111            Variation112
        |-media(usually pic)    |-media(usually pic)

        '''
        ut.pLog(f"Pulling files from Drive...")
        try:
            service = self.drive_client
            cat_query = f"('{self.driveId}' in parents) and (trashed = false)"
            ut.pLog(f"Querying {self.trawl_for} with \n {cat_query}", p1=True)
            fields = 'nextPageToken, files(id, name, capabilities(canListChildren))'
            cat_response = service.files().list(q=cat_query,fields=fields).execute()
            
            # Iterate Category
            for category in cat_response.get('files', []):
                cat_name = category.get('name')
                cat_id = category.get('id')
                if category.get('capabilities')['canListChildren'] == True:
                    self.pointers[cat_name] = {
                        "id": cat_id,
                        "products":{}
                    }

                    # Iterate products
                    pro_query = f"('{cat_id}' in parents) and (trashed = false)"
                    pro_response = service.files().list(q=pro_query, fields=fields).execute()
                    for pro in pro_response.get('files', []):
                        pro_name = pro.get('name')
                        pro_id = pro.get('id')
                        if pro.get('capabilities')['canListChildren'] == True:
                            self.pointers[cat_name]["products"][pro_name] = {
                                "id": pro_id,
                                "media": {},
                                "variations": {}
                            }

                            # Iterate variations within product folders
                            var_query = f"('{pro_id}' in parents) and (trashed = false)"
                            var_response = service.files().list(q=var_query, fields=fields).execute()
                            
                            for var in var_response.get('files', []):
                                var_name = var.get('name')
                                var_id = var.get('id')
                                if var.get('capabilities')['canListChildren'] == True:
                                    # deal with as variation exists (as a folder) and need to iterate
                                    # deeper to search for IDs of photo files
                                    self.pointers[cat_name]["products"][pro_name]["variations"][var_name] = {
                                            "id": var_id,
                                            "media": {},
                                            "tags": "",
                                            "sizes": {}
                                        }                                    
                                    file_query = f"('{var_id}' in parents) and (trashed = false)"
                                    file_response = service.files().list(q=file_query, fields=fields).execute()
                                    for file in file_response.get('files', []):
                                        
                                        file_id = file.get('id')
                                        file_name = file.get('name')
                                        # deal with as photo, record tag ID if name contains tag and media if otherwhise
                                        if 'tag' in file_name.lower():
                                            self.pointers[cat_name]["products"][pro_name]["variations"][var_name]["tag"] = file_id
                                        else:
                                            self.pointers[cat_name]["products"][pro_name]["variations"][var_name]["media"][file_name] = file_id
                                else:
                                    #  Assume Product Media File, add to product media dict
                                    self.pointers[cat_name]["products"][pro_name]["media"][var_name] = var_id
            ut.logObj(self.pointers, name= f"{self.trawl_for} Pointers")
            ut.pLog(f"File and Folder IDs have been loaded from {self.trawl_for}.", p1=True)
        except:
            ut.pLog(f"Could not load file IDs from {self.trawl_for}", p1=True)

    def metaTablePull(self):
        gs_client = self.spreadsheet_client
        try:
            md_sht = gs_client.open_by_key(self.metaId)
        except PermissionError:
            ut.pLog("You have not enabled Sheets API on the Google Cloud Platform project associated with this chatbot!")
        sht = md_sht.worksheet("AAMAA")
        df = pd.DataFrame(sht.get_all_records())
        print(df)


    def compareMD2Dict(self):
        '''
        from self.pointers, each to query response get a file from G Drive (tags GSheets)
        '''
        self.pointers
        self.metaHeaders
        self.productTable

        # Try for one item
        for cat in self.pointers.keys():
            cat_ID = self.pointers[cat]['id']
            for prod in self.pointers[cat]['products'].keys():
                prod_ID = self.pointers[cat]['products'][prod]['id']

                # Product Media ID list concatenation
                common_media_IDs = ''
                for common_media in self.pointers[cat]['products'][prod]['media'].keys():
                    common_media_IDs += self.pointers[cat]['products'][prod]['media'][common_media] + ", "
                common_media_IDs = common_media_IDs[:-2]

                for var in self.pointers[cat]['products'][prod]['variations'].keys():
                    var_ID = self.pointers[cat]['products'][prod]['variations'][var]['id']

                    media_IDs = ''
                    for media in self.pointers[cat]['products'][prod]['variations'][var]['media'].keys():
                        media_IDs += self.pointers[cat]['products'][prod]['variations'][var]['media'][media] + ", "
                    media_IDs = media_IDs[:-2]

                    self.productTable.loc[len(self.productTable.index)] = [
                        cat_ID, prod_ID, common_media_IDs, var_ID, media_IDs, '' , cat, prod, var, '', 0
                    ]
        print("tabulated")
        

    


class TrawlerSet:
    '''
    Utilises Source section under control.yml to generate x number of trawlers, each with its
    own set of apiUse config depending on the keys required by the respective platforms.
    These will also be stored in the respective json objects in the env folder.
    '''
    def __init__(self, trawlset_for, trawl_url_dict):
        self.trawlset_for = trawlset_for # String name of the type of bot the trawlerset is made for (B2D, B2c, etc)
        self.trawlers = {}

        # Creating a list of trawlers
        for platform in trawl_url_dict:
            if trawl_url_dict[platform] != '':
                ut.pLog(f"Creating Trawler for {platform}...")
                try:
                    self.trawlers[platform] = Trawler(platform, trawl_url_dict[platform])
                    ut.pLog(f"Trawler created: {platform} for {self.trawlset_for}.", p1=True)
                except:
                    ut.pLog(f"Unable to create Trawler: {platform} for {self.trawlset_for}", p1=True)
    

    