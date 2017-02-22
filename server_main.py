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
VERIFY_TOKEN = "secret"
replier=reply.Reply(ACCESS_TOKEN)
#WTF

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
    data = request.get_json()
    print("----------------START--------------")
    print("DATA:")
    print(data)
    print("---------------END-----------------")
    user_id = data['entry'][0]['messaging'][0]['sender']['id']
    replier.arbitrate(user_id,data)

    return "ok"


@app.route('/', methods=['GET'])
def handle_verification():
    if request.args['hub.verify_token'] == VERIFY_TOKEN:
        return request.args['hub.challenge']
    else:
        return "Invalid verification token"


if __name__=='__main__':
    init()
    app.run(debug=True,use_reloader=False,threaded=True)
