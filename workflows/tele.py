import telegram
import telegram.ext
import os

from dotenv import load_dotenv

# Global Env Vars
load_dotenv()
API_TELE = os.environ.get('API_TELE')

class Bot_Tele():
    def __init__(self):
        self = telegram.Bot(API_TELE)

print("Successful Bot Call")
Bot_Tele()