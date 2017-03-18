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

        elif content_list[0] == 'subscribe':
            self.subscribe(user_id, content_list[1:])
        
        elif content_list[0] == 'unsubscribe':
            self.unsubscribe(user_id, content_list[1:])

        elif content_lower == "delete me":
            self.reply(user_id, "Are you sure? By deleting your information i will also delete all reminders you have "
                                "scheduled with me. To delete all your information, type 'yes, i agree to delete all "
                                "my information'", "text")

        elif content_lower == "yes, i agree to delete all my information":
            self.db.remove_user(user_id)
            self.reply(user_id, "I have now deleted all your information. If you have any feedback to give me, please "
                                "do so with the 'request' function.\nI hope to see you again!", "text")

        elif content_list[0] == "help":
            self.help(user_id, content_list[1:])

        elif content_lower == "hint":
            msg = "This will be removed at launch!\n\n- Juicy gif\n- Juice gif\n- Who am I?\n- Who are you?\n- Chicken\n- Id\n- Hello"
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
            msg = "Hi there " + fname + "!\nMy name is CallyBot, but you may call me Cally :)\nI will keep you up to " \
                                        "date on your upcomming deadlines on It'slearning and Blackboard. Type 'login' " \
                                        "or use the menu to get started. \nIf you need help, or want to know more about" \
                                        " what i can do for you, just type 'help'.\n\n Please do enjoy!"
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
        if not content_list:
            self.reply(user_id,'Please specify what to get\nType help get if you need help','text')
            return
        if content_list[0] == "deadline" or content_list[0] == "deadlines":
            self.deadlines(user_id, content_list)
        elif content_list[0] == "reminder" or content_list[0] == "reminders":
            reminders = self.db.get_reminders(user_id)
            if reminders:
                msg = ""
                for reminder in reminders:
                    msg += reminder[0] + "\nat " + reminder[1].strftime("%d.%m.%Y %H:%M:%S") + "\n\n"
            else:
                msg = "You don't appear to have any reminders scheduled with me"
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
        elif content_list[0] == "link" or content_list[0] == "links":
            try:
                if content_list[1] == "itslearning":
                    self.reply(user_id, "Link to itslearning:\nhttps://idp.feide.no/simplesaml/module.php/feide/login.php?asLen=252&Auth"
                                        "State=_95a62d76d2130777c0ff6c860f81edcf9e7054c94c%3Ahttps%3A%2F%2Fidp."
                                        "feide.no%2Fsimplesaml%2Fsaml2%2Fidp%2FSSOService.php%3Fspentityid%3Durn%"
                                        "253Amace%253Afeide.no%253Aservices%253Ano.ntnu.ssowrapper%26cookieTime%3D"
                                        "1489851781%26RelayState%3D%252Fsso-wrapper%252Fweb%252Fwrapper%253Ftarget%"
                                        "253Ditslearning", "text")
                elif content_list[1] == "blackboard":
                    self.reply(user_id, "Link to blackboard:\nhttps://idp.feide.no/simplesaml/module.php/feide/"
                                        "login.php?asLen=233&AuthState=_75f2b28123d67c422f8b104e5a6f72339b09ba7583"
                                        "%3Ahttps%3A%2F%2Fidp.feide.no%2Fsimplesaml%2Fsaml2%2Fidp%2FSSOService.php%3"
                                        "Fspentityid%3Dhttp%253A%252F%252Fadfs.ntnu.no%252Fadfs%252Fservices%252Ftru"
                                        "st%26cookieTime%3D1489851857%26RelayState%3Dac5888bf-816a-4fd9-954b-3d623f726c3e", "text")

                else:
                    self.reply(user_id,
                               "Link to itslearning:\nhttps://idp.feide.no/simplesaml/module.php/feide/login.php?asLen=252&Auth"
                               "State=_95a62d76d2130777c0ff6c860f81edcf9e7054c94c%3Ahttps%3A%2F%2Fidp."
                               "feide.no%2Fsimplesaml%2Fsaml2%2Fidp%2FSSOService.php%3Fspentityid%3Durn%"
                               "253Amace%253Afeide.no%253Aservices%253Ano.ntnu.ssowrapper%26cookieTime%3D"
                               "1489851781%26RelayState%3D%252Fsso-wrapper%252Fweb%252Fwrapper%253Ftarget%"
                               "253Ditslearning", "text")
                self.reply(user_id, "Link to blackboard:\nhttps://idp.feide.no/simplesaml/module.php/feide/"
                                    "login.php?asLen=233&AuthState=_75f2b28123d67c422f8b104e5a6f72339b09ba7583"
                                    "%3Ahttps%3A%2F%2Fidp.feide.no%2Fsimplesaml%2Fsaml2%2Fidp%2FSSOService.php%3"
                                    "Fspentityid%3Dhttp%253A%252F%252Fadfs.ntnu.no%252Fadfs%252Fservices%252Ftru"
                                    "st%26cookieTime%3D1489851857%26RelayState%3Dac5888bf-816a-4fd9-954b-3d623f726c3e",
                           "text")
            except IndexError:
                    self.reply(user_id, "Link to itslearning:\nhttps://idp.feide.no/simplesaml/module.php/feide/login.php?asLen=252&Auth"
                                        "State=_95a62d76d2130777c0ff6c860f81edcf9e7054c94c%3Ahttps%3A%2F%2Fidp."
                                        "feide.no%2Fsimplesaml%2Fsaml2%2Fidp%2FSSOService.php%3Fspentityid%3Durn%"
                                        "253Amace%253Afeide.no%253Aservices%253Ano.ntnu.ssowrapper%26cookieTime%3D"
                                        "1489851781%26RelayState%3D%252Fsso-wrapper%252Fweb%252Fwrapper%253Ftarget%"
                                        "253Ditslearning", "text")
                    self.reply(user_id, "Link to blackboard:\nhttps://idp.feide.no/simplesaml/module.php/feide/"
                                        "login.php?asLen=233&AuthState=_75f2b28123d67c422f8b104e5a6f72339b09ba7583"
                                        "%3Ahttps%3A%2F%2Fidp.feide.no%2Fsimplesaml%2Fsaml2%2Fidp%2FSSOService.php%3"
                                        "Fspentityid%3Dhttp%253A%252F%252Fadfs.ntnu.no%252Fadfs%252Fservices%252Ftru"
                                        "st%26cookieTime%3D1489851857%26RelayState%3Dac5888bf-816a-4fd9-954b-3d623f726c3e", "text")



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


    def subscribe(self, user_id, content_list):
        """Subscribes user to course(s). Takes in user id and course(s) to be subscribed to. Replies with confirmation and ends"""
        if not content_list:
            self.reply(user_id,'subsribe to what?\nType help subscribe if you need help','text')
            return
        
        self.reply(user_id,'Subscribing to '+','.join(content_list)+"...",'text')
        non_existing,already_subscribed,success_subscribed=[],[],[]
        for course in content_list:
            course=course.upper()
            if self.db.course_exists(course):
                if not self.db.user_subscribed_to_course(user_id,course):
                    self.db.subscribe_to_course(user_id,course)
                    success_subscribed.append(course)
                else:
                    already_subscribed.append(course)
            else:
                non_existing.append(course)
        if non_existing:
            self.reply(user_id,'The following course(s) do(es) not exist: '+','.join(non_existing),'text')
        if already_subscribed:
            self.reply(user_id,'You are already subscribed to '+','.join(already_subscribed),'text')
        if success_subscribed:
            self.reply(user_id,'You have successfully subscribed to'+','.join(success_subscribed),'text')


    def unsubscribe(self, user_id, content_list):
        """Unsubscribes user to course(s). Takes in user id and course(s) to be subscribed to. Replies with confirmation and ends"""
        if not content_list:
            self.reply(user_id,'Unsubsribe from what?\nType help unsubscribe if you need help','text')
            return

        self.reply(user_id,'Unsubscribing from '+','.join(content_list)+"...",'text')
        non_existing,not_subscribed,success_unsubscribed=[],[],[]
        for course in content_list:
            course=course.upper()
            if self.db.course_exists(course):
                if self.db.user_subscribed_to_course(user_id,course):
                    self.db.unsubscribe(user_id,course)
                    success_unsubscribed.append(course)
                else:
                    not_subscribed.append(course)
            else:
                non_existing.append(course)
        if non_existing:
            self.reply(user_id,'The following course(s) do(es) not exist: '+','.join(non_existing),'text')
        if not_subscribed:
            self.reply(user_id,'You are not subscribed to '+','.join(not_subscribed),'text')
        if success_unsubscribed:
            self.reply(user_id,'You have successfully unsubscribed from'+','.join(success_unsubscribed),'text')


    def bug(self, user_id, content_list):
        """Bug report. Takes in user id and list of message, without 'bug' at List[0]. Replies, saves and ends"""
        if not content_list:
            self.reply(user_id,'Please specify atleast one bug\nType help bug if you need help','text')
            return
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
        if not content_list:
            self.reply(user_id, "Oh you need help?\nNo problem!\nFollowing commands are supported:\n"
                                "\n- Login\n- Get deadlines\n- Get exams\n- Get links\n- Get reminders\n- Set reminder"
                                "\n- Delete me\n- Bug\n- Request\n- Subscribe\n- Help"
                                "\n\nBut thats not all, theres also some more hidden commands!\nIts up to you to find "
                                "them ;)\n\n"
                                "If you want a more detailed overview over a feature, you can write 'help <feature>'. "
                                "You can try this with 'help help' now!", 'text')

        elif content_list[0] == "get":
            try:
                if content_list[1] == "deadlines" or content_list[1] == "deadline":
                    self.reply(user_id, "Deadlines are fetched from It'slearning and Blackboard with the feide username and"
                                        " password you entered with the 'login' command. To get the deadlines you can write"
                                        " the following commands:\n\t- get deadlines\n\t- get deadlines until <DD/MM>\n"
                                        "\t- get deadlines from <course>\n\t- get deadlines from <course> until <DD/MM>\n\n"
                                        "Without the <> and the course code, date and month you wish", "text")

                elif content_list[1] == "exam" or content_list[1] == "exams":
                    self.reply(user_id, "I can get the exam date for any of your courses. Just write"
                                        "\n- Get exams <course_code> (course_code2....)", "text")

                elif content_list[1] == "link" or content_list[1] == "links":
                    self.reply(user_id, "I can give you fast links to It'slearning or Blackboard with these commands:"
                                        "\n- Get links\n- Get link Itslearning\n- Get link Blackboard", "text")
                elif content_list[1] == "reminder" or content_list[1] == "reminders":
                    self.reply(user_id, "This gives you an overview of all upcoming reminders I have in store for you."
                                        , "text")
                else:
                    self.reply(user_id,
                               "I'm not sure that's a supported command, if you think this is a bug, please do report "
                               "it with the 'bug' function! If it something you simply wish to be added, use the "
                               "'request' function", "text")
            except IndexError:
                self.reply(user_id,
                           "I'm not sure that's a supported command, if you think this is a bug, please do report "
                           "it with the 'bug' function! If it something you simply wish to be added, use the "
                           "'request' function", "text")

        elif content_list[0] == "set":
            if content_list[1] == "reminder" or content_list[1] == "reminders":
                self.reply(user_id, "I can give reminders to anyone who is logged in with the 'login' command. "
                                    "Anyone who is logged in can create and manage their own reminders. "
                                    "If you login with your feide username and password I can retrieve all your "
                                    "deadlines on It'slearning and Blackboard as well, and give you reminders to "
                                    "those when they are soon due. I will naturally never share your information with "
                                    "anyone!\n\nThe following commands are supported:\n\n\t"
                                    "- set reminder ¤Reminder text¤ at YYYY-MM-DD HH:mm:ss\n\n"
                                    "Where ¤Reminder text¤ is what "
                                    "i should tell you when the reminder is due.", "text")
            else:
                self.reply(user_id,
                           "I'm not sure that's a supported command, if you think this is a bug, please do report "
                           "it with the 'bug' function. If it something you simply wish to be added, use the "
                           "'request' function", "text")

        elif content_list[0] == "help":
            self.reply(user_id, "The help method gives more detailed information about my features, and their commands"
                                ". You may type help in front of any method to get a more detailed overview of what it"
                                " does.", "text")
        elif content_list[0] == "login":
            self.reply(user_id, "You must log in for me to be able to give you reminders. If you log in with your "
                                "feide username and password I can also fetch your deadlines from blackboard and "
                                "It'slearning!", "text")
        elif content_list[0] == "delete me":
            self.reply(user_id, "If you want me to delete all information I have on you, type in 'delete me', and "
                                "follow the instructions i give you", "text")
        elif content_list[0] == "bug":
            self.reply(user_id, "If you encounter a bug please let me know! You submit a bug report with a"
                                "\n- bug <message> \n"
                                "command. If it is a feature you wish added, please use the request command instead", "text")
        elif content_list[0] == "request":
            self.reply(user_id, "If you have a request for a new feature please let me know! You submit a feature"
                                " request with a\n- request <message> \ncommand. If you think this is already a feature"
                                ", and you encountered a bug, please use the bug command instead", "text")
        elif content_list[0] == "subscribe":
           self.reply(user_id, "You can subscribe to courses you wish to get reminders from", "text")

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
            self.replier.reply(user_id, "Could not fetch deadlines. Check if your user info is correct. You can "
                                        "probably fix this by using the 'login' command and logging in again with your"
                                        " feide username and password.\n\nIf you belive this is a bug, please report "
                                        "it with the 'bug' function", 'text')
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


