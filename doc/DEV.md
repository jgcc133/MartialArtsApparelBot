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