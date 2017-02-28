import MySQLdb
import datetime

class Cally_DB():

    def __init__(self, host, username, password, db_name):
        self.db = MySQLdb.connect(host, username, password, db_name)
        self.cursor = self.db.cursor()

    def removeUser(self, user_id):
        # deletes user from database
        sql = """DELETE * FROM user WHERE userID=%s""", user_id
        if self.userExists(user_id):
            try:
                self.cursor.execute(sql)
            except:
                pass

    def userExists(self, user_id):
        # returns True if user is in database
        sql = """SELECT * FROM user WHERE userID=%s""", user_id
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return len(result) != 0
        except:
            return False

    def addCourse(self, course, coursename):
        # adds course to database if it does not already exist
        sql = """INSERT INTO course (coursecode, courseName) VALUES (%s, %s)""", (course, coursename)
        if not self.courseExists(course):
            try:
                self.cursor.execute(sql)
            except:
                pass

    def removeCourse(self, course):
        # removes course from the database
        sql = """DELETE * FROM course WHERE coursecode=%s""", course
        if self.courseExists(course):
            try:
                self.cursor.execute(sql)
            except:
                pass

    def courseExists(self, course):
        # returns if the course exists or False if it could not execute the sql
        sql = """SELECT * FROM course
              WHERE coursecode = %s""", course
        try:
            # Execute the SQL command
            self.cursor.execute(sql)
            # Fetch all the rows in a list of lists.
            result = self.cursor.fetchall()
            return len(result) != 0
        except:
            return False

    def subscribeToCourse(self, user_id, course):
        # adds user to course
        # assums user and course are already in the database
        sql = """INSERT INTO subscribed (userID, course) VALUES (%s, %s)""", (user_id, course)
        if not self.userSubscribedToCourse(user_id, course):
            try:
                self.cursor.execute(sql)
            except:
                pass

    def userSubscribedToCourse(self, user_id, course):
        # checks if a user is subscribed to this course
        sql = """SELECT * FROM subscribed
                WHERE userID=%s AND course=%s""", (user_id, course)
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            # result is entire table so if result has 0 rows then the realtion dos not exist
            return len(result) != 0
        except:
            return False

    def unSubscribe(self, user_id, course):
        # deletes relation between user and course
        sql = """DELETE * FROM subscribed
                WHERE userID=%s AND course=%s""", (user_id, course)
        if self.userSubscribedToCourse(user_id, course):
            try:
                self.cursor.execute(sql)
            except:
                pass

    def addReminder(self, what, deadline, coursemade, user_id):
        # adds a reminder to the database
        # change the deadline specified by the defaulttime
        df = self.getDefaulttime(user_id)
        # only alter deadline if coursemade == 1
        newdeadline = deadline
        # assumes deadline is a string of format DD-MM-YYYY-HH:MM
        if coursemade == 1:
            newdeadline = fixnewdeadline(deadline, df)
        newdeadline = makedatetimeobject(newdeadline)
        sql = """INSERT INTO reminder (what, deadline, coursemade, user_id) VALUES (%s, %s, %s, %s)""", (what, newdeadline, coursemade, user_id)
        try:
            self.cursor.execute(sql)
        except:
            pass

    def getDefaulttime(self, user_id):
        # gets the defaulttime set by the user of how long before a deadline the user wish to reminded of it
        sql = """SELECT defaulttime FROM user WHERE fbid=%s""", user_id
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            dt = result[0][4]
            return dt
        except:
            # could possibly be changed to whatever we decide wil be the defaulttime
            return 0

    def cleanCourse(self, user_id):
        # deletes all relations a user has to courses
        # this is possibly quicker than just calling unsubscrib for all courses a user has
        sql = """DELETE * FROM subscribed WHERE userID=%s""", user_id
        try:
            self.cursor.execute(sql)
        except:
            pass

    def getAllCourses(self, user_id):  # if returnvalue is [] then user is not subscribed to any courses or sql failed
        # finds all courses a user is subscribed to
        sql = """SELECT course FROM subscribed WHERE userID=%s""", user_id
        out = []
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            # results is now a list of lists only containing the coursecode [[coursecode]]
            # want the result to be [coursecode]
            for row in results:
                out.append(row[0])
        except:
            pass
        return out

    def getReminders(self, user_id):
        # costum reminders
        # find all reminders for a user where coursemade == 0
        sql = """SELECT what, deadline, coursemade FROM reminder
                WHERE userID=%s AND coursemade=0""", user_id
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            # results format: [[what, deadline]]
            return results
        except:
            return []

    def formatReminders(self, user_id):  # I know, not a good method name
        reminders = self.getReminders(user_id)
        out = ""
        for row in reminders:
            out += "you have", row[0], "at", row[1], "\n"
        return out


def fixnewdeadline(deadline, df):
    daysofmonth = {"1": 31, "2": 28, "3": 31, "4": 30, "5": 31, "6": 30,
                   "7": 31, "8": 31, "9": 30, "10": 31, "11": 30, "12": 31}
    year = int(deadline[6:10])
    month = int(deadline[3:5])
    day = int(deadline[:2])
    # assumes df is not larger than 28 days
    if day - df < 1:
        # fix day/month/year accordingly
        if month - 1 < 1:
            # set back year
            year -= 1
            month = 12
        else:
            month -= 1
            day += daysofmonth[str(month)]
    out = str(day - df) + "-" + str(month) + "-" + str(year) + deadline[10:]
    return out


def makedatetimeobject(deadline):
    # turns string of format DD-MM-YYYY-HH:MM into a datetime object
    year = int(deadline[6:10])
    month = int(deadline[3:5])
    day = int(deadline[:2])
    hour = int(deadline[11:13])
    minnutt = int(deadline[14:16])
    # datetime.ctime() returns string of format (dayofweek month day HH:MM)
    return datetime.datetime(year, month, day, hour, minnutt)
