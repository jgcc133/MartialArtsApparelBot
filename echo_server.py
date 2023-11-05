from flask import Flask, request
import requests
import json

APITele = "6630257115:AAENE0cRzBtwlmfD2j22X_JvrzL2YDXcnW8"
URLTele = f"https://api.telegram.org/bot{APITele}/"

app = Flask(__name__)

URLWebhook = "https://martialartsapparelbot.free.beeceptor.com"
# Deployed first time

def setWebhook(URLWebhook: str = URLWebhook):
    webhook_is_set = getWebhook()
    if not webhook_is_set:
        webhook_post = requests.post(URLTele + f"setWebhook?url={URLWebhook}")    

@app.route('/getWebHookInfo')
def getWebhook():
    webhook_response = requests.get(URLTele + "getWebhookInfo")
    payload = json.loads(webhook_response.text)
    URLWebhook = payload["result"]["url"]        
    return False if URLWebhook == "" else URLWebhook

setWebhook()