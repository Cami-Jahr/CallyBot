

def addCourse(cursor, course, coursename):
    # adds course to database if it does not already exist
    sql = """INSERT INTO course (coursecode, courseName) VALUES (%s, %s)""", (course, coursename)
    if not courseExists(cursor, course):
        try:
            cursor.execute(sql)
        except:
            pass


def removeCourse(cursor, course):
    # removes course from the database
    sql = """DELETE * FROM course WHERE coursecode=%s""", course
    if courseExists(cursor, course):
        try:
            cursor.execute(sql)
        except:
            pass

def courseExists(cursor, course):
    # returns if the course exists or False if it could not execute the sql
    sql = """SELECT * FROM course
          WHERE coursecode = %s""", course
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Fetch all the rows in a list of lists.
        result = cursor.fetchall()
        return len(result) != 0
    except:
        return False


def subscribeToCourse(cursor, user_id, course):
    # adds user to course
    # assums user and course are already in the database
    sql = """INSERT INTO subscribed (userID, course) VALUES (%s, %s)""", (user_id, course)
    if not userSubscribedToCourse(cursor, user_id, course):
        try:
            cursor.execute(sql)
        except:
            pass


def userSubscribedToCourse(cursor, user_id, course):
    # checks if a user is subscribed to this course
    sql = """SELECT * FROM subscribed
            WHERE userID=%s AND course=%s""", (user_id, course)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        # result is entire table so if result has 0 rows then the realtion dos not exist
        return len(result) != 0
    except:
        return False


def unSubscribe(cursor, user_id, course):
    # deletes relation between user and course
    sql = """DELETE * FROM subscribed
            WHERE userID=%s AND course=%s""", (user_id, course)
    if userSubscribedToCourse(cursor, user_id, course):
        try:
            cursor.execute(sql)
        except:
            pass


def addReminder(cursor, what, deadline, coursemade, user_id):  # not yet finished
    # adds a reminder to the database
    # change the deadline specified by the defaulttime
    df = getDefaulttime(cursor, user_id)
    # do not know which kind of date object mySQL wil accept as datetime yet
    # only alter deadline if coursemade == 1
    newdeadline = deadline
    if coursemade == 1:
        newdeadline = deadline - df  # this is PSAUDOCODE, kind of
    sql = """INSERT INTO reminder (what, deadline, coursemade, user_id) VALUES (%s, %s, %s, %s)""", (what, newdeadline, coursemade, user_id)
    try:
        cursor.execute(sql)
    except:
        pass


def getDefaulttime(cursor, user_id):
    # gets the defaulttime set by the user of how long before a deadline the user wish to reminded of it
    sql = """SELECT defaulttime FROM user WHERE fbid=%s""", user_id
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        dt = result[0][4]
        return dt
    except:
        # could possibly be changed to whatever we decide wil be the defaulttime
        return 0


def cleanCourse(cursor, user_id):
    # deletes all relations a user has to courses
    # this is possibly quicker than just calling unsubscrib for all courses a user has
    sql = """DELETE * FROM subscribed WHERE userID=%s""", user_id
    try:
        cursor.execute(sql)
    except:
        pass


def getAllCourses(cursor, user_id):  # if returnvalue is [] then user is not subscribed to any courses or sql failed
    # finds all courses a user is subscribed to
    sql = """SELECT course FROM subscribed WHERE userID=%s""", user_id
    out = []
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        # results is now a list of lists only containing the coursecode [[coursecode]]
        # want the result to be [coursecode]
        for row in results:
            out.append(row[0])
    except:
        pass
    return out


def getReminders(cursor, user_id):
    # costum reminders
    # find all reminders for a user where coursemade == 0
    sql = """SELECT what, deadline, coursemade FROM reminder
            WHERE userID=%s AND coursemade=0""", user_id
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        # results format: [[what, deadline]]
        return results
    except:
        return []


def formatReminders(cursor, user_id):  # I know, not a good method name
    reminders = getReminders(cursor, user_id)
    out = ""
    for row in reminders:
        out += "you have", row[0], "at", row[1], "\n"
    return out
