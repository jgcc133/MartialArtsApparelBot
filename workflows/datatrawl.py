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
import dotenv
import requests
import io

import google.auth.transport.urllib3

from workflows import utils as ut

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload




class Trawler:
    '''
    Single Trawler Class. I.e. a trawlers instance is made up of multiple trawler
    '''
    def __init__(self, trawl_for, key_dict):

        '''
        Initialise Trawler

        Variables:
        trawl_for: string = ['GoogleDrive']
        key_dict: dict = <control dict loaded from control.yml>
        
        returns an instance of a Trawler, with .productTable, .mediaList, .uiTable set
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
        self.metaIdentifier = {
            "category": None,
            "product": None,
            "variation": None,
            "size": None,
            "serial": None,
            "tags": [],
            "product_media_IDs": [],
            "variation_media_IDs": [],
            "product_media": {},
            "variation_media": {}
        }
        self.metaQuery = {
            "categories": [],
            "products": [],
            "variations": [],
            "sizes": [],
            "serial": [],
            "tags": []
        }
        self.__breadcrumbs = {'categories': {},
                              'products': {},
                              'variations': {},
                              'sizes': {}}
        
        self._media_storage_location = key_dict["storage"]
        self.mediaList = {}
                        
        self.setCreds()
        self.idPull() # Add download_media=True when deployed

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
                params = {
                    "grant_type": "refresh_token",
                    "client_id": self.creds.client_id,
                    "client_secret": self.creds.client_secret,
                    "refresh_token": self.creds.refresh_token
                }
                authorization_url = "https://oauth2.googleapis.com/token"
                r = requests.post(authorization_url, data=params)
                response_body = r.json()
                self.creds.token = response_body['access_token']                
                dotenv.set_key(".env", "GOOGLE_TOKEN", self.creds.to_json())
            except:
                ut.pLog(f"No Token Found. Please get token from your existing Credentials")
                stored_creds=os.environ.get("GOOGLE_CREDENTIALS")
                if stored_creds != None or stored_creds != '':
                    stored_creds = json.loads(stored_creds)
                    flow = InstalledAppFlow.from_client_config(stored_creds, scopes=self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                    dotenv.set_key(".env", "GOOGLE_TOKEN", self.creds.to_json())
                else:
                    ut.pLog("No credentials found (Require at least 1). Please contact administrator.", p1=True)
                    return None
        
            self.drive_client = build("drive", "v3", credentials=self.creds)
            self.spreadsheet_client = gspread.authorize(self.creds)
            ut.pLog(f"Expiry for token is {self.creds.expiry}")
            ut.pLog(f"Credentials for {self.trawl_for} successfully set.", p1=True)
        except:
            ut.pLog(f"Credentials for {self.trawl_for} could not be set", p1=True)
        
        return self.creds

    def idPull(self, download_media=False):
        '''
        Initial pull of IDs.
        
        Also to pull every single file and endpoint to display.
        Based on self.url as base root GDrive folder url, pulls and populates productTable

        returns .pointers
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
            ut.pLog(f"Querying {self.trawl_for} with \t {cat_query}", p1=True)
            fields = 'nextPageToken, files(id, name, webContentLink, capabilities(canListChildren))'
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
                    self.__breadcrumbs['categories'][cat_name] = ''

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
                            self.__breadcrumbs['products'][pro_name] = {'category': cat_name}

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
                                            "tags": [],
                                            "sizes": {}
                                        }
                                    self.__breadcrumbs['variations'][var_name] = {'category': cat_name, 'product': pro_name}                                   
                                    file_query = f"('{var_id}' in parents) and (trashed = false)"
                                    file_response = service.files().list(q=file_query, fields=fields).execute()
                                    for file in file_response.get('files', []):
                                        
                                        file_id = file.get('id')
                                        file_name = file.get('name')
                                        # deal with as variation photo, record tag ID if name contains tag and media if otherwhise
                                        self.pointers[cat_name]["products"][pro_name]["variations"][var_name]["media"][file_name] = file_id
                                        self.mediaList[file_name] = {'storage': self._media_storage_location + file_name,
                                                                     'googleID': file_id,
                                                                     'googleURL': file.get('webContentLink')}
                                        if download_media: self.__download(file)
                                else:
                                    #  Assume Product Media File, add to product media dict
                                    self.pointers[cat_name]["products"][pro_name]["media"][var_name] = var_id
                                    self.mediaList[var_name] = {'storage': self._media_storage_location + var_name,
                                                                     'googleID': var_id,
                                                                     'googleURL': var.get('webContentLink')}
                                    if download_media: self.__download(var)
            ut.logObj(self.pointers, name= f"{self.trawl_for} Pointers")
            ut.logObj(self.mediaList, name=f"{self.trawl_for} Media List")
            ut.pLog(f"File and Folder IDs have been loaded from {self.trawl_for}.", p1=True)
        except:
            ut.pLog(f"Could not load file IDs from {self.trawl_for}", p1=True)

        return self.pointers

    def __download(self, dict_):
        service = self.drive_client
        request = service.files().get_media(fileId=dict_['id'])
        fh = io.FileIO(self._media_storage_location + dict_['name'], mode='wb')
        downloader = MediaIoBaseDownload(fh, request, chunksize=1024*1024)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

    def metaTablePull(self):
        gs_client = self.spreadsheet_client
        try:
            md_sht = gs_client.open_by_key(self.metaId)
        except PermissionError:
            ut.pLog("You have not enabled Sheets API on the Google Cloud Platform project associated with this chatbot!")
        sht = md_sht.worksheet("AAMAA")
        self.productTable = pd.DataFrame(sht.get_all_records())
        return self.productTable
    
    def getCategories(self):
        return self.__breadcrumbs['categories'].keys()

    def getProducts(self):        
        return self.__breadcrumbs['products'].keys()
        
    def getVariations(self):
        return self.__breadcrumbs['variations'].keys()
    
    def __getMediaFile(self, identifier: dict):
        """
        Internal method: dicitionaries passed in must have all fields. Returnes an object:
        product_media_IDs, variation_media_IDs, product_media, variation_media        
        
        Variables:
        identifier: dictionary obj. Format:
        {'category' : str or None,
         'product'  : str or None,
         'variation': str or None,
         'size'     : str or None,
         'serial'   : str or None}
        to one of the getCategories, then getProducts, getVariations to check if it's even valid
        """
        product_dict = dict(self.metaIdentifier)

        # Checks
        if len(identifier) > 0:
            for key, value in identifier.items():
                if key not in self.metaIdentifier.keys():
                    raise KeyError(f"{identifier} contains the key {key} which is not one of the keys in the query identifier: {self.metaIdentifier}")
            cate, prod, vari = identifier.get('category', None), identifier.get('product', None), identifier.get('variation', None)
            try:                
                if cate is not None and prod is not None and vari is not None:
                    cat_, pro_, var_ = self.pointers[cate], self.pointers[cate]['products'][prod], self.pointers[cate]['products'][prod]['variations'][vari]
                    var_med_id, pro_med_id = var_['media'], pro_['media']
                    var_med, pro_med = product_dict['variation_media'], product_dict['product_media']
                    product_dict['category'], product_dict['product'], product_dict['variation'] = cate, prod, vari
                    product_dict['tags'] = var_['tags']
                    for k,v in pro_med_id.items():
                        with open(self._media_storage_location + k, 'rb') as media:
                            pro_med[k] = media
                    product_dict['product_media_IDs'] = pro_med_id
                    for k  in var_med_id.keys():
                        with open(self._media_storage_location + k, 'rb') as media:
                            var_med[k] = media
                    product_dict['variation_media_IDs'] = var_med_id
                else:
                    fields = ''
                    if cat_ is None: fields += 'category, '
                    if pro_ is None: fields += 'product, '
                    if var_ is None: fields += 'variations'
                    raise ValueError(f"Missing one or more argument value for {fields}")
            except Exception as e:
                print(e.args)
        else:
            raise ValueError('No parameter passed in as identifier!')
        return product_dict
    
    def getMediaFiles(self, query: dict = None):
        """
        Similar to getMediaFile, but allows uncertainty (does one round of error checking)
        before sending the dict identifier into self.__getMediaFile(identifier). Assumption is that
        the lowest unit with unique media is at variation (not size or serial)
        
        Variables:
        perfect(or imperfect) identifier dict
        
        returns product_dict (chained with __getMediaFile)"""

        repeat_categories, repeat_products = set(), set()
        errors, product_list = [], []

        map_query = dict(self.metaQuery)
        if query is None:
            query = map_query
            category_query = list(self.__breadcrumbs['categories'].keys())
            product_query = list(self.__breadcrumbs['products'].keys())
            variation_query = list(self.__breadcrumbs['variations'].keys())
        else:
            for k, v in query.items():
                if not isinstance(v, list):
                    map_query[k] = [v]
                else:
                    map_query[k] = v
            query = map_query
            category_query, product_query, variation_query = query['categories'], query['products'], query['variations']
        
        # Check if variations exist (start bottom up)
        if len(variation_query) > 0:
            for var_ in variation_query:
                if var_ in self.__breadcrumbs['variations'].keys():
                    cat_, pro_ = self.__breadcrumbs['variations'][var_]['category'], self.__breadcrumbs['variations'][var_]['product']
                    product_list.append({'category': cat_, 'product': pro_, 'variation': var_})
                    repeat_products.update([pro_])
                    repeat_categories.update([cat_])
                else:
                    errors.append(ValueError(f"{var_} is not found in variation list!"))
        if len(product_query) > 0:
            for pro_ in product_query:
                if pro_ in self.__breadcrumbs['products'].keys():
                    if pro_ not in repeat_products:
                        cat_ = self.__breadcrumbs['products'][pro_]['category']
                        for var_ in self.pointers[cat_]['products'][pro_]['variations'].keys():
                            product_list.append({'category': cat_, 'product': pro_, 'variation': var_})
                            repeat_categories.update([cat_])
                else:
                    errors.append(ValueError(f"{pro_} not found in product list!"))
        if len(category_query) > 0:
            for cat_ in category_query:
                if cat_ in self.__breadcrumbs['categories'].keys():
                    if cat_ not in repeat_categories:
                        for pro_, pro_v in self.pointers[cat_]['products'].items():
                            for var_ in pro_v['variations'].keys():
                                product_list.append({'category': cat_, 'product': pro_, 'variation': var_})
                else:
                    errors.append(ValueError(f"{cat_} not found in category list!"))

        media = []
        for product in product_list:
            media.append(self.__getMediaFile(product))
        
        return media, errors
    
    def update(self):
        """
        Re run ID pull. If there are differences, compare changes
        get new tree / re-initialise whole trawler"""
        ut.pLog(f"Updating Trawler.pointers from {self.trawl_for}")
        new_tree = self.idPull()
        print(self.pointers == new_tree)
        return

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
    

    