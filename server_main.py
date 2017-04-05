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
from datetime import datetime

app = Flask(__name__)
credential = credentials.Credentials()
db_credentials = credential.db_info
db = callybot_database.CallybotDB(db_credentials[0], db_credentials[1], db_credentials[2], db_credentials[3])
replier = reply.Reply(credential.access_token, db)
received_message = []


def init():
    interrupt()
    clear_old_reminders()
    thread_handler = thread_settings.ThreadSettings(credential.access_token)
    thread_handler.whitelist("https://folk.ntnu.no/halvorkmTDT4140/")
    thread_handler.set_greeting(
        "Hi there {{user_first_name}}!\nWelcome to CallyBot. Press 'Get Started' to get started!")
    thread_handler.set_get_started()
    return thread_handler.set_persistent_menu()


def clear_old_reminders():
    """Clears old reminders, which were not checked while database was down"""
    reminders = db.get_all_reminders()
    for reminder in reminders:
        if reminder[0] < datetime.now():
            db.delete_reminder(reminder[4])


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
    return current


@app.route('/', methods=['POST'])  # pragma: no cover
def handle_incoming_messages():  # pragma: no cover
    """Handles incoming POST messages, has 'pragma: no cover' due to pytest throwing an error
    when handling flask application methods, and internal testing is not needed as this is 
    properly tested trough blackbox"""
    data = request.json
    global received_message
    try:
        message_id = data['entry'][0]['messaging'][0]['message']['mid']
    except (KeyError, TypeError):
        print("\x1b[0;31;0mError: Could not find message_id, or unknown format\x1b[0m")
        return "ok", 200
    if message_id in received_message:
        print("\x1b[0;34;0mDuplicated message\x1b[0m")
        return 'ok', 200
    else:
        if len(received_message) > 256:
            received_message = received_message[-32:]
        received_message.append(message_id)
    print("\n\n")
    print("----------------START--------------")
    print("DATA:")
    try:
        user_id = data['entry'][0]['messaging'][0]['sender']['id']
        print(data)
        print("---------------END-----------------\n")
    except KeyError:
        return "ok", 200
    replier.arbitrate(user_id, data)
    print("\x1b[0;32;0mok 200 for message with message_id", message_id, "\x1b[0m")
    return "ok", 200


@app.route('/', methods=['GET'])  # pragma: no cover
def handle_verification():  # pragma: no cover
    """Handles incoming GET messages, has 'pragma: no cover' due to pytest throwing an error
    when handling flask application methods. This method is properly tested by connectig the server
    to the server"""
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if request.args['hub.verify_token'] == credential.verify_token:
            return request.args['hub.challenge'], 200
        else:
            return "Invalid verification token", 403
    return 'ok', 200


if __name__ == '__main__':
    init()
    app.run(threaded=True)
