import requests
import help_methods
import re  # Regular expressions https://docs.python.org/3/library/re.html
from datetime import datetime, timedelta
import json
import scraper


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
                           date_format_separator + "(0?[13578]|1[02]))|((29|30)" + date_format_separator + \
                           "(0?[469]|11))))"
        # checks if is legit date.
        self.db = db
        self.scraper = scraper.Scraper(self, self.db)
        self.scraper.start()

        self.rep = {" ": "-", "/": "-", "\\": "-", ":": "-", ";": "-", ",": "-", ".": "-"}
        # define desired replacements here.
        # Used in set reminder to get a standard format to work with
        self.rep = dict((re.escape(k), v) for k, v in self.rep.items())
        self.pattern = re.compile("|".join(self.rep.keys()))

        self.delete_conf = {}
        self.user_reminders = {}

    def arbitrate(self, user_id, data):
        """Chooses action based on message given, does not return"""
        data_type, content = Reply.process_data(data)
        print("Data type:", data_type)
        print("Content:", content)
        with open("LOG/" + user_id + "_chat.txt", "a", encoding="UTF-8") as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "  User: " + content + "\n")
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

        elif content_list[0] == "delete":
            self.delete_statements(user_id, content_list[1:])

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


        elif content_lower == "yes, i agree to delete all my information":
            self.db.remove_user(user_id)
            self.reply(user_id, "I have now deleted all your information. If you have any feedback to give me, please "
                                "do so with the 'request' function.\nI hope to see you again!", "text")

        elif content_list[0] == "help":
            self.help(user_id, content_list[1:])

        elif content_lower == "hint":
            msg = "This will be removed at launch!\n\n- Juicy gif\n- Juice gif\n- Who am I?\n- Who are you?\n- Chicken\n- Hello"
            self.reply(user_id, msg, 'text')

        # ------------ EASTER EGGS --------------
        elif content_lower == "chicken":
            # msg = "http://folk.ntnu.no/halvorkm/TDT4140/chickenattack.mp4"
            msg = "Did I scare ya?"
            self.reply(user_id, msg, 'text')

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

        elif content_lower == "good bye" or content_lower == "bye" or content_lower == "farewell":
            msg = "Bye now!"
            self.reply(user_id, msg, 'text')

        # ------------ GET STARTED --------------
        elif content_lower == "start_new_chat":
            fname, lname, pic = help_methods.get_user_info(self.access_token, user_id)  # Get userinfo
            msg = "Hi there " + fname + "!\nMy name is CallyBot, but you may call me Cally :)\nI will keep you up to " \
                                        "date on your upcomming deadlines on It'slearning and Blackboard. Type 'login' " \
                                        "or use the menu to get started. \nIf you need help, or want to know more about" \
                                        " what i can do for you, just type 'help'.\n\n Please do enjoy!"
            self.reply(user_id, msg, 'text')
            self.reply(user_id, "_____@_____\nThis is alpha version of the bot, if you encounter anything unusual, "
                                "please report it as detailed as possible. If you wish a feature added please inform"
                                " us about it. Please do report anything you can, from typos, to "
                                "poor sentences, to hard to access information, to any 'shortcuts' you would like to "
                                "see. Thank you for helping with testing of "
                                "the bot!\n\n- The developers of CallyBot", "text")
            self.db.add_user(user_id,fname+lname)


        # ------------- DEVELOPER - --------------

        # NOT TO BE SHOWN TO USERS, FOR DEVELOPER USE ONLY, do not add to hint/help etc

        elif content_lower == "developer: id":
            self.reply(user_id, user_id, 'text')

        elif content_lower == "developer: get requests":
            with open("REQUEST/user_requests.txt", "r", encoding='utf-8') as f:
                all_requests = f.readlines()
                msg = ""
                for request in all_requests:
                    if len(msg) + len(request) >= 600:
                        self.reply(user_id, msg, "text")
                        msg = request
                    else:
                        msg += request
                self.reply(user_id, msg, "text")

        elif content_lower == "developer: get bugs":
            with open("BUG/user_bug_reports.txt", "r", encoding='utf-8') as f:
                reports = f.readlines()
                msg = ""
                for report in reports:
                    if len(msg) + len(report) >= 600:
                        self.reply(user_id, msg, "text")
                        msg = report
                    else:
                        msg += report
                self.reply(user_id, msg, "text")

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
            self.reply(user_id, 'Please specify what to get\nType help get if you need help', 'text')
            return

        if content_list[0] == "deadline" or content_list[0] == "deadlines":
            self.deadlines(user_id, content_list)

        elif content_list[0] == "reminder" or content_list[0] == "reminders":
            reminders = self.db.get_reminders(user_id)
            self.user_reminders[user_id] = {}
            i = 1
            if reminders:
                msg = ""
                for reminder in reminders:
                    msg += str(i) + ": " + reminder[0] + "\nat " + reminder[1].strftime("%d.%m.%Y %H:%M") + "\n\n"
                    self.user_reminders[user_id][i] = reminder[3]
                    i += 1
                print(self.user_reminders)
            else:
                msg = "You don't appear to have any reminders scheduled with me"
            self.reply(user_id, msg, "text")

        elif content_list[0] == "exam" or content_list[0] == "exams":
            msg = ""
            if content_list[1:]:
                for exam in content_list[1:]:
                    date = help_methods.get_course_exam_date(exam)
                    if date:
                        msg += "The exam in " + exam + " is on " + date + "\n\n"
                    else:
                        msg += "I cant find the exam date for " + exam + "\n\n"
                if not msg:
                    msg = "I could not find any exam dates, are you sure you wrote the correct code?"
            else:
                courses = self.db.get_all_courses(user_id)
                for exam in courses:
                    date = help_methods.get_course_exam_date(exam)
                    if date:
                        msg += "The exam in " + exam + " is on " + date + "\n\n"
                    else:
                        msg += "I cant find the exam date for " + exam + "\n\n"
                if not msg:
                    msg = "I could not find any exam date, are you sure you are subscribed to courses?"
            self.reply(user_id, msg, "text")

        elif content_list[0] == "default-time":
            df = self.db.get_defaulttime(user_id)
            if df == -1:
                self.reply(user_id, "To check default-time, please login", 'text')
            else:
                self.reply(user_id, "Your default-time is: " + str(df), 'text')

        elif content_list[0] == "link" or content_list[0] == "links":
            try:
                if content_list[1] == "itslearning":
                    self.reply(user_id,
                               "Link to itslearning:\nhttps://idp.feide.no/simplesaml/module.php/feide/login.php?asLen=252&Auth"
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
                                        "st%26cookieTime%3D1489851857%26RelayState%3Dac5888bf-816a-4fd9-954b-3d623f726c3e",
                               "text")

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

        elif content_list[0] == "subscribe" or content_list[0] == "subscribed":
            courses = self.db.get_all_courses(user_id)
            if courses:
                msg = "You are subscribed to:\n"
                for course in courses:
                    msg += course + "\n"
            else:
                msg = "You are not subscribed to any courses currently"
            self.reply(user_id, msg, "text")

        else:
            self.reply(user_id, "I'm sorry, I'm not sure how to retrieve that",
                       "text")  # TODO: Return a list of all supported get statements

    def deadlines(self, user_id, content_list):
        """Handles all requests for deadlines, with all parameters supported, returns nothing, but replies to user"""
        self.scraper.scrape(user_id, content_list)
        self.reply(user_id, "I'll go get your deadlines right now. If there are many people asking for deadlines "
                            "this might take me some time", "text")

    def delete_statements(self, user_id, content_list):
        """All delete statements. Takes in user id and what to delete. Replies with confirmation and ends"""
        if not content_list:
            self.reply(user_id, 'Please specify what to delete\nType help delete if you need help', 'text')
            return
        if content_list[0] == 'me':
            self.reply(user_id, "Are you sure? By deleting your information i will also delete all reminders you have "
                                "scheduled with me. To delete all your information, type 'yes, i agree to delete all "
                                "my information'", "text")
        elif content_list[0] == "reminder" or content_list[0] == "reminders":
            if not content_list[1:]:
                try:
                    if (self.delete_conf[user_id]['reminder']):
                        self.reply(user_id, 'Deleting all reminders', 'text')
                        self.db.delete_all_reminders(user_id)
                        self.reply(user_id, 'All reminders deleted', 'text')
                        self.delete_conf[user_id]['reminder'] = 0
                    else:
                        self.reply(user_id,
                                   'Are you sure you want to delete all your reminders?\nType <delete reminders> again to confirm',
                                   'text')
                        self.delete_conf[user_id]['reminder'] = 1
                except KeyError:
                    self.reply(user_id,
                               'Are you sure you want to delete all your reminders?\nType <delete reminders> again to confirm',
                               'text')
                    self.delete_conf[user_id] = {
                        'reminder': 1}  # Needs to be changed to an init process to allow other delete confs
            else:
                self.reply(user_id, 'Deleting reminders...', 'text')
                not_valid, complete = [], []
                for reminder in content_list[1:]:
                    try:
                        int_reminder = int(reminder)
                        try:
                            self.db.delete_reminder(self.user_reminders[user_id][int_reminder])
                            complete.append(reminder)
                        except KeyError:
                            self.reply(user_id, "Please type <get reminders> before you try to delete", 'text')
                            return
                    except ValueError:
                        not_valid.append(reminder)
                        continue
                if not_valid:
                    self.reply(user_id,
                               "The following reminders are not valid:\n" + ",".join(not_valid) + "\nPlease try again",
                               'text')
                if complete:
                    self.reply(user_id, "The following reminders were deleted:\n" + ",".join(complete), 'text')
        else:
            self.reply(user_id, "Im not sure how to delete that, are you sure you wrote it correctly?\nType "
                                "'help delete' for more information", "text")

    def set_statements(self, user_id, content_list):
        """All set statements. Takes in user id and list of message, without 'set' at List[0]. Replies and ends"""
        if not content_list:
            self.reply(user_id, 'Please specify what to set\nType help set if you need help', 'text')
            return

        if content_list[0] == "reminder" or content_list[0] == "reminders":
            if not content_list[1:]:
                self.reply(user_id, 'Please specify what to be reminded of\nType help set reminder if you need help',
                           'text')
                return
            try:
                date = content_list[-2]
                current = datetime.now()
                due_time = content_list[-1]
                due_time = self.pattern.sub(lambda m: self.rep[re.escape(m.group(0))],
                                            due_time)  # Makes any date string split with "-"
                day = current.day
                month = current.month
                year = current.year
                if date != "at":  # with date in front. Format reminder <text> at date time
                    date = self.pattern.sub(lambda m: self.rep[re.escape(m.group(0))],
                                            date)  # Makes any date string split with "-"
                    date_list = date.split("-")
                    if len(date_list) == 3:  # YYYY-MM-DD
                        if len(date_list[0]) == 2:
                            date_list[0] = "20" + date_list[0]
                        year = int(date_list[0])
                        month = int(date_list[1])
                        day = int(date_list[2])
                    elif len(date_list) == 2:  # DD-MM
                        if int(date_list[1]) < month or (int(date_list[1]) == month and int(date_list[0]) < day):
                            year += 1
                        month = int(date_list[1])
                        day = int(date_list[0])
                    else:  # DD
                        if int(date_list[0]) < day:
                            month += 1
                        day = int(date_list[0])
                    msg = " ".join(content_list[1:-3])
                else:  # without date in front. Format reminder <text> at time
                    msg = " ".join(content_list[1:-2])
                try:
                    hour, minute = [int(i) for i in due_time.split("-")]
                except ValueError:
                    self.reply(user_id, "Don't write seconds, check out the valid formats with 'help set reminder'",
                               "text")
                    return
                time = datetime(year, month, day, hour, minute)
                if time < current:
                    time = time + timedelta(days=1)
                if time < current + timedelta(minutes=10):
                    self.reply(user_id,
                               "I am sorry, I could not set the reminder '" + msg + "' as it tried to set itself to a "
                                                                                    "time in the past, or within the "
                                                                                    "next 10 minutes: " +
                               time.strftime("%Y-%m-%d %H:%M") + ". Please write it again, or in another format. "
                                                                 "If you belive this was a bug, report it with the "
                                                                 "'bug' function.",
                               "text")
                elif time > current + timedelta(weeks=60):
                    self.reply(user_id, "I am sorry, i cant remember for that long. Are you sure you ment " +
                               time.strftime("%Y-%m-%d %H:%M"), "text")
                else:
                    self.db.add_reminder(msg, time.strftime("%Y-%m-%d %H:%M:%S"), 0, user_id)
                    # Expects format "reminder $Reminder_text at YYYY-MM-DD HH:mm:ss
                    self.reply(user_id, "The reminder " + msg + " was sat at " +
                               time.strftime("%Y-%m-%d %H:%M"), "text")
            except ValueError:
                self.reply(user_id, "Im not able to set that reminder. Are you sure you wrote the message in a "
                                    "supported format? Type 'help set reminders' to see supported formats", "text")
        elif content_list[0] == 'default-time':
            if not content_list[1:]:
                self.reply(user_id, 'Please specify default-time to set', 'text')
                return
            try:
                df = int(content_list[1])
            except ValueError:
                self.reply(user_id, 'Please type in an integer as default-time', 'text')
                return
<<<<<<< HEAD
            if(self.db.set_defaulttime(user_id,df)):
                self.reply(user_id,'Your default-time was set to: '+content_list[1],'text')
=======
            if (self.db.set_defaulttime(user_id, df)):
                self.reply(user_id, 'Your default-time was set to :' + content_list[1], 'text')
>>>>>>> 949c24ba778edeb80202bfdb63227cb1e0cc7e67
            else:
                self.reply(user_id,
                           'Could not set default-time. Please check if you are using the correct format and that you are logged in. Type "help set default-time" for more help',
                           'text')
        else:
            self.reply(user_id, "I'm sorry, I'm not sure what you want me to remember", "text")

    def subscribe(self, user_id, content_list):
        """Subscribes user to course(s). Takes in user id and course(s) to be subscribed to.
        Replies with confirmation and ends"""
        if not content_list:
            self.reply(user_id, 'subscribe to what?\nType help subscribe if you need help', 'text')
            return

        self.reply(user_id, 'Subscribing to ' + ','.join(content_list) + "...", 'text')
        non_existing, already_subscribed, success_subscribed = [], [], []
        for course in content_list:
            course = course.upper()
            if self.db.course_exists(course):
                if not self.db.user_subscribed_to_course(user_id, course):
                    self.db.subscribe_to_course(user_id, course)
                    success_subscribed.append(course)
                else:
                    already_subscribed.append(course)
            else:
                non_existing.append(course)
        if non_existing:
            self.reply(user_id, 'The following course(s) do(es) not exist: ' + ','.join(non_existing), 'text')
        if already_subscribed:
            self.reply(user_id, 'You are already subscribed to ' + ','.join(already_subscribed), 'text')
        if success_subscribed:
            self.reply(user_id, 'You have successfully subscribed to ' + ','.join(success_subscribed), 'text')

    def unsubscribe(self, user_id, content_list):
        """Unsubscribes user to course(s). Takes in user id and course(s) to be subscribed to.
         Replies with confirmation and ends"""
        if not content_list:
            self.reply(user_id, 'Unsubsribe from what?\nType help unsubscribe if you need help', 'text')
            return

        self.reply(user_id, 'Unsubscribing from ' + ','.join(content_list) + "...", 'text')
        non_existing, not_subscribed, success_unsubscribed = [], [], []
        for course in content_list:
            course = course.upper()
            if self.db.course_exists(course):
                if self.db.user_subscribed_to_course(user_id, course):
                    self.db.unsubscribe(user_id, course)
                    success_unsubscribed.append(course)
                else:
                    not_subscribed.append(course)
            else:
                non_existing.append(course)
        if non_existing:
            self.reply(user_id, 'The following course(s) do(es) not exist: ' + ','.join(non_existing), 'text')
        if not_subscribed:
            self.reply(user_id, 'You are not subscribed to ' + ','.join(not_subscribed), 'text')
        if success_unsubscribed:
            self.reply(user_id, 'You have successfully unsubscribed from ' + ','.join(success_unsubscribed), 'text')

    def bug(self, user_id, content_list):
        """Bug report. Takes in user id and list of message, without 'bug' at List[0]. Replies, saves and ends"""
        if not content_list:
            self.reply(user_id, 'Please specify at least one bug\nType help bug if you need help', 'text')
            return
        with open("BUG/user_bug_reports.txt", "a", encoding='utf-8') as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M") + ";" + user_id + ": " + " ".join(content_list) + "\n")
        self.reply(user_id, "The bug was taken to my developers. One of them might contact you if they need further "
                            "help with the bug", "text")

    def request(self, user_id, content_list):
        """Requests. Takes in user id and list of message, without 'request' at List[0]. Replies, saves and ends"""
        with open("REQUEST/user_requests.txt", "a", encoding='utf-8') as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M") + ";" + user_id + ": " + " ".join(content_list) + "\n")
        self.reply(user_id, "The request was taken to my developers. I will try to make your wish come true, but keep"
                            " in mind that not all request are feasible", "text")

    def help(self, user_id, content_list):
        """Replies to the user with a string explaining the method in content_list"""
        if not content_list:
            self.reply(user_id, "Oh you need help?\nNo problem!\nFollowing commands are supported:\n"
                                "\n- Login\n- Get deadlines\n- Get exams\n- Get links\n- Get reminders"
                                "\n- Get default-time\n- Get subscribed\n- Set reminder\n- Set default-time"
                                "\n- Delete me\n- Bug\n- Request\n- Subscribe\n- Unsubscribe\n- Help"
                                "\n\nBut that's not all, there's also some more hidden commands!\nIts up to you to find"
                                " them ;)\n\n"
                                "If you want a more detailed overview over a feature, you can write 'help <feature>'. "
                                "You can try this with 'help help' now!", 'text')

        elif content_list[0] == "get":
            try:
                if content_list[1] == "deadlines" or content_list[1] == "deadline":
                    self.reply(user_id,
                               "Deadlines are fetched from It'slearning and Blackboard with the feide username and"
                               " password you entered with the 'login' command. To get the deadlines you can write"
                               " the following commands:\n\t- get deadlines\n\t- get deadlines until <DD/MM>\n"
                               "\t- get deadlines from <course>\n\t- get deadlines from <course> until <DD/MM>\n\n"
                               "Without the <> and the course code, date and month you wish", "text")

                elif content_list[1] == "exam" or content_list[1] == "exams":
                    self.reply(user_id, "I can get the exam date for any of your courses. Just write"
                                        "\n- Get exams <course_code> (<course_code2>...)", "text")

                elif content_list[1] == "link" or content_list[1] == "links":
                    self.reply(user_id, "I can give you fast links to It'slearning or Blackboard with these commands:"
                                        "\n- Get links\n- Get link Itslearning\n- Get link Blackboard", "text")
                elif content_list[1] == "reminder" or content_list[1] == "reminders":
                    self.reply(user_id, "This gives you an overview of all upcoming reminders I have in store for you."
                               , "text")
                elif content_list[1] == "default-time":
                    self.reply(user_id,
                               'Default-time decides how many days before an assigment you will be reminded by default. Get default-time shows your current default-time',
                               'text')
                else:
                    self.reply(user_id,
                               "I'm not sure that's a supported command, if you think this is a bug, please do report "
                               "it with the 'bug' function! If it something you simply wish to be added, use the "
                               "'request' function", "text")
            except IndexError:
                self.reply(user_id,
                           "To get something type:\n- get <what_to_get> (opt:<value1> <value2>...)\nType <help> for a list of what you can get",
                           "text")

        elif content_list[0] == "set":
            try:
                if content_list[1] == "reminder" or content_list[1] == "reminders":
                    self.reply(user_id, "I can give reminders to anyone who is logged in with the 'login' command. "
                                        "If you login with your feide username and password I can retrieve all your "
                                        "deadlines on It'slearning and Blackboard as well, and give you reminders to "
                                        "those when they are soon due. I will naturally never share your information with "
                                        "anyone!\n\nThe following commands are supported:\n\n"
                                        "- set reminder <Reminder text> at <Due_date>\n"
                                        "where <Due_date> can have the following formats:"
                                        "\n- YYYY-MM-DD HH:mm\n- DD-MM HH:mm\n- DD HH:mm\n- HH:mm\n"
                                        "and <Reminder text> is what "
                                        "I should tell you when the reminder is due.", "text")
                elif content_list[1] == 'default-time':
                    self.reply(user_id,
                               "I can set your default-time which decides how long before an assignment you will be reminded by default.\n\n"
                               "To set your default-time please use the following format:\n\n"
                               "- set default-time <integer>\n\n"
                               "Where <integer> can be any number of days", 'text')
                else:
                    self.reply(user_id,
                               "I'm not sure that's a supported command, if you think this is a bug, please do report "
                               "it with the 'bug' function. If it something you simply wish to be added, use the "
                               "'request' function", "text")
            except IndexError:
                self.reply(user_id,
                           "To set something type:\n- set <what_to_set> <value1> (opt:<value2>...)\nType <help> for a list of what you can set",
                           "text")

        elif content_list[0] == "delete":
            try:
                if content_list[1] == "reminder" or content_list[1] == "reminders":
                    self.reply(user_id,
                               "Do delete a specific reminder you first have to type <get reminders> to find reminder id, which will"
                               "show first <index>: reminder. To delete type:\n- delete reminder <index> (<index2>...)\n"
                               "\nTo delete all reminders type:\n- delete reminders", 'text')
                elif content_list[1] == 'me':
                    self.reply(user_id,
                               "If you want me to delete all information I have on you, type in 'delete me', and "
                               "follow the instructions i give you", "text")
                else:
                    self.reply(user_id,
                               "I'm not sure that's a supported command, if you think this is a bug, please do report "
                               "it with the 'bug' function. If it something you simply wish to be added, use the "
                               "'request' function", "text")
            except IndexError:
                self.reply(user_id,
                           "To delete something type:\n- delete <what_to_delete> (opt:<value1> <value2>...)\nType <help> for a list of what you can delete",
                           "text")


        elif content_list[0] == "help":
            self.reply(user_id, "The help method gives more detailed information about my features, and their commands"
                                ". You may type help in front of any method to get a more detailed overview of what it"
                                " does.", "text")

        elif content_list[0] == "login":
            self.reply(user_id, "You must log in for me to be able to give you reminders. If you log in with your "
                                "feide username and password I can also fetch your deadlines from blackboard and "
                                "It'slearning! \nIf you submitted wrong username or password, don't worry! I will still"
                                " remember any reminders or courses you have saved with me if you login with a new "
                                "username and password", "text")

        elif content_list[0] == "bug":
            self.reply(user_id, "If you encounter a bug please let me know! You submit a bug report with a"
                                "\n- bug <message> \n"
                                "command. If it is a feature you wish added, please use the request command instead. "
                                "\nA bug is anything from an unexpected output to no output at all. Please include as"
                                "much information as possible about how you encountered the bug, so I can recreate it",
                       "text")

        elif content_list[0] == "request":
            self.reply(user_id, "If you have a request for a new feature please let me know! You submit a feature"
                                " request with a\n- request <message> \ncommand. If you think this is already a feature"
                                ", and you encountered a bug, please use the bug command instead", "text")

        elif content_list[0] == "subscribe":
            self.reply(user_id, "You can subscribe to courses you want to get reminders from. To subscribe to a course "
                                "just write\n- subscribe <course_code> (<course_code2>...)", "text")

        elif content_list[0] == "unsubscribe":
            self.reply(user_id,
                       "You can unsubscribe to courses you dont want to get reminders from. To unsubscribe to a course "
                       "just write\n- unsubscribe <course_code> (<course_code2>...)", "text")

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
        feedback = json.loads(response.content.decode())
        if "error" in feedback:
            with open("LOG/reply_fail.txt", "a", encoding="UTF-8") as f:
                f.write(user_id + ": msg: " + msg + "; ERROR msg: " + str(feedback["error"]) + "\n")
        with open("LOG/" + user_id + "_chat.txt", "a", encoding="UTF-8") as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " Cally: " + msg + "\n")

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
        feedback = json.loads(response.content.decode())
        if "error" in feedback:
            with open("LOG/login_fail.txt", "a", encoding="UTF-8") as f:
                f.write(user_id + ": login ; ERROR msg: " + str(feedback["error"]) + "\n")

    def get_reply_url(self):
        return "https://graph.facebook.com/v2.8/me/messages?access_token=" + self.access_token
