from flask import Flask, request
import reply
import help_methods
import thread_settings
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import credentials
import callybot_database

app = Flask(__name__)
credential = credentials.Credentials()
db_credentials = credential.db_info
db = callybot_database.CallybotDB(db_credentials[0], db_credentials[1], db_credentials[2], db_credentials[3])
replier = reply.Reply(credential.access_token, db)
handled_timestamps = []


def init():
    thread_handler = thread_settings.ThreadSettings(credential.access_token)
    thread_handler.whitelist("https://folk.ntnu.no/halvorkmTDT4140/")
    thread_handler.set_greeting(
        "Hi there {{user_first_name}}!\nWelcome to CallyBot. Press 'Get Started' to get started!")
    thread_handler.set_get_started()
    thread_handler.set_persistent_menu()

    interrupt()


def interrupt():
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=reminder_check,
        trigger=CronTrigger(minute='0,5,10,15,20,25,30,35,40,45,50,55'),  # checking every 5th minute
        id='reminder_check',
        name='Reminder',
        replace_existing=True)
    atexit.register(lambda: scheduler.shutdown())


def reminder_check():
    # Run reminder_check
    print("Reminder trigger" + str(time.ctime()))
    current = help_methods.search_reminders(db)
    if current:
        for reminder in current:
            replier.reply(reminder[1], "Reminder: " + reminder[2], "text")
    return


@app.route('/', methods=['POST'])
def handle_incoming_messages():
    data = request.json
    global handled_timestamps
    try:
        timestamp = data['entry'][0]['time']
    except KeyError:
        print("\x1b[0;31;0mError: Could not find timestamp\x1b[0m")
        return "ok", 200
    if timestamp in handled_timestamps:
        print("\x1b[0;34;0mDuplicated message\x1b[0m")
        return 'ok', 200
    else:
        if len(handled_timestamps) > 256:
            handled_timestamps = handled_timestamps[-32:]
        handled_timestamps.append(timestamp)
    print("\n\n\n")
    print("----------------START--------------")
    print("DATA:")
    try:
        print(data)
        print("---------------END-----------------")
        user_id = data['entry'][0]['messaging'][0]['sender']['id']
    except KeyError:
        return "ok", 200
    replier.arbitrate(user_id, data)
    print("\x1b[0;32;0mok 200 for message with timestamp", timestamp, "\x1b[0m")
    return "ok", 200


@app.route('/', methods=['GET'])
def handle_verification():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if request.args['hub.verify_token'] == credential.verify_token:
            return request.args['hub.challenge'], 200
        else:
            return "Invalid verification token", 403
    return 'ok', 200


if __name__ == '__main__':
    init()
    app.run(debug=True, use_reloader=False, threaded=True)
