from flask import Flask, request
from collections import namedtuple

APITele = "6630257115:AAENE0cRzBtwlmfD2j22X_JvrzL2YDXcnW8"
URLTele = f"https://api.telegram.org/bot${APITele}/"

app = Flask(__name__)

URLWebhook = ""
SetWebhook_str = URLTele + f"setWebhook?url=${URLWebhook}"

@app.route('/')

def index():
    return f"<h1>Home Page</h1>"

@app.route('/api')
def api():
    user_input = request.args.get('input')
    response = generate_response(user_input)

    response_JSON = {
        'input': user_input,
        'response': response.response,
        'accuracy': response.accuracy
    }
    return response_JSON

Response = namedtuple('Response', 'response accuracy')

def generate_response(user_input: str) -> Response:
    lc_input = user_input.strip().lower()

    if lc_input == "hello":
        return Response("Hello There!", 1)
    elif lc_input == "goodbye":
        return Response("See you later!", 1)
    else:
        return Response("Could not understand.", 0)

def send_diagnostics():
    pass

if __name__ == '__main__':
    app.run()