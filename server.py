from flask import Flask, request
import requests

app = Flask(__name__)

ACCESS_TOKEN = "EAAZANSkaEgg8BADeaog9sCdpujr2lwhwdHSMNa6Ug5zpgJkpScGZCTOdDZAjD2XNbqfKGjZAxHoJZCddEjvkeRQ37dHm1qAGVAZCX3D52CZA6fc8VSx6qenZCZCerEoScLztn6EXqNwiVPWaVB2iX0YOrsV9RL790mAZByefL5ocrfYwZDZD" 
VERIFY_TOKEN = "secret"

def reply(user_id, msg):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    resp = requests.post("https://graph.facebook.com/v2.8/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    print(resp.content)


@app.route('/', methods=['GET'])
def handle_verification():
    if request.args['hub.verify_token'] == VERIFY_TOKEN:
        return request.args['hub.challenge']
    else:
        return "Invalid verification token"


@app.route('/', methods=['POST'])
def handle_incoming_messages():
    data = request.json
    print("----------------START--------------")
    print(data)
    print("---------------END-----------------")
    sender = data['entry'][0]['messaging'][0]['sender']['id']
    try:
        emoji=data['entry'][0]['messaging'][0]['message']['attachments'][0]['payload']['url']
        if emoji=="https://scontent.xx.fbcdn.net/v/t39.1997-6/851557_369239266556155_759568595_n.png?_nc_ad=z-m&oh=b8d4a7e477ea566b5bf04cd2fb6c1bc4&oe=58A0C7DC":
            message="Takk for tommel opp, her er min favoritt sang:\nhttps://www.youtube.com/results?search_query=chicken+attack+song"
    except:
        try:
            message = data['entry'][0]['messaging'][0]['message']['text']
            message= "Din melding var: "+message+"! ( ͡° ͜ʖ ͡°) "
        except KeyError:
            message="Ikke bruk emojies pls"
    reply(sender, message)

    return "ok"


if __name__ == '__main__':
    app.run(debug=True)

