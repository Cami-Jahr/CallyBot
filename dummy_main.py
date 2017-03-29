"""This is a dummy version of server_main. Only ran localy, and does not support reminders"""
import reply
import credentials
import callybot_database

credential = credentials.Credentials()
db_credentials = credential.db_info
db = callybot_database.CallybotDB(db_credentials[0], db_credentials[1], db_credentials[2], db_credentials[3])
replier = reply.Reply(credential.access_token, db)

while True:
    inn = input("Input message: ")
    data = {'entry': [{'messaging': [{'message': {'text': inn}}]}]}
    print(replier.arbitrate("1", data))
