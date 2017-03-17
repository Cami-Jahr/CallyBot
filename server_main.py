from flask import Flask, request
import reply
import help_methods
import thread_settings
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import credentials
import Callybot_DB

app = Flask(__name__)
credential = credentials.Credentials()
db_creds = credential.db_info
db = Callybot_DB.CallybotDB(db_creds[0], db_creds[1], db_creds[2], db_creds[3])
replier = reply.Reply(credential.access_token, db)
sequence_numbers = []


def init():
	thread_handler = thread_settings.Thread_Settings(credential.access_token)
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
		trigger=CronTrigger(minute=0),  # second = 0 for checking every minute
		id='reminder_check',
		name='Reminder',
		replace_existing=True)
	atexit.register(lambda: scheduler.shutdown())


def reminder_check():
	# Run reminder_check
	print("Reminder trigger", time.ctime())
	current = help_methods.search_reminders(db)
	if current:
		for reminder in current:
			replier.reply(reminder[1], "Reminder: " + reminder[2], "text")
	return


@app.route('/', methods=['POST'])
def handle_incoming_messages():
	data = request.json
	try:
		global sequence_numbers
		seq = data['entry'][0]['messaging'][0]['message']['seq']
		if seq in sequence_numbers:
			print("Duplicated message")
			return 'ok', 200
		else:
			if len(sequence_numbers) > 100: sequence_numbers = []
			sequence_numbers.append(seq)
	except KeyError:
		pass

	print()
	print("----------------START--------------")
	print("DATA:")
	print(data)
	print("---------------END-----------------")
	user_id = data['entry'][0]['messaging'][0]['sender']['id']
	replier.arbitrate(user_id, data)
	print("Everything is good in the good")
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
