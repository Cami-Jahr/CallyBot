"""This is a dummy version of server_main. Only ran locally, and does not support reminders"""
from reply import Reply
from credentials import Credentials
from callybot_database import CallybotDB
from datetime import datetime

credential = Credentials()
db_credentials = credential.db_info
db = CallybotDB(db_credentials[0], db_credentials[1], db_credentials[2], db_credentials[3])
replier = Reply(credential.access_token, db)
joachim_jahr_id = "1550995208259075"

def clear_old_reminders():
    reminders = db.get_all_reminders()
    for reminder in reminders:
        if reminder[0] < datetime.now():
            db.delete_reminder(reminder[4])

clear_old_reminders()

#while True:
#    inn = input("Input message: ")
#    data = {'entry': [{'messaging': [{'message': {'text': inn}}]}]}

#    print(replier.arbitrate(joachim_jahr_id, data))
