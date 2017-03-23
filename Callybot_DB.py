import MySQLdb
from datetime import datetime, timedelta

class CallybotDB:
    """Class object for access to Callybots database"""
    # Cally_Database turned into an object class

    def __init__(self, host, username, password, DB_name):
        """Initializes CallybotDB, sets up connection to the database"""
        print("trying to connect to " + host)
        self.db = MySQLdb.connect(host, username, password, DB_name)
        print("successful connect to database " + DB_name)
        self.cursor = self.db.cursor()

    def close(self):
        """close connection to database, void"""
        self.db.close()

    def get_credential(self, user_id):
        """Get all saved information about a user,
        :returns a list"""
        sql = "SELECT * FROM user WHERE fbid=" + str(user_id)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results[0]

    def add_user(self, user_id, navn, username=None, password=None, df=1):  # test: DONE
        """Add a user to the database, void"""
        if username is None or password is None:  # remember to change default value of username and password to null
            # print("no username or password")
            sql = "INSERT INTO user(fbid, name, defaulttime)" \
                  " VALUES('%s', '%s', '%d')" % (user_id, navn, df)
        else:
            sql = "INSERT INTO user(fbid, name, username, password, defaulttime)" \
                  " VALUES('%s', '%s', '%s', '%s', '%d')" % (user_id, navn, username, password, df)
        if not self.user_exists(user_id):
            try:
                # print("try to execute add user")
                self.cursor.execute(sql)
                self.db.commit()
            # print("added user")
            except:
                print("closed in except")

    def remove_user(self, user_id):  # test: DONE
        """Deletes a user from the database, void"""
        # deletes user from database
        sql = """DELETE FROM user WHERE fbid=""" + str(user_id)
        if self.user_exists(user_id):
            try:
                self.cursor.execute(sql)
                self.db.commit()
            except:
                print("unsuccessful")
        else:
            print("could not find user")

    def user_exists(self, user_id):  # test: DONE
        """Checks if a user is already in the database,
        :returns Boolean value"""
        sql = """SELECT * FROM user WHERE fbid=""" + str(user_id)
        try:
            print("try to execute")
            self.cursor.execute(sql)
            print("executed sql")
            result = self.cursor.fetchall()
            return len(result) != 0
        except:
            return False

    def get_users(self):
        """Returns all existing users"""
        sql = """SELECT * FROM user"""
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        except:
            return []

    def set_username_password(self, user_id, username, password):
        """Sets username and password for a user that already exists, void"""
        sql = """UPDATE user SET username='%s' AND password='%s' WHERE fbid='%s'""" % (username, password, user_id)
        if self.user_exists(user_id):
            try:
                self.cursor.execute(sql)
                self.db.commit()
            except:
                print("could not set username and password for user", user_id)

    def add_course(self, course, coursename):  # test: DONE
        """Adds course to database if it does not already exist, void"""
        sql = """INSERT INTO course(coursecode, courseName) VALUES ('%s', '%s')""" % (course, coursename)
        if not self.course_exists(course):
            try:
                # print("trying to add course")
                self.cursor.execute(sql)
                self.db.commit()
                print("added course")
            except:
                print("could not add course", course)
        else:
            print("course is already in database")

    def remove_course(self, course):  # test: DONE
        """Deletes course from the database if it is in the database, void"""
        # removes course from the database
        sql = """DELETE FROM course WHERE coursecode='%s'""" % str(course)
        if self.course_exists(course):
            try:
                self.cursor.execute(sql)
                self.db.commit()
            # print("removed course", course)
            except:
                print("could not remove course")

    def course_exists(self, course):  # test: DONE
        """Checks if a course is in the database,
        :returns Boolean value,
        Default return value is False indicating cursor could not execute or course is not in database"""
        sql = """SELECT * FROM course WHERE coursecode='%s'""" % str(course)
        try:
            # print("try to execute")
            self.cursor.execute(sql)
            # print("executed sql")
            result = self.cursor.fetchall()
            return len(result) != 0
        except:
            return False

    def subscribe_to_course(self, user_id, course):  # test: DONE
        """Creates a relation between course and user in table subscribed if the relation does not already exist,
         assumes both course and user is already in the database, void"""
        sql = """INSERT INTO subscribed (userID, course) VALUES ('%s', '%s')""" % (user_id, course)
        if not self.user_subscribed_to_course(user_id, course):
            try:
                self.cursor.execute(sql)
                self.db.commit()
            except:
                print("could not subscribe")

    def user_subscribed_to_course(self, user_id, course):  # test: DONE
        """Checks if a user is subscribed to a course,
        :returns Boolean value"""
        sql = """SELECT * FROM subscribed
                WHERE userID='%s' AND course='%s'""" % (user_id, course)
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            # result is entire table so if result has 0 rows then the realtion dos not exist
            return len(result) != 0
        except:
            return False

    def unsubscribe(self, user_id, course):  # test: DONE
        """Deletes the relation between user and course if the relation exists, void"""
        # deletes relation between user and course
        sql = """DELETE FROM subscribed
                WHERE userID='%s' AND course='%s'""" % (user_id, course)
        if self.user_subscribed_to_course(user_id, course):
            try:
                self.cursor.execute(sql)
                self.db.commit()
            except:
                print("could not unsubscribe")

    def add_reminder(self, what, deadline, coursemade, user_id):  # test: DONE
        """Add reminder to the database,
        what: <String> whatever user wants to be reminded of,
        deadline: <'YYYY-MM-DD HH:MM> whenever user wants to be reminded of it,
        coursemade: <Boolean> True if this reminder is an assignment, False if costum reminder,
        user_id: <String> the user who wants to reminded of what,
        void"""
        # change the deadline specified by the defaulttime
        # print(what, deadline, coursemade, user_id)
        df = self.get_defaulttime(user_id)
        # only alter deadline if coursemade == 1
        newdeadline = deadline.replace('.', '-')
        # assumes deadline is a string of format 'YYYY-MM-DD hh:mm:ss'
        if coursemade:
            newdeadline = fix_new_deadline(deadline, df)
        sql = "INSERT INTO reminder(what, deadline, userID, coursemade) " \
              "VALUES ('%s', '%s', '%s', '%d')" % (what, newdeadline, user_id, coursemade)
        # print(sql)
        try:
            # print("trying to execute")
            self.cursor.execute(sql)
            self.db.commit()
        # print("added reminder")
        except:
            print("could not add reminder")

    def get_defaulttime(self, user_id):  # test: DONE
        """:returns a users defaulttime <Integer>"""
        # gets the defaulttime set by the user of how long before a deadline the user wish to reminded of it
        sql = """SELECT defaulttime FROM user WHERE fbid='%s'""" % user_id
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            dt = result[0][0]
            return dt
        except:
            # could possibly be changed to whatever we decide wil be the defaulttime
            return -1

    def set_defaulttime(self, user_id, df):  # test: DONE
        """Sets a user's defaulttime to be df <Integer>, void"""
        sql = """UPDATE user SET defaulttime=%d WHERE fbid='%s'""" % (df, user_id)
        try:
            # print("trying to execute")
            self.cursor.execute(sql)
            self.db.commit()
            return True
        # print("set defaulttime")
        except:
            print("could not set defaulttime")
            return False

    def clean_course(self, user_id):
        """Deletes all relations a user has to its courses, void"""
        # deletes all relations a user has to courses
        # this is possibly quicker than just calling unsubscrib for all courses a user has
        sql = """DELETE FROM subscribed WHERE userID='%s'""" % str(user_id)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            print("could not execute")

    def get_all_courses(self, user_id):
        """returns all courses a user is subscribed to,
        :returns a list of courses,
        [] (empty list) if a user is not subscribed to any courses or if method could not execute"""
        sql = """SELECT course FROM subscribed WHERE userID='%s'""" % user_id
        out = []
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            # results is now a list of lists only containing the coursecode [[coursecode]]
            #  want the result to be [coursecode]
            for row in results:
                out.append(row[0])
        except:
            print("could not get courses")
        return out

    def get_reminders(self, user_id):
        """:returns all reminders a user has"""
        sql = """SELECT what, deadline, coursemade, RID FROM reminder
                        WHERE userID='%s' ORDER BY deadline ASC""" % user_id
        try:
            self.cursor.execute(sql)
            
            results = self.cursor.fetchall()
            # print(results)
            # results format: ((what, deadline, coursemade),)
            return results
        except:
            return []

    def delete_all_reminders(self, user_id):
        """Deletes all reminders a user has,
        :returns a list of lists"""
        sql = """DELETE FROM reminder
                        WHERE userID='%s'""" % user_id
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            self.db.commit()
            # print(results)
            # results format: ((what, deadline, coursemade),)
            return results
        except:
            return []

    def delete_all_coursemade_reminders(self, user_id):
        # costum reminders
        # find all reminders for a user
        sql = """DELETE FROM reminder
                        WHERE userID='%s' AND coursemade = 1""" % user_id
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            self.db.commit()
            # print(results)
            # results format: ((what, deadline, coursemade),)
            return results
        except:
            return []

    def delete_reminder(self, RID):
        """Deletes reminder with this RID,
        :returns a list of lists"""
        sql = """DELETE FROM reminder
                        WHERE RID='%s'""" % RID
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            self.db.commit()
            # print(results)
            # results format: ((what, deadline, coursemade),)
            return results
        except:
            return []

    def get_all_reminders(self):
        """Returns all reminders in the database,
        :returns [[deadline, userID, what, coursemade, RID]...]"""
        sql = """SELECT deadline, userID, what, coursemade, RID FROM reminder"""
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            return results
        except:
            return []


def fix_new_deadline(deadline, df):  # tested: Done
    """:returns deadline minus df days """
    # deadline is supposed to be a string of format 'YYYY-MM-DD HH:MM:SS'
    return (datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S") - timedelta(days=df)).strftime("%Y-%m-%d %H:%M:%S")

c = CallybotDB("mysql.stud.ntnu.no", "joachija", "Tossu796", "ingritu_callybot")
from time import sleep
c.get_reminders()