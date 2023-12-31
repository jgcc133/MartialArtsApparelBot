'''
Creates an instance of a class object to trawl data on product catalogue
Currently, this is a hard coded process. I.e. we decide it goes by the 'tags' and 'metadata' file,
all products are to adhere to it. In future, we may want to abstract it to control.yml
Meaning:
Through the dict that we define in control yml, it determines where the bot trawls through, or 
even what is the trawling procedure (depend on which file as metadata, etc)
One trawler to many drives
'''

import os
import io
import requests

from workflows import utils as ut

from google.auth.transport.requests import Request
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
        self.cred_loc = key_dict["apiUse"]["credLoc"]
        self.token_loc = key_dict["apiUse"]["tokenLoc"]
        self.driveId = key_dict["apiUse"]["driveId"]
        self.creds = None
        self.pointers = {}
        self.payload = {}

        self.svcID = None
        self.svckey = None

        self.setCreds()
        self.initialPull()
        # self.pullFiles(by_keyword=True, keywords=["metadata", "meta"])

    def setCreds(self):
        ut.pLog(f"Setting Credentials for {self.trawl_for}...")
        try:
            if self.token_loc is None or self.token_loc != '':
                self.token_loc = f"env/{self.trawl_for}Token.json"
            if os.path.exists(self.token_loc):
                ut.pLog(f"Using Token from {self.token_loc}...")
                self.creds = Credentials.from_authorized_user_file(self.token_loc, self.SCOPES)
            else:
                '''
                token_loc filepath has not been set,
                token.json has not been created, or
                credentials are no longer valid
                '''
                if not self.creds or not self.creds.valid:
                    if self.creds and self.creds.expired and self.creds.refresh_token:
                        self.creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.cred_loc, self.SCOPES)
                        self.creds = flow.run_local_server(port=0)
                    # Save the credentials for the next run
                    with open(self.token_loc, "w") as token:
                        token.write(self.creds.to_json())
            ut.pLog(f"Credentials for {self.trawl_for} successfully set.", p1=True)
        except:
            ut.pLog(f"Credentials for {self.trawl_for} could not be set", p1=True)

    def initialPull(self):
        '''
        Initial pull method. Also to pull every single file and endpoint to display.
        Shortened form of pullFiles.
        Causes self.pointers to be filled with a dict object of ids that we can use to
        pull and download photos
        '''
        ut.pLog(f"Pulling files from Drive...")
        try:
            service = build("drive", "v3", credentials=self.creds)
            cat_query = f"('{self.driveId}' in parents) and (trashed = false)"
            ut.pLog(f"Querying {self.trawl_for} with \n {cat_query}")
            cat_page_token = None
            cat_response = service.files().list(q=cat_query,
                                            fields='nextPageToken, files(id, name, capabilities(canListChildren))').execute()
            
            while True:                
                for category in cat_response.get('files', []):
                    cat_name = category.get('name')
                    cat_id = category.get('id')
                    ut.pLog(f"Found file : {cat_name} (id: {cat_id})")
                    if category.get('capabilities')['canListChildren'] == True:
                        self.pointers[cat_name] = {
                            "id": cat_id,
                            "sku":{}
                        }
                        sku_page_token = None
                        sku_query = f"('{cat_id}' in parents) and (trashed = false)"
                        sku_response = service.files().list(q=sku_query,
                                            fields='nextPageToken, files(id, name, capabilities(canListChildren))').execute()
                        while True:
                            for sku in sku_response.get('files', []):
                                sku_name = sku.get('name')
                                sku_id = sku.get('id')
                                if sku.get('capabilities')['canListChildren'] == True:
                                    self.pointers[cat_name]["sku"][sku_name] = {
                                        "id": sku_id,
                                        "tags": [],
                                        "photos": {}
                                    }
                            sku_page_token = sku_response.get('nextPageToken', None)
                            if sku_page_token is None:
                                break
                cat_page_token = cat_response.get('nextPageToken', None)
                if cat_page_token is None:
                    break                

            ut.pObj(self.pointers, p1 = True)
           
        except:
            ut.pLog(f"Could not load files from {self.trawl_for}", p1=True)

    def pullFiles(self, by_keyword=False, keywords=[]):
        '''
        To reduce the need for complexity of GDrive structure to be listed on control.yml
        or a metadata doc, it is recommended that the folder structure is two levels deep
        Root (For Chatbot)
        |           |           |
        Category1   Category2   Category3
        |       |
        SKU11   SKU12
        |-text
        |-pictures

        If by_keyword is set to true, then keywords act as an additional filter.
        If we don't want to re-organise everything into a common Root 'For Chatbot' folder,
        Then the url supplied can be to AA's root folder.
        Both the folders' with names that match keyword, and pics with names that match keyword,
        will be added to the list, in an OR set.
        '''
        ut.pLog(f"Pulling files from Drive...")
        try:
            service = build("drive", "v3", credentials=self.creds)
            if by_keyword and len(keywords)!=0:
                query = f"('{self.driveId}' in parents) and (trashed = false) and ((name contains "
                query += f"'{keywords[0]}')"
                if len(keywords) > 1:
                    for kw in keywords[1:]:
                        query += f" or (name contains '{kw}')"
                query += ")"
            else:
                query = f"('{self.driveId}' in parents) and (trashed = false)"
            ut.pLog(f"Querying {self.trawl_for} with \n {query}")
            page_token = None
            response = service.files().list(q=query,
                                            fields='nextPageToken, files(id, name, capabilities(canListChildren))').execute()
            
            # ut.pObj(response) # For Devt Only
            while True:                
                for category in response.get('files', []):
                    ut.pLog(f"Found file : {category.get('name')} (id: {category.get('id')})")
                    if category.get('capabilities')['canListChildren'] == True:
                        self.pointers[category.get('name')] = {
                            "id": category.get('id'),
                            "sku":{}
                        }
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break            
            ut.logObj(self.pointers, name=f"{self.trawl_for}Pointers")


            '''
            Iterates a second round with query, to catch all folders under category folders
            '''

        except:
            ut.pLog(f"Could not load files from {self.trawl_for}", p1=True)


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
    

    