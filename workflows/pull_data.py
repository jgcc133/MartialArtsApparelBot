'''
In this file, we expect to pull the data to populate the chat.
However, because this is tailored to each client and how they structure their data,
this file shall be on a per-client basis.

In this current example, our client has stored the data in google drive, with pictures and
product data to be pulled. However, it is this projects' wish to not host code on Google platforms
(Due to their instability and slowness in loading). Hence we will develop our environment
as if we were hosted on AWS or Azure, interfacing with Google Drive.

is suposed to give:
a directory table of urls to check, consisting of:


and pull all files with 'catalogue' in their name
'''

import requests
import yaml

from workflows import tele
from workflows import utils as ut

# Pull data from control.yml for google drive url
def pull():
    

repo_url = tele.loadControl()['Source']['data']['url']
ut.pLog("repo_url")


# Get Request to pull metadata file (google sheets)
# Based on Google sheets filepaths, load either all or filter and then load filtered
# Go to individual list of folders and pull out relevant information