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
        - SKU 11/
            - Tags Text file
            - Photo1
            - Photo2
            - etc
        - SKU 12/
            - Tags Text file
            - Photo1

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