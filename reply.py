import requests
import help_methods
import re
from datetime import datetime, timedelta
import json
import scraper


class Reply:
    """The reply class handles all incoming messages. The input is the user id and the json element of the message.
    The class handles it with the 'arbitrate' function, and replies to the user with a logical reply"""

    def __init__(self, access_token=None, db=None):
        self.access_token = access_token
        self.db = db
        self.scraper = scraper.Scraper(self, self.db)
        self.scraper.start()

        self.rep = {"/": "-", "\\": "-", ":": "-", ";": "-", ",": "-", ".": "-"}
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
            return True
        content_lower = content.lower()
        content_list = content_lower.split()
        msg = ""
        reply_type = ""
        # ------------ COMMANDS --------------
        if content_list[0] == "get":
            msg = self.get_statements(user_id, content_list[1:])
            reply_type = "text"

        elif content_list[0] == "exam" or content_list[0] == "exams":
            msg = self.get_statements(user_id, content_list)
            reply_type = "text"

        elif content_list[0] == "deadline" or content_list[0] == "deadlines":
            msg = self.get_statements(user_id, content_list)
            reply_type = "text"

        elif content_list[0] == "link" or content_list[0] == "links":
            msg = self.get_statements(user_id, content_list)
            reply_type = "text"

        elif content_list[0] == "profile":
            msg = self.profile(user_id)
            reply_type = "text"

        elif content_list[0] == "subscribed" or content_list[0] == 'classes' \
                or content_list[0] == 'class' or content_list[0] == 'courses' or content_list[0] == 'course':
            msg = self.get_statements(user_id, content_list)
            reply_type = "text"

        elif content_list[0] == "set":
            msg = self.set_statements(user_id, content_list[1:])
            reply_type = "text"

        elif content_list[0] == "delete":
            msg = self.delete_statements(user_id, content_list[1:])
            reply_type = "text"

        elif content_lower == "login":
            msg = self.login(user_id)
            reply_type = "text"

        elif content_list[0] == "bug":
            msg = self.bug(user_id, content_list[1:])
            reply_type = "text"

        elif content_list[0] == "request":
            msg = self.request(user_id, content_list[1:])
            reply_type = "text"

        elif content_list[0] == 'subscribe':
            msg = self.subscribe(user_id, content_list[1:])
            reply_type = "text"

        elif content_list[0] == 'unsubscribe':
            msg = self.unsubscribe(user_id, content_list[1:])
            reply_type = "text"

        # Delete confirmation
        elif content_lower == "yes, i agree to delete all my information":
            self.db.remove_user(user_id)
            msg = "I have now deleted all your information. If you have any feedback to give me, please " \
                  "do so with the 'request' function.\nI hope to see you again!."
            reply_type = "text"

        elif content_list[0] == "help":
            msg = self.help(user_id, content_list[1:])
            reply_type = "text"

        elif content_lower == "hint":
            msg = "This will be removed at launch!\n\n- Juicy gif\n- Juice gif\n- Who am I?\n- Who are you?\n- " \
                  "Chicken\n- Hello\n- Good bye"
            reply_type = "text"

        # ------------ EASTER EGGS --------------
        elif content_lower == "hello" or content_lower == "hi":
            msg = "http://cdn.ebaumsworld.com/mediaFiles/picture/2192630/83801651.gif"
            reply_type = "image"

        elif content_lower == "chicken":
            msg = "Did I scare ya?"
            reply_type = "text"

        elif content_lower == "juice gif":
            msg = "https://i.makeagif.com/media/10-01-2015/JzrY-u.gif"
            reply_type = "image"

        elif content_lower == "juicy gif":
            msg = "http://68.media.tumblr.com/tumblr_m9pbdkoIDA1ra12qlo1_400.gif"
            reply_type = "image"

        elif content_lower == "who are you?":
            msg = "I am Cally, your lord and savior"
            self.reply(user_id, msg, 'text')
            msg = "https://folk.ntnu.no/halvorkm/callysavior.jpg"
            reply_type = "image"

        elif content_lower == "who am i?":
            fname, lname, pic = help_methods.get_user_info(self.access_token, user_id)  # Get userinfo
            msg = "You are " + fname + " " + lname + " and you look like this:"
            self.reply(user_id, msg, 'text')
            msg = pic
            reply_type = "image"

        elif content_lower == "good bye" or content_lower == "bye" or content_lower == "farewell":
            msg = "Bye now!"
            self.reply(user_id, msg, 'text')
            msg = "http://i.imgur.com/NBUNSSG.gif"
            reply_type = "image"

        elif content_lower == "rick" or content_lower == "roll" or content_lower == "rick roll" \
                or content_lower == "never gonna give you up" or content_lower == "never gonna let you down":
            msg = "Uh huh"
            self.reply(user_id, msg, 'text')
            msg = "https://media.giphy.com/media/Vuw9m5wXviFIQ/giphy.gif"
            reply_type = "image"

        elif content_lower == "thanks" or content_lower == "thank you" or content_lower == "ty":
            msg = "You're welcome!"
            reply_type = "text"

        # ------------ GET STARTED --------------
        elif content_lower == "start_new_chat":
            msg = "_____@_____\nThis is alpha version of the bot, if you encounter anything unusual, " \
                  "please report it as detailed as possible. If you wish a feature added please inform" \
                  " us about it. Please do report anything you can, from typos, to " \
                  "poor sentences, to hard to access information, to any 'shortcuts' you would like to " \
                  "see. Thank you for helping with testing of " \
                  "the bot!\n\n- The developers of CallyBot."
            self.reply(user_id, msg, 'text')
            fname, lname, pic = help_methods.get_user_info(self.access_token, user_id)  # Get userinfo
            self.db.add_user(user_id, fname + lname)
            msg = "Welcome " + fname + "!\nMy name is CallyBot, but you may call me Cally :)\nI will keep you up to " \
                                       "date on your upcoming deadlines on itslearning and Blackboard. Type 'login' " \
                                       "or use the menu to get started. \nIf you need help, or want to know more " \
                                       "about what I can do for you, just type 'help'.\n\nPlease do enjoy!"
            reply_type = "text"

        # ------------- DEVELOPER - --------------
        # NOT TO BE SHOWN TO USERS, FOR DEVELOPER USE ONLY, do not add to hint/help etc
        elif content_list[0] == "developer":
            msg = self.developer_statements(user_id, content_list[1:])
            reply_type = "text"

        # -------------- DEFAULT ----------------
        elif content_lower == "most_likely_command_was_not_true":
            msg = "Im sorry I was not able to help you. Please type 'help' to see my supported commands, or 'help " \
                  "<feature>' to get information about a specific feature, or visit my " \
                  "wiki https://github.com/Folstad/TDT4140/wiki/Commands.\nIf you believe you found a bug, or have a " \
                  "request for a new feature or command, please use the 'bug' and 'request' commands"
            reply_type = "text"
        else:
            if data_type == "text":
                # Typo correction prompt
                self.make_typo_correction_buttons(user_id, content_lower)

            else:
                msg = content
                reply_type = data_type
        if msg:
            self.reply(user_id, msg, reply_type)
            return msg, reply_type

    def developer_statements(self, user_id, content_list):
        if user_id not in ('1214261795354796', '1212139502226885', '1439762959401510', '1550995208259075'):
            return "Sorry, but these commands are only for developers. Type 'help' or visit " \
                   "https://github.com/Folstad/TDT4140/wiki/Commands for a list of supported commands"

        elif not content_list:
            return "Specify developer command: id, requests, bugs, users or announcement"

        elif content_list[0] == "id":
            return str(user_id)

        elif content_list[0] == "requests" or content_list[0] == "request":
            with open("REQUEST/user_requests.txt", "r", encoding='utf-8') as f:
                all_requests = f.readlines()
                msg = ""
                for request in all_requests:
                    if len(msg) + len(request) >= 600:
                        self.reply(user_id, msg, "text")
                        msg = request
                    else:
                        msg += request
            return msg

        elif content_list[0] == "bugs" or content_list[0] == "bug":
            with open("BUG/user_bug_reports.txt", "r", encoding='utf-8') as f:
                reports = f.readlines()
                msg = ""
                for report in reports:
                    if len(msg) + len(report) >= 600:
                        self.reply(user_id, msg, "text")
                        msg = report
                    else:
                        msg += report
            return msg

        elif content_list[0] == "users" or content_list[0] == "user":
            msg = ""
            ids = self.db.get_user_ids()
            for id in ids:
                if len(msg) + len(id) < 600:
                    msg += id + '\n'
                else:
                    self.reply(user_id, msg, "text")
                    msg = id
            return msg

        elif content_list[0] == 'announcement':
            users = self.db.get_announcement_subscribers()
            for user in users:
                self.reply(user, 'Announcement:\n' + ' '.join(content_list[1:]).capitalize(), 'text')

        else:
            return "Unknown command"

    def get_statements(self, user_id, content_list):
        """All get statements. Takes in user id and list of message, without 'get' at List[0]. Replies and ends"""
        if not content_list:
            return "Please specify what to get. Type 'help' or visit " \
                   "https://github.com/Folstad/TDT4140/wiki/Commands for a list of supported commands"

        elif content_list[0] == "deadline" or content_list[0] == "deadlines":
            return self.deadlines(user_id, content_list)

        elif content_list[0] == "profile":
            return self.profile(user_id)

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
            else:
                msg = "You don't appear to have any reminders scheduled with me"
            return msg

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
            return msg

        elif content_list[0] == "default-time" or content_list[0] == "default":
            df = self.db.get_defaulttime(user_id)
            if df == -1:
                return "To check default-time, please login."
            else:
                return "Your default-time is: " + str(df) + " day(s)"

        elif content_list[0] == "link" or content_list[0] == "links":
            try:
                if content_list[1] == "itslearning":
                    return "http://ilearn.sexy"
                elif content_list[1] == "blackboard":
                    return "http://iblack.sexy"
                else:
                    return "http://iblack.sexy\nhttp://ilearn.sexy"
            except IndexError:
                return "http://iblack.sexy\nhttp://ilearn.sexy"

        elif content_list[0] == "subscribe" or content_list[0] == "subscribed" or content_list[0] == 'classes' \
                or content_list[0] == 'class' or content_list[0] == 'courses' or content_list[0] == 'course':
            courses = self.db.get_all_courses(user_id)
            if courses:
                msg = "You are subscribed to:\n"
                for course in courses:
                    msg += course + "\n"
            else:
                msg = "You are not subscribed to any courses currently"
            return msg

        else:
            self.make_typo_correction_buttons(user_id, " ".join(["get"] + content_list))

    def deadlines(self, user_id, content_list):
        """Handles all requests for deadlines, with all parameters supported, returns nothing, but replies to user"""
        if self.db.user_exists(user_id):
            self.scraper.scrape(user_id, content_list)
            return "I'll go get your deadlines right now. If there are many people asking for deadlines this might" \
                   " take me some time."
        else:
            return "You don't appear to be logged in. To use the 'get deadlines' function you need to log" \
                   "in with your feide username and password with the 'login' command."

    def delete_statements(self, user_id, content_list):
        """All delete statements. Takes in user id and what to delete. Replies with confirmation and ends"""
        if not content_list:
            return "Please specify what to delete. Type 'help' or visit " \
                   "https://github.com/Folstad/TDT4140/wiki/Commands for a list of supported commands"

        elif content_list[0] == 'me':
            return "Are you sure? By deleting your information i will also delete all reminders you have " \
                   "scheduled with me. To delete all your information, type 'yes, i agree to delete all " \
                   "my information'."

        elif content_list[0] == "reminder" or content_list[0] == "reminders":
            if not content_list[1:]:
                try:
                    if self.delete_conf[user_id]['reminder']:
                        self.reply(user_id, 'Deleting all reminders.', 'text')
                        self.db.delete_all_reminders(user_id)
                        self.delete_conf[user_id]['reminder'] = 0
                        return 'All reminders deleted.'
                    else:
                        self.delete_conf[user_id]['reminder'] = 1
                        return 'Are you sure you want to delete all your reminders?\nType <delete reminders> ' \
                               'again to confirm'

                except KeyError:
                    self.delete_conf[user_id] = {
                        'reminder': 1}  # Needs to be changed to an init process to allow other delete confs
                    return 'Are you sure you want to delete all your reminders?\nType ' \
                           '<delete reminders> again to confirm'
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
                            return "Please type <get reminders> before you try to delete."
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
            self.make_typo_correction_buttons(user_id, " ".join(["delete"] + content_list))

    def set_statements(self, user_id, content_list):
        """All set statements. Takes in user id and list of message, without 'set' at List[0]. Replies and ends"""
        if not content_list:
            return "Please specify what to set. Type 'help' or visit " \
                   "https://github.com/Folstad/TDT4140/wiki/Commands for a list of supported commands"

        elif content_list[0] == "reminder" or content_list[0] == "reminders":
            if not content_list[1:]:
                return 'Please specify what to be reminded of\nType help set reminder if you need help'
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
                    return "Don't write seconds, check out the valid formats with 'help set reminder'"
                time = datetime(year, month, day, hour, minute)
                if time < current:
                    time = time + timedelta(days=1)
                if time < current + timedelta(minutes=10):
                    self.reply(user_id,
                               "I am sorry, I could not set the reminder '" +
                               msg.capitalize() + "' as it tried to set itself to a time in the past, or within the "
                                                  "next 10 minutes: " +
                               time.strftime("%Y-%m-%d %H:%M") + ". Please write it again, or in another format. "
                                                                 "If you believe this was a bug, report it with the "
                                                                 "'bug' function.",
                               "text")
                elif time > current + timedelta(weeks=60):
                    self.reply(user_id, "I am sorry, i cant remember for that long. Are you sure you ment " +
                               time.strftime("%Y-%m-%d %H:%M"), "text")
                else:
                    self.db.add_reminder(msg.capitalize(), time.strftime("%Y-%m-%d %H:%M:%S"), 0, user_id)
                    # Expects format "reminder $Reminder_text at YYYY-MM-DD HH:mm:ss
                    self.reply(user_id, "The reminder " + msg.capitalize() + " was sat at " +
                               time.strftime("%Y-%m-%d %H:%M") + ". Reminders will be checked every 5 minutes.", "text")
            except ValueError:
                self.reply(user_id, "Im not able to set that reminder. Are you sure you wrote the message in a "
                                    "supported format? Type 'help set reminders' to see supported formats.", "text")

        elif content_list[0] == 'class' or content_list[0] == 'classes' or content_list[0] == 'course' or \
                        content_list[0] == 'courses':
            return self.subscribe(user_id, content_list[1:])

        elif content_list[0] == 'default-time' or content_list[0] == 'default':
            if not content_list[1:]:
                return 'Please specify default-time to set.'
            try:
                df = int(content_list[1])
            except ValueError:
                return 'Please type in an integer as default-time.'
            if self.db.set_defaulttime(user_id, df):
                return 'Your default-time was set to: ' + content_list[1] + " day(s)"
            else:
                return 'Could not set default-time. Please check if you are using the correct format ' \
                       'and that you are logged in. Type "help set default-time" for more help'
        else:
            self.make_typo_correction_buttons(user_id, " ".join(["set"] + content_list))

    def subscribe(self, user_id, content_list):
        """Subscribes user to course(s). Takes in user id and course(s) to be subscribed to.
        Replies with confirmation and ends"""
        if not content_list:
            return "Please specify what to subscribe to. Type 'help' or visit " \
                   "https://github.com/Folstad/TDT4140/wiki/Commands for a list of supported commands"
        if content_list[0] == 'announcement' or content_list[0] == 'announcements':
            result = self.db.subscribe_announcement(user_id)
            if result:
                return 'You are now subscribed to announcements from my developers'
            else:
                return 'You are already subscribed to announcements from my developers'

        self.reply(user_id, 'Subscribing to ' + ','.join(content_list).upper() + "...", 'text')
        non_existing, already_subscribed, success_subscribed = [], [], []
        for course in content_list:
            course = course.upper()
            if self.db.course_exists(course):
                if not self.db.user_subscribed_to_course(user_id, course):
                    self.db.subscribe(user_id, course)
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
            return "Please specify what to unsubscribe to. Type 'help' or visit " \
                   "https://github.com/Folstad/TDT4140/wiki/Commands for a list of supported commands"
        if content_list[0] == 'announcement':
            result = self.db.unsubscribe_announcement(user_id)
            if result:
                return 'You are now unsubscribed from announcements from my developers'
            else:
                return 'You are already unsubscribed from announcements from my developers'
        if content_list[0] == 'all':
            result = self.db.clean_course(user_id)
            if result != 0:
                return 'Successfully unsubscribed you from all your courses'
            else:
                return 'Could not unsubscribe you from your courses'

        self.reply(user_id, 'Unsubscribing from ' + ','.join(content_list).upper() + "...", 'text')
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
            return "Please specify the bug you found. Type 'help' or visit " \
                   "https://github.com/Folstad/TDT4140/wiki/Commands for a list of supported commands"
        with open("BUG/user_bug_reports.txt", "a", encoding='utf-8') as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M") + ";" + user_id + ": " + " ".join(content_list) + "\n")
        return "The bug was taken to my developers. One of them might contact you if they need further " \
               "help with the bug."

    def request(self, user_id, content_list):
        """Requests. Takes in user id and list of message, without 'request' at List[0]. Replies, saves and ends"""
        if not content_list:
            return "Please specify your request. Type 'help' or visit " \
                   "https://github.com/Folstad/TDT4140/wiki/Commands for a list of supported commands"
        with open("REQUEST/user_requests.txt", "a", encoding='utf-8') as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M") + ";" + user_id + ": " + " ".join(content_list) + "\n")
        return "The request was taken to my developers. I will try to make your wish come true, but keep" \
               " in mind that not all request are feasible."

    def help(self, user_id, content_list):
        """Replies to the user with a string explaining the method in content_list"""
        if not content_list:
            return "Oh you need help?\nNo problem!\nFollowing commands are supported:\n" \
                   "\n- Login\n- Get deadlines\n- Get exams\n- Get links\n- Get reminders" \
                   "\n- Get default-time\n- Get subscribed\n- Set reminder\n- Set default-time" \
                   "\n- Delete me\n- Delete reminder\n- Bug\n- Request\n- Subscribe\n- Unsubscribe\n- " \
                   "subscribe announcement\n- unsubscribe announcement\n- " \
                   "Help\n\nThere is also a persistent menu to the left of the input field, it has shortcuts to some " \
                   "of the commands!\n\nBut that's not all, there are also some more hidden commands!\nIt " \
                   "is up to you to find them ;)\n\nIf you want a more detailed overview over a feature, you can " \
                   "write 'help <feature>'. You can try this with 'help help' now!."

        elif content_list[0] == "get":
            try:
                if content_list[1] == "subscribe" or content_list[1] == "subscribed":
                    return "The 'Get subscribed' command will give you a list of all your subscribed courses." \
                           " When you are subscribed to a course, it's deadlines will automatically be added to your" \
                           " reminders, and you will get the registered exam dates for it with the 'Get exams'" \
                           " command. For more info on subscriptions, type 'Help subscribe'."

                if content_list[1] == "deadlines" or content_list[1] == "deadline":
                    return "Deadlines are fetched from It'slearning and Blackboard with the feide username and" \
                           " password you entered with the 'login' command. To get the deadlines you can write" \
                           " the following commands:\n\t- get deadlines\n\t- get deadlines until <DD/MM>\n" \
                           "\t- get deadlines from <course>\n\t- get deadlines from <course> until <DD/MM>\n\n" \
                           "Without the <> and the course code, date and month you wish."

                elif content_list[1] == "exam" or content_list[1] == "exams":
                    return "I can get the exam date for any of your courses. Just write" \
                           "\n- Get exams <course_code> (<course_code2>...)."

                elif content_list[1] == "link" or content_list[1] == "links":
                    return "I can give you fast links to It'slearning or Blackboard with these commands:" \
                           "\n- Get links\n- Get link Itslearning\n- Get link Blackboard."

                elif content_list[1] == "reminder" or content_list[1] == "reminders":
                    return "This gives you an overview of all upcoming reminders I have in store for you."

                elif content_list[1] == "default-time" or content_list[1] == "default":
                    return 'Default-time decides how many days before an assigment you will be reminded by default. ' \
                           'Get default-time shows your current default-time',
                else:
                    return "I'm not sure that's a supported command, if you think this is a bug, please do report " \
                           "it with the 'bug' function! If it something you simply wish to be added, use the " \
                           "'request' function."
            except IndexError:
                return "To get something type:\n- get <what_to_get> (opt:<value1> <value2>...)\nType <help> for a " \
                       "list of what you can get"

        elif content_list[0] == "set":
            try:
                if content_list[1] == "reminder" or content_list[1] == "reminders":
                    return "I can give reminders to anyone who is logged in with the 'login' command. " \
                           "If you login with your feide username and password I can retrieve all your " \
                           "deadlines on It'slearning and Blackboard as well, and give you reminders to " \
                           "those when they are soon due. I will naturally never share your information with " \
                           "anyone!\n\nThe following commands are supported:\n\n" \
                           "- set reminder <Reminder text> at <Due_date>\n" \
                           "where <Due_date> can have the following formats:" \
                           "\n- YYYY-MM-DD HH:mm\n- DD-MM HH:mm\n- DD HH:mm\n- HH:mm\n" \
                           "and <Reminder text> is what " \
                           "I should tell you when the reminder is due. I will check " \
                           "reminders every 5 minutes."

                elif content_list[1] == 'default-time' or content_list[1] == 'default':
                    return "I can set your default-time which decides how long before an" \
                           " assignment you will be reminded by default.\n\n" \
                           "To set your default-time please use the following format:\n\n" \
                           "- set default-time <integer>\n\nWhere <integer> can be any number of days."

                else:
                    return "I'm not sure that's a supported command, if you think this is a bug, please do report " \
                           "it with the 'bug' function. If it something you simply wish to be added, use the " \
                           "'request' function."
            except IndexError:
                return "To set something type:\n- set <what_to_set> <value1> (opt:<value2>...)\nType" \
                       " <help> for a list of what you can set"

        elif content_list[0] == "delete":
            try:
                if content_list[1] == "reminder" or content_list[1] == "reminders":
                    return "Do delete a specific reminder you first have to type <get reminders> to find reminder " \
                           "id, which will" \
                           "show first <index>: reminder. To delete type:\n- delete reminder <index> (<index2>...)\n" \
                           "\nTo delete all reminders type:\n- delete reminders."
                elif content_list[1] == 'me':
                    return "If you want me to delete all information I have on you, type in 'delete me', and " \
                           "follow the instructions i give you."
                else:
                    return "I'm not sure that's a supported command, if you think this is a bug, please do report " \
                           "it with the 'bug' function. If it something you simply wish to be added, use the " \
                           "'request' function."
            except IndexError:
                return "To delete something type:\n- delete <what_to_delete> (opt:<value1> <value2>...)\nType " \
                       "<help> for a list of what you can delete"

        elif content_list[0] == "help":
            return "The help method gives more detailed information about my features, and their commands" \
                   ". You may type help in front of any method to get a more detailed overview of what it does."

        elif content_list[0] == "login":
            return "You must log in for me to be able to give you reminders. If you log in with your " \
                   "feide username and password I can also fetch your deadlines from blackboard and " \
                   "It'slearning! \nIf you submitted wrong username or password, don't worry! I will still" \
                   " remember any reminders or courses you have saved with me if you login with a new " \
                   "username and password."

        elif content_list[0] == "bug":
            return "If you encounter a bug please let me know! You submit a bug report with a" \
                   "\n- bug <message> \n" \
                   "command. If it is a feature you wish added, please use the request command instead. " \
                   "\nA bug is anything from an unexpected output to no output at all. Please include as" \
                   "much information as possible about how you encountered the bug, so I can recreate it"

        elif content_list[0] == "request":
            return "If you have a request for a new feature please let me know! You submit a feature" \
                   " request with a\n- request <message> \ncommand. If you think this is already a " \
                   "feature, and you encountered a bug, please use the bug command instead."

        elif content_list[0] == "subscribe":
            return "You can subscribe to courses you want to get reminders from. To subscribe to a course " \
                   "just write\n- subscribe <course_code> (<course_code2>...)."

        elif content_list[0] == "unsubscribe":
            return "You can unsubscribe to courses you don't want to get reminders from. To unsubscribe to a course " \
                   "just write\n- unsubscribe <course_code> (<course_code2>...)."

        elif content_list[0] == "reminder" or content_list[0] == "reminders":
            return "There is no 'reminder' command, but type 'Set reminder' to add a new reminder, or 'Get" \
                   " reminders' to see all currently active reminders. If you want more info on the format" \
                   " of 'Set reminder', type 'help Set reminder'."

        elif content_list[0] == "deadlines" or content_list[0] == "deadline":
            return "Type 'Get deadlines' to get a full overview of all of your deadlines on it's learning and" \
                   " blackboard! You need to log in to use this command."

        else:
            self.make_typo_correction_buttons(user_id, " ".join(["help"] + content_list))

    def process_data(data):
        """Classifies data type and extracts the data. Returns [data_type, content]"""
        try:
            content = data['entry'][0]['messaging'][0]['message']  # Pinpoint content
            if 'quick_reply' in content:  # Check if Button reply
                content = content['quick_reply']['payload']  # Extract reply
                data_type = 'text'
            elif 'text' in content:  # Check if text
                content = content['text']  # Extract text
                data_type = 'text'
            elif 'attachments' in content:  # Check if attachment
                content = content['attachments'][0]
                data_type = content['type']  # Extract attachment type
                if data_type in ('image', 'audio', 'video', 'file'):  # Extract payload based on type
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
            except KeyError:
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
            return True
        response = requests.post(self.get_reply_url(), json=data)
        feedback = json.loads(response.content.decode())
        with open("LOG/" + user_id + "_chat.txt", "a", encoding="UTF-8") as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " Cally: " + msg + "\n")
        if "error" in feedback:
            with open("LOG/reply_fail.txt", "a", encoding="UTF-8") as f:
                f.write(user_id + ": msg: " + msg + "; ERROR msg: " + str(feedback["error"]) + "\n")

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
                        "text": "By logging in you acknowledge that your user information will be stored in an "
                                "encrypted database.",
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

    def profile(self, user_id):
        first_name, last_name, pic = help_methods.get_user_info(self.access_token, user_id)
        msg = "Hello {} {}!\n".format(first_name, last_name)
        subscribed = self.db.get_all_courses(user_id)
        if subscribed:
            msg += "You are subscribed to the following classes: "
            for i, course in enumerate(subscribed):
                if i < len(subscribed) - 1:
                    msg += "{}, ".format(course)
                else:
                    msg += "{}\n".format(course)
        else:
            msg += "You are not subscribed to any courses\n"
        reminders = self.db.get_reminders(user_id)
        if reminders:
            msg += "These are your active reminders:\n\n"
            for row in reminders:
                what = row[0]
                deadline = row[1].strftime("%Y-%m-%d %H:%M")
                new = "{} at {}\n\n".format(what, deadline)
                if len(msg) + len(new) > 600:
                    self.reply(user_id, msg, "text")
                    msg = new
                else:
                    msg += new
        else:
            msg += "You do not have any active reminders"
        return msg

    def make_typo_correction_buttons(self, user_id, content_lower):
        """Help method for typo correction prompt: Makes 'Yes' and 'No' button for user. Yes button carries most likely
        query. No carries 'most_likely_command_was_not_true'"""
        most_likely_cmd = help_methods.get_most_similar_command(content_lower)
        nr_command = len(most_likely_cmd.split())
        nr_auxiliary_text = len(content_lower.split()) - nr_command
        if nr_auxiliary_text:
            total_msg = most_likely_cmd + " " + " ".join(content_lower.split()[-nr_auxiliary_text:])
        else:
            total_msg = most_likely_cmd
        message = "Did you mean to write '{}'?".format(total_msg)
        data = {
            "recipient": {"id": user_id},
            "message": {
                "text": message,
                "quick_replies": [{
                    "content_type": "text",
                    "title": "Yes",
                    "payload": most_likely_cmd,
                    "image_url": "http://i.imgur.com/JcMP9XD.png"
                },
                    {
                        "content_type": "text",
                        "title": "No",
                        "payload": "most_likely_command_was_not_true",
                        "image_url": "http://i.imgur.com/wrzzfNr.png"
                    }]
            }
        }
        response = requests.post(self.get_reply_url(), json=data)
        feedback = json.loads(response.content.decode())
        if "error" in feedback:
            with open("LOG/quick_reply_errors.txt", "a", encoding="UTF-8") as f:
                f.write(user_id + ": msg: " + content_lower + ". Assumed: " + most_likely_cmd + "; ERROR msg: "
                        + str(feedback["error"]) + "\n")

    def get_reply_url(self):
        return "https://graph.facebook.com/v2.8/me/messages?access_token=" + self.access_token
