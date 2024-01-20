# MartialArtsApparelBot
## Documentation

7 Nov 23
Restarted by wiping all files

8 Nov 23
Successfully loaded .env files and settings (left out in .gitignore)
Module for telegram bot is set up.
Separate Modules for each of the bots, where main.py can call on them depending on how many are added

11 Nov 23
Created basic flow of start messages
Pending being able to call start message handler when "new query" is selected as a button. As of now, the await async coroutine causes the start message to fire off the moment any non command text is detected. Perhaps should not key in as a function but remain as button call argument

Next Steps:
Control Flow is to be abstracted OUT of the main.py or [some platform].py files. This is to allow control flow to be updated regardless of the number of chat platforms being supported

13 Nov 23
Control Flow has been abstracted. The config is now read in from control_flow.py by the respective chat platform files (tele.py, and in future others)

Next Steps:
Adding events.NewMessage handler for non-command text submitted by user, and callbackquery for button callback data

14 Nov 23
Control File completely abstracted and converted to yaml file

Next Steps:
Host using GitHub Actions, and HTTP Get request to pull info from google drive (test with personal)

9 Dec 23
Use google drive url api to pull data from google drive. Provided data there is public to all.

12 Dec 23
After discussion with Verne, there are a few big pieces that we can tackle in phases for the next quarter:
1) Connectivity to Google Drive (code and data in the correct file structure)
2) Web hosting of code (Python Anywhere? Microsoft Azure? Google Cloud?)
3) Chatbot Search function enhancement

The structure of google drive will be:
Root/
    - Category 1/
        - Product 11/
            - Tags sheets file
            - Media1(catalog pdfs)
            - Variations 111/
                - Media (pictures) : Mediafile ID


Step 1:
abstract load dotenv and control.yml to 

22 Dec 23:
Completed Abstraction of Tele into a class of handler creators to interface with control.yml
Forked gdrive manual to attempt building a TrawlSet and Trawler class, which should also interface with control.yml to get the credentials and talk to each respective storage management platforms.
Next steps: understand and build OAuth 2.0 for service account APIs

28 Dec 23:
Completed Auth with GDrive, OAuth2.0 Able to pull files with url
Able to distinguish between folder or file with file(Capabilities(canListChildren))

Next Steps: Query two layer deep folders and store the IDs in Trawler.pointers or Trawler.payloads
Next steps: Merge back to main, then add in long term logging (add timestamp and save to log.yml)
Next Steps: Post the data (pictures, with text / tags) back to telegram

29 Dec 23:
2-Layer deep folders queried and stored in Trawler.pointers

31 Dec 23:
Completed Query to GDrive and Logging

Next Steps: Google Apps Script with triggers set on G Cloud projects, to trawl and update to metadata Gsheets
(Note: G Sheets metadata is potentially just a interim repo for Biz content management. In steady state if these files hosted on a server can be the DB for the mgmt, then G sheets metadata, as well as occasional backup of logs will remain)

3 Jan 24:
Started work on Google Drive Google Apps Script. However it seems redundant to reproduce the exact same trawler just existing on GDrive. Also, there are no GAS triggers that can listen to changes in folder structure (when SKUs are added, deleted, or shifted, or catalog media is added). Hence, the GAS code behaviour will also consist of time-based querying. We should use it instead as a backup process (i.e. In addition to the data being saved in metadata GSheets as a backup to data files stored together with this code, Apps Script queries once every week to store that in GSheets and our servers for a lower level backup)
Recommend for tags to be in google sheets rather than docs (not yml friendly)
Tags in column A, Columns B to D are variation, sizes and stock

next steps: gspread to pull all tags files, pulling the tags within, to 2) populate a metadata file, which will then 3) be used to check against 4a) pulled metadata file from root, and then update metadata file accordingly

4 Jan 24:
Trawler.initialPull() complete.
Pulls in all file and folder IDs

Tags should be done at metadata level. Reason being: while client may be carrying the same set of SKUs (category - product - variation - size), he may be adding to SEO list only (changing tags BUT not changing variations offered)

Tags handling:
Tags should be added to a set (to ensure unique, Case Sensitive keywords), then concatenated to a list of words, delimted with ", ". In the case when pulling the algo realises there are a difference in tags, a union of both 1) metadata tags column and 2) tags column in variation tags Gsheets is to be retained AND synchronised
Next steps: How do we then delete tags? (It has to be by function, either on G Sheets. Clear from metadata / variations Gsheets and then slowly add back by the same function)
Pending Verne's reply

Potential steps:
SKU data object would include (from metadata)
Category_ID	Product_ID	Common_Media_ID	Variation_ID	Media_ID	Tags	Category	Product	Variation	Sizes	Inventory
but also:
media files
other purchase related fields such as
supplier, MOQ, purchase history, etc
other hidden methods to push data to update meta data