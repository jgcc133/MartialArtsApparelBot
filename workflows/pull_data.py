'''
In this file, we expect to pull the data to populate the chat.
However, because this is tailored to each client and how they structure their data,
this file shall be on a per-client basis.

In this current example, our client has stored the data in google drive, with pictures and
product data to be pulled. However, it is this projects' wish to not host code on Google platforms
(Due to their instability and slowness in loading). Hence we will develop our environment
as if we were hosted on AWS or Azure, interfacing with Google Drive.

  data:
    base_url: some url (Activeapparels)
    alt_url:
      - url1
      - url2

    base_dir: root
    alt_dir:
      - dir1
      - dir2


is suposed to give:
a directory table of urls to check, consisting of:

            base_url        url1        url2
base_dir    base_url/       url1/       url2/
dir1        base_url/dir1   url1/dir1   url2/dir1
dir2        base_url/dir2   url1/dir2   url2/dir2

and pull all files with 'catalogue' in their name
'''