import telegram
import telegram.ext
import os

from dotenv import load_dotenv

# Global Env Vars
load_dotenv()
API_TELE = os.environ.get('API_TELE')

class gram():
    def __init__(self):
        self.bot = telegram.Bot(API_TELE)
        self.p()

    def p(self):
        print("Printing getMe")
        blob = self.bot.get_me()
        print(blob)


# class Bot_Tele(): pass

# for i in telegram.Bot.__all__:
#     setattr(Bot_Tele, i, getattr(telegram.Bot, i))

print("Successful Bot Call")
gram()