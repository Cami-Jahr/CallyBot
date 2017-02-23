from flask import Flask, request
import requests
import reply
import help_methods
import thread_settings
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

app = Flask(__name__)

ACCESS_TOKEN = "EAAZANSkaEgg8BADeaog9sCdpujr2lwhwdHSMNa6Ug5zpgJkpScGZCTOdDZAjD2XNbqfKGjZAxHoJZCddEjvkeRQ37dHm1qAGVAZCX3D52CZA6fc8VSx6qenZCZCerEoScLztn6EXqNwiVPWaVB2iX0YOrsV9RL790mAZByefL5ocrfYwZDZD" 
#ACCESS_TOKEN =" EAAZANSkaEgg8BAN1QsZAcGCWPLMk3SGttzfZANVh2JRkYnnYudat4ODHc8f3K3CQl7n4n103cLCaImGsj3tCmOiXNYbUza4EQufM64FZAZArnzEh8MHRnTE12eCtrnaZCyMNC4ZC1lVWmxGYK76iZBxz1yeWd21ucOBehpY45OraPwZDZD" #2
VERIFY_TOKEN = "verifytoken"
replier=reply.Reply(ACCESS_TOKEN)
seqnumbers=[]

def init():
    thread_handler=thread_settings.Thread_Settings(ACCESS_TOKEN)
    thread_handler.whitelist("https://folk.ntnu.no/halvorkmTDT4140/")
    thread_handler.set_greeting("Hi there {{user_first_name}}!\nWelcome to CallyBot. Press 'Get Started' to get started!")
    thread_handler.set_get_started()
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=test,
        trigger=IntervalTrigger(seconds=60),
        id='printing_job',
        name='Print test',
        replace_existing=True)
    atexit.register(lambda: scheduler.shutdown())
    

def test():
    print("Funker fortsatt:",time.ctime())

@app.route('/', methods=['POST'])
def handle_incoming_messages():
    data = request.json
    if 'message' not in data['entry'][0]['messaging'][0]:
        return 'ok', 200
    global seqnumbers
    seq=data['entry'][0]['messaging'][0]['message']['seq']
    if seq in seqnumbers:
        print("Duplicated message")
        return 'ok', 200
    else:
        if len(seqnumbers)>100: seqnumbers=[]
        seqnumbers.append(seq)

    print()
    print("----------------START--------------")
    print("DATA:")
    print(data)
    print("---------------END-----------------")
    user_id = data['entry'][0]['messaging'][0]['sender']['id']
    replier.arbitrate(user_id,data)
    print("Everything is good in the good")
    return "ok", 200


@app.route('/', methods=['GET'])
def handle_verification():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if request.args['hub.verify_token'] == VERIFY_TOKEN:
            return request.args['hub.challenge'], 200
        else:
            return "Invalid verification token", 403
    return 'ok', 200

if __name__=='__main__':
    init()
    app.run(debug=True,use_reloader=False,threaded=True)
