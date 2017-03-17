import ilearn_scrape
import iblack_scrape
import requests
import MySQLdb
import json
from datetime import datetime, timedelta


def add_default_reminders(user_id, assignments, db):
	names = [x[0] for x in db.get_reminders(user_id)]
	for assignment in assignments:
		if db.user_subscribed_to_course(user_id, assignment[0]) and assignment[1] not in names:
			db.add_reminder(assignment[1], assignment[2], 1, user_id)


def search_reminders(db):
	"""Returns all reminders for the next hours, in format [datetime.datetime, user_id, message, course_made]"""
	listing = db.get_all_reminders()
	# print(listing)
	min_ago = datetime.now() - timedelta(minutes=1)
	min_til = datetime.now() + timedelta(minutes=1)
	current = []
	app = current.append
	for line in listing:
		if min_ago < line[0] < min_til:
			app(line)
	# print(current)
	return current


def get_course_info(course):
	# Other information may be fetched later, by reading from the info data
	try:
		info = requests.get('http://www.ime.ntnu.no/api/course/' + course).json()
	except json.decoder.JSONDecodeError:  # course does not exist in ime api
		return "Was unable to retrive exam date for " + course
	exam_date = None
	try:
		for i in range(len(info["course"]["assessment"])):
			if "date" in info["course"]["assessment"][i]:
				exam_date = info["course"]["assessment"][i]["date"]
				break
	except (KeyError, TypeError):  # Catch if date does not exist, or assessment does not exist
		pass
	return course, exam_date


def get_user_info(access_token, user_id):  # Get user info from profile
	user_details_url = "https://graph.facebook.com/v2.8/" + str(user_id)
	user_details_params = {'fields': 'first_name,last_name,profile_pic', 'access_token': access_token}
	user_details = requests.get(user_details_url, user_details_params).json()
	lastname = user_details['last_name']
	firstname = user_details['first_name']
	picture = user_details['profile_pic']
	return firstname, lastname, picture


def IL_scrape(user_id, course, until, db):
	course = course.upper()
	result = db.get_credential(user_id)

	info = ilearn_scrape.scrape(result[2], result[3])
	msg = ""
	max_day = int(until.split("/")[0])
	max_month = int(until.split("/")[1])
	# Max time it should get deadlines to
	reminders_to_set = []
	if course == "ALL":
		for line in info:
			due_day = int(line[3].split(".")[0])
			due_month = int(line[3].split(".")[1])
			if max_month > due_month or (max_month == due_month and max_day >= due_day):  # Before max deadlines
				day, month, year = line[3].split(".")
				reminders_to_set.append((line[1], line[0], "{}-{}-{}".format(year, month, day) + " " + line[4] + ":00"))
				msg += line[0] + "\nin " + line[1] + " " + line[2] + "\nDue date: " + line[3] + " " + line[
					4] + "\n\n"  # Format to default ###NOTE### does support time as line[4]
		add_default_reminders(user_id, reminders_to_set, db)
	else:
		for line in info:
			due_day = int(line[3].split(".")[0])
			due_month = int(line[3].split(".")[1])
			if line[1] == course and (max_month > due_month or (
							max_month == due_month and max_day >= due_day)):  # Before  max deadlines and correct course
				msg += line[0] + "\nin " + line[1] + " " + line[2] + "\nDue date: " + line[3] + " " + line[
					4] + "\n\n"  # Format to default ###NOTE### does support time as line[4]
	return msg


def BB_scrape(user_id, course, until, db):
	course = course.upper()
	result = db.get_credential(user_id)
	info = iblack_scrape.scrape(result[2], result[3])
	msg = ""
	max_day = int(until.split("/")[0])
	max_month = int(until.split("/")[1])
	# Max time it should get deadlines to
	reminders_to_set = []
	if course == "ALL":
		for line in info:
			due_day = int(line[3].split(".")[0])
			due_month = int(line[3].split(".")[1])
			if max_month > due_month or (max_month == due_month and max_day >= due_day):  # Before  max deadlines
				day, month, year = line[3].split(".")
				reminders_to_set.append(
					(line[1], line[0], "20{}-{}-{}".format(year, month, day) + " 23:59:00"))
				msg += line[0] + "\nin " + line[1] + " " + line[2] + "\nDue date: " + line[
					3] + "\n\n"  # Format to default ###NOTE### do NOT support time as line[4]
		add_default_reminders(user_id, reminders_to_set, db)
	else:
		for line in info:
			due_day = int(line[3].split(".")[0])
			due_month = int(line[3].split(".")[1])
			if line[1] == course and (max_month > due_month or (
							max_month == due_month and max_day >= due_day)):  # Before  max deadlines and correct course
				msg += line[0] + "\nin " + line[1] + " " + line[2] + "\nDue date: " + line[
					3] + "\n\n"  # Format to default ###NOTE### do NOT support time as line[4]
	return msg
