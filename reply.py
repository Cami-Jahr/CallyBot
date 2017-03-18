import requests
import help_methods
import re  # Regular expressions https://docs.python.org/3/library/re.html


class Reply:
    """The reply class handles all incoming messages. The input is the user id and the json element of the message.
    The class handles it with the 'arbitrate' function, and replies to the user with a logical reply"""

    def __init__(self, access_token, db):
        self.access_token = access_token
        # These regex allow a increasing amount of courses, They however also use longer time to check,
        # and allow more non existing courses to be processed
        course_code_format1 = '[a-z]{2,3}[0-9]{4}'
        # course_code_format2 = "[æøåa-z]{1,6}[0-9]{1,6}"
        # course_code_format3 = "[0-9]?[æøåa-z]{1,6}[0-9]{1,6}[æøåa-z]{0,4}[0-9]{0,2}\-?[A-Z]{0,3}[0-9]{0,3}|mts/mo1"
        self.course_code_format = course_code_format1  # Checks if string is in format aaa1111 or aa1111,
        # ie course_code format on ntnu
        date_format_separator = "[\/]"  # Date separators allowed. Regex format
        self.date_format = "(^(((0?[1-9]|1[0-9]|2[0-8])" + date_format_separator + "(0?[1-9]|1[012]))|((29|30|31)" + \
                           date_format_separator + "(0?[13578]|1[02]))|((29|30)" + date_format_separator + "(0?[469]|11))))"
        # checks if is legit date.
        self.db = db
        self.scraper = Scraper(self, self.db)
        self.scraper.start()

    def arbitrate(self, user_id, data):
        """Chooses action based on message given, does not return"""
        data_type, content = Reply.process_data(data)
        print("Data type:", data_type)
        print("Content:", content)
        if data_type == "unknown":  # Cant handle unknown
            print("\x1b[0;34;0mUnknown data type\x1b[0m")
            return
        content_lower = content.lower()
        content_list = content_lower.split()
        # ------------ COMMANDS --------------

        if content_list[0] == "get":
            self.get_statements(user_id, content_list[1:])

        elif content_list[0] == "set":
            self.set_statements(user_id, content_list[1:])

        elif content_lower == "hello":
            msg = "http://cdn.ebaumsworld.com/mediaFiles/picture/2192630/83801651.gif"
            self.reply(user_id, msg, 'image')

        elif content_lower == "login":
            self.login(user_id)

        elif content_list[0] == "bug":
            self.bug(user_id, content_list[1:])

        elif content_list[0] == "request":
            self.request(user_id, content_list[1:])

        # ------------ HELP METHODS -----------
        elif content_list[0] == "help":
            self.help(user_id, content_list[1:])

        elif content_lower == "hint":
            msg = "This will be removed at launch!\n\n- juicy gif\n- juice gif\n- who am I?\n- who are you?\n- chicken\n- id"
            self.reply(user_id, msg, 'text')

        # ------------ EASTER EGGS --------------
        elif content_lower == "chicken":
            msg = "http://folk.ntnu.no/halvorkm/TDT4140/chickenattack.mp4"
            self.reply(user_id, msg, 'video')

        elif content_lower == "id":
            self.reply(user_id, user_id, 'text')

        elif content_lower == "juice gif":
            msg = "https://i.makeagif.com/media/10-01-2015/JzrY-u.gif"
            self.reply(user_id, msg, 'image')

        elif content_lower == "juicy gif":
            msg = "http://68.media.tumblr.com/tumblr_m9pbdkoIDA1ra12qlo1_400.gif"
            self.reply(user_id, msg, 'image')

        elif content_lower == "who are you?":
            msg = "I am Cally, your lord and savior"
            self.reply(user_id, msg, 'text')
            url = "https://folk.ntnu.no/halvorkm/callysavior.jpg"
            self.reply(user_id, url, 'image')

        elif content_lower == "who am i?":
            fname, lname, pic = help_methods.get_user_info(self.access_token, user_id)  # Get userinfo
            msg = "You are " + fname + " " + lname + " and you look like this:"
            self.reply(user_id, msg, 'text')
            self.reply(user_id, pic, 'image')

        # ------------ GET STARTED --------------
        elif content_lower == "start_new_chat":
            fname, lname, pic = help_methods.get_user_info(self.access_token, user_id)  # Get userinfo
            msg = "Hi there " + fname + "!\nMy name is CallyBot, but you may call me Cally :)\nType 'help' to see" \
                                        " what I can do. \n\n Please do enjoy!"
            self.reply(user_id, msg, 'text')

        # -------------- DEFAULT ----------------
        else:
            # with open("LOG/"+user_id+".txt", "a", encoding='utf-8') as f:  #W rite to log file, to see what errors
            # are made, per user
            #    f.write(content+"\n")
            if data_type == "text":
                self.reply(user_id,
                           content + "\nDid you mean to ask me to do something? Type 'help' to see my supported "
                                     "commands", data_type)
            else:
                self.reply(user_id, content, data_type)

    def get_statements(self, user_id, content_list):
        """All get statements. Takes in user id and list of message, without 'get' at List[0]. Replies and ends"""
        if content_list[0] == "deadline" or content_list[0] == "deadlines":
            self.deadlines(user_id, content_list)
        elif content_list[0] == "reminder" or content_list[0] == "reminders":
            reminders = self.db.get_reminders(user_id)
            msg = ""
            for reminder in reminders:
                msg += reminder[0] + "\nat " + reminder[1].strftime("%d.%m.%Y %H:%M:%S") + "\n\n"
            self.reply(user_id, msg, "text")
        elif content_list[0] == "exam" or content_list[0] == "exams":
            msg = ""
            for exam in content_list[1:]:
                date = help_methods.get_course_exam_date(exam)
                if date:
                    msg += "The exam in " + exam + " is on " + date + "\n\n"
                else:
                    msg += "I cant find the exam date for " + exam + "\n\n"
            self.reply(user_id, msg, "text")
        else:
            self.reply(user_id, "I'm sorry, I'm not sure how to retrieve that",
                       "text")  # TODO: Return a list of all supported get statements

    def deadlines(self, user_id, content_list):
        """Handles all requests for deadlines, with all parameters supported, returns nothing, but replies to user"""
        self.scraper.scrape(user_id, content_list)
        self.reply(user_id, "I'll go get your deadlines right now. If there are many people asking for deadlines "
                            "this might take me some time", "text")


    def set_statements(self, user_id, content_list):
        """All set statements. Takes in user id and list of message, without 'set' at List[0]. Replies and ends"""
        if content_list[0] == "reminder" or content_list[
            0] == "reminders":  # Expects format "reminder $Reminder_text at YYYY-MM-DD HH:mm:ss
            self.db.add_reminder(" ".join(content_list[1:-3]), " ".join(content_list[-2:]), 0, user_id)
            self.reply(user_id, "The reminder" + " ".join(content_list[1:-3]) + " was sat at " +
                       " ".join(content_list[-2:]), "text")
        else:
            self.reply(user_id, "I'm sorry, I'm not sure what you want me to remember", "text")

    def bug(self, user_id, content_list):
        """Bug report. Takes in user id and list of message, without 'bug' at List[0]. Replies, saves and ends"""
        with open("BUG/user_bug_reports.txt", "a", encoding='utf-8') as f:
            f.write(user_id + ": " + " ".join(content_list) + "\n")
        self.reply(user_id, "The bug was taken to my developers. One of them might contanct you if they need further "
                            "help with the bug", "text")

    def request(self, user_id, content_list):
        """Requests. Takes in user id and list of message, without 'request' at List[0]. Replies, saves and ends"""
        with open("REQUEST/user_bug_reports.txt", "a", encoding='utf-8') as f:
            f.write(user_id + ": " + " ".join(content_list) + "\n")
        self.reply(user_id, "The request was taken to my developers. I will try to make your wish come true, but keep"
                            " in mind that not all request are feasible", "text")

    def help(self, user_id, content_list):
        """Replies to the user with a string explaining the method in content_list"""
        # TODO: Add help strings to most funtions supported by the bot, to ease navigation
        if not content_list:
            self.reply(user_id, "Oh you need help?\nNo problem!\nFollowing commandoes are supported:\n\n\- hello\n- "
                                "login\n- get deadlines [in <course>][until <DD/MM>]\
            \n\nBut thats not all, theres also some more!\nIts up to you to find them :)\n\n"
                                "If you want a more detailed overview over a feature, you can write 'help <feature>'. "
                                "You can try this with 'help help' now", 'text')

        elif content_list[0] == "deadlines" or content_list[0] == "deadline":
            self.reply(user_id, "Deadlines are fetched from It'slearning and Blackboard with the feide username and "
                                "password you entered with the 'login' command. To get the deadlines you can write "
                                "the following commands:\n\t- get deadlines\n\t- get deadlines until <DD/MM>\n\t- get deadlines "
                                "from <course>\n\t- get deadlines from <course> until <DD/MM>\n\n"
                                "Without the <> and the course code, date and month you wish", "text")

        elif content_list[0] == "help":
            self.reply(user_id, "The help method gives more detailed information about my features, and their commands"
                                ". Currently you can search up information for:\n\t-deadlines\n\t-help"
                                "\n\t-reminders", "text")

        elif content_list[0] == "reminder" or content_list[0] == "reminders":
            self.reply(user_id, "I can give reminders to anyone who is logged in with the 'login' command. "
                                "Anyone who is logged in can create and manage their own reminders. "
                                "If you login with your feide username and password I can retrieve all your "
                                "deadlines on It'slearning and Blackboard as well, and give you reminders to "
                                "those when they are soon due. I will naturally never share your information with "
                                "anyone.\n\nThe following commands are supported:\n\n\t"
                                "- set reminder ¤Reminder text¤ at YYYY-MM-DD HH:mm:ss\n\t- get reminders\n\n"
                                "Where ¤Reminder text¤ is what "
                                "i should tell you when the reminder is due.", "text")

        else:
            self.reply(user_id, "I'm not sure that's a supported command, if you think this is a bug, please do report "
                                "it with the 'bug' function. If it something you simply wish to be added, use the "
                                "'request' function", "text")

    def process_data(data):
        """Classifies data type and extracts the data. Returns [data_type, content]"""
        try:
            content = data['entry'][0]['messaging'][0]['message']  # Pinpoint content
            if 'text' in content:  # Check if text
                content = content['text']  # Extract text
                data_type = 'text'
            elif 'attachments' in content:  # Check if attachment
                content = content['attachments'][0]
                data_type = content['type']  # Extract attachment type
                if (data_type in ('image', 'audio', 'video', 'file')):  # Extract payload based on type
                    content = content['payload']['url']  # Get attachement url
                else:  # Must be either location or multimedia which only have payload
                    content = content['payload']
            else:
                data_type = "unknown"
                content = ""
        except KeyError:
            try:  # Check if payload from button (ie Get Started, persistent menu)
                content = data['entry'][0]['messaging'][0]['postback']['payload']
                data_type = 'text'
            except:
                data_type = "unknown"
                content = ""

        return data_type, content

    def reply(self, user_id, msg, msg_type):
        """Replies to the user with the given message"""
        if msg_type == 'text':  # Text reply
            data = {
                "recipient": {"id": user_id},
                "message": {"text": msg}
            }
        elif msg_type in ('image', 'audio', 'video', 'file'):  # Media attachment reply
            data = {
                "recipient": {"id": user_id},
                "message": {
                    "attachment": {
                        "type": msg_type,
                        "payload": {
                            "url": msg
                        }
                    }
                }
            }
        else:
            print("Error: Type not supported")
            return
        response = requests.post(self.get_reply_url(), json=data)
        print(response.content)

    def login(self, user_id):
        """Sends the user to the login page"""
        fname, lname, pic = help_methods.get_user_info(self.access_token, user_id)  # Retrieve user info
        url = "https://folk.ntnu.no/halvorkm/TDT4140?userid=" + str(user_id) + "?name=" + fname + "%" + lname
        data = {
            "recipient": {"id": user_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": "Please login here:",
                        "buttons": [{
                            "type": "web_url",
                            "url": url,
                            "title": "Login via Feide",
                            "webview_height_ratio": "compact",
                            "messenger_extensions": True,
                            "fallback_url": url}]
                    }
                }
            }
        }
        response = requests.post(self.get_reply_url(), json=data)
        print(response.content)

    def get_reply_url(self):
        return "https://graph.facebook.com/v2.8/me/messages?access_token=" + self.access_token


from threading import Thread
from collections import deque
from time import sleep

class Scraper(Thread):
    """The class inherits Thread, something that is necessary to make the Scraper start a new thread, which
    allows the server to send a '200 ok' fast after being prompted to scrape, and then scrape without facebook pushing
    new POST messages of the same get deadlines command.
    To add a scrape request to the queue, run function scrape(user_id, content_list)"""

    def __init__(self, reply_class, db):
        Thread.__init__(self)
        # Flag to run thread as a deamon (stops when no other threads are running)
        self.daemon = True
        self.requests = deque()
        self.pop = self.requests.popleft
        self.app = self.requests.append
        self.replier = reply_class

        course_code_format1 = '[a-z]{2,3}[0-9]{4}'
        # course_code_format2 = "[æøåa-z]{1,6}[0-9]{1,6}"
        # course_code_format3 = "[0-9]?[æøåa-z]{1,6}[0-9]{1,6}[æøåa-z]{0,4}[0-9]{0,2}\-?[A-Z]{0,3}[0-9]{0,3}|mts/mo1"
        self.course_code_format = course_code_format1  # Checks if string is in format aaa1111 or aa1111,
        # ie course_code format on ntnu
        date_format_separator = "[\/]"  # Date separators allowed. Regex format
        self.date_format = "(^(((0?[1-9]|1[0-9]|2[0-8])" + date_format_separator + "(0?[1-9]|1[012]))|((29|30|31)" + \
                           date_format_separator + "(0?[13578]|1[02]))|((29|30)" + date_format_separator + "(0?[469]|11))))"
        self.db = db

    def run(self):
        while True:
            if self.requests:
                self.process(self.pop())
            else:
                sleep(10)  # Delay until looks again if it did not find an active scrape request

    def scrape(self, user_id, content_list):
        """Queues the scrape request for the server to handle"""
        self.app((user_id, content_list,))

    def process(self, query):
        user_id, content_list = query
        course = "ALL"
        until = "31/12"  # TODO: Changed to default duration of user from sql server. Must still be in format DD/MM
        if len(content_list) == 1:  # Asks for all
            pass
        elif len(content_list) <= 3:  # Allows "in" and "until" to be dropped by the user
            if re.fullmatch(self.course_code_format, content_list[-1]):
                course = content_list[-1]
            elif re.fullmatch(self.date_format, content_list[-1]):
                until = content_list[-1]
            else:
                pass
        elif len(content_list) == 5:  # Strict format
            if content_list[1] == "in" and re.fullmatch(self.course_code_format, content_list[2]) and content_list[
                3] == "until" and re.fullmatch(self.date_format, content_list[4]):
                # Format: get deadline in aaa1111 until DD/MM
                course = content_list[2]
                until = content_list[4]
            elif content_list[1] == "until" and re.fullmatch(self.date_format, content_list[2]) and content_list[
                3] == "in" and re.fullmatch(self.course_code_format, content_list[
                4]):  # Format: get deadline until DD/MM deadline in aaa1111
                until = content_list[2]
                course = content_list[4]

        # print(content_list, course, until)
        ILdeads = help_methods.IL_scrape(user_id, course, until, self.db)
        BBdeads = help_methods.BB_scrape(user_id, course, until, self.db)
        # print(ILdeads, BBdeads)
        if ILdeads == "SQLerror" or BBdeads == "SQLerror":
            self.replier.reply(user_id, "Could not fetch deadlines. Check if your user info is correct", 'text')
        elif course == "ALL":
            msg = "ItsLearning:\n" + ILdeads
            msg2 = "BlackBoard:\n" + BBdeads
            self.replier.reply(user_id, msg, 'text')
            self.replier.reply(user_id, msg2, 'text')
        else:
            if ILdeads or BBdeads:  # Both is returned as empty if does not have course
                self.replier.reply(user_id, "For course " + course + " I found these deadlines:\n" + ILdeads + BBdeads, "text")
            else:
                self.replier.reply(user_id, "I couldn't find any deadlines for " + course, "text")


