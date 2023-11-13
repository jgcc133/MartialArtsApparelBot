'''
Control Flow Config File
called by control.py, a control flow engine
returns a python dictionary of control flow configurations

'''


CONFIG = {
    "Auth": {"meta": "A list of keys required from os.environ",
             "data": {
                "tele":[
                    "API_TELE_BOT",
                    "API_TELE_APP_ID",
                    "API_TELE_APP_HASH"],
                "whatsapp":[]
            }
        },
    "Platforms": {"meta": "A list of platforms supported / to be loaded",
                  "data": ["tele",
                           "whatsapp"]
                  },
    "Flow":{"meta": "Control Flow config for ControlEngine to read in and generate a list of handlers and callbackquery",
            "data": {
                "commands": {
                    "/start": {
                        "msg": "Welcome to Martial Arts Apparel Bot! What services would you like to take a look at?",
                        "btn": ["Product Enquiry", "Arrange Viewing", "Other Services"]
                    },
                    "/help":{
                        "msg": "View our list of commands?",
                        "btn": ["Product Enquiry", "Arrange Viewing", "Other Services"]
                    },
                    "/call":{
                        "msg": "Speak to our sales representatives?",
                        "btn": ["Call", "Chat with Live Rep", "test1", "test2", "test3", "test4", "Back"]
                    }
                },
                "callbacks": {
                    "Product Enquiry": {
                        "msg": "Which areas of products would you like to look at today?",
                        "btn": ["MMA", "Muay Thai", "BJJ", "Other Accessories"]
                    },

                }
            }
    }
}
def main():
    return CONFIG