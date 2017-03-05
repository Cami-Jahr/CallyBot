import MySQLdb
import datetime


def add_user(user_id, navn, username=None, password=None, df=0):  # test: DONE
    # add user to database
    sql = "INSERT INTO user(fbid, name, username, password, defaulttime)" \
          " VALUES('%s', '%s', '%s', '%s', '%d')" % (user_id, navn, username, password, df)
    if not user_exists(user_id):
        try:
            db = MySQLdb.connect("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
            cursor = db.cursor()
            print("try to execute add user")
            cursor.execute(sql)
            db.commit()
            print("added user")
            db.close()
        except:
            print("closed in except")


def remove_user(user_id):  # test: DONE
    # deletes user from database
    sql = """DELETE FROM user WHERE fbid=""" + str(user_id)
    if user_exists(user_id):
        try:
            db = MySQLdb.connect("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
            db.close()
        except:
            print("unsuccessful")
    else:
        print("could not find user")


def user_exists(user_id):  # test: DONE
    # returns True if user is in database
    db = MySQLdb.connect("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
    cursor = db.cursor()
    sql = """SELECT * FROM user WHERE fbid=""" + str(user_id)
    try:
        print("try to execute")
        cursor.execute(sql)
        print("executed sql")
        result = cursor.fetchall()
        db.close()
        return len(result) != 0
    except:
        db.close()
        return False


def add_course(course, coursename):  # test: DONE
    # adds course to database if it does not already exist
    sql = """INSERT INTO course(coursecode, courseName) VALUES ('%s', '%s')""" % (course, coursename)
    if not course_exists(course):
        try:
            db = MySQLdb.connect("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
            cursor = db.cursor()
            print("trying to add course")
            cursor.execute(sql)
            db.commit()
            print("added course")
            db.close()
        except:
            print("could not add course", course)
    else:
        print("course is already in database")


def remove_course(course):  # test: DONE
    # removes course from the database
    sql = """DELETE FROM course WHERE coursecode='%s'""" % str(course)
    if course_exists(course):
        try:
            db = MySQLdb.connect("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
            db.close()
            print("removed course", course)
        except:
            print("could not remove course")


def course_exists(course):  # test: DONE
    # returns if the course exists or False if it could not execute the sql
    db = MySQLdb.connect("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
    cursor = db.cursor()
    sql = """SELECT * FROM course WHERE coursecode='%s'""" % str(course)
    try:
        print("try to execute")
        cursor.execute(sql)
        print("executed sql")
        result = cursor.fetchall()
        db.close()
        return len(result) != 0
    except:
        db.close()
        return False


def subscribe_to_course(user_id, course):  # test: DONE
    # adds user to course
    # assums user and course are already in the database
    sql = """INSERT INTO subscribed (userID, course) VALUES ('%s', '%s')""" % (user_id, course)
    if not user_subscribed_to_course(user_id, course):
        try:
            db = MySQLdb.connect("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
            db.close()
        except:
            print("could not subscribe")


def user_subscribed_to_course(user_id, course):  # test: DONE
    # checks if a user is subscribed to this course
    db = MySQLdb.connect("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
    cursor = db.cursor()
    sql = """SELECT * FROM subscribed
            WHERE userID='%s' AND course='%s'""" % (user_id, course)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        # result is entire table so if result has 0 rows then the realtion dos not exist
        db.close()
        return len(result) != 0
    except:
        db.close()
        return False


def unsubscribe(user_id, course):  # test: DONE
    # deletes relation between user and course
    sql = """DELETE FROM subscribed
            WHERE userID='%s' AND course='%s'""" % (user_id, course)
    if user_subscribed_to_course(user_id, course):
        try:
            db = MySQLdb.connect("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
            db.close()
        except:
            print("could not unsubscribe")


def add_reminder(what, deadline, coursemade, user_id):  # test: DONE
    # adds a reminder to the database
    db = MySQLdb.connect("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
    cursor = db.cursor()
    # change the deadline specified by the defaulttime
    df = get_defaulttime(user_id)
    # only alter deadline if coursemade == 1
    newdeadline = deadline
    # assumes deadline is a string of format DD-MM-YYYY-HH:MM
    if coursemade == 1:
        newdeadline = fix_new_deadline(deadline, df)
    print(newdeadline)
    sql = "INSERT INTO reminder(what, deadline, coursemade, userID) " \
          "VALUES ('%s' " % what + ", " + "'" + newdeadline + "'" + ", '%d', '%s')" % (coursemade, user_id)
    print(sql)
    try:
        print("trying to execute")
        cursor.execute(sql)
        db.commit()
        print("added reminder")
        db.close()
    except:
        print("could not add reminder")
        db.close()


def get_defaulttime(user_id):  # test: DONE
    # gets the defaulttime set by the user of how long before a deadline the user wish to reminded of it
    db = MySQLdb.connect("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
    cursor = db.cursor()
    sql = """SELECT defaulttime FROM user WHERE fbid='%s'""" % user_id
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        dt = result[0][0]
        cursor.close()
        return dt
    except:
        # could possibly be changed to whatever we decide wil be the defaulttime
        db.close()
        return 0


def set_defaulttime(user_id, df):  # test: DONE
    # set the defaulttime of a user
    db = MySQLdb.connect("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
    cursor = db.cursor()
    sql = """UPDATE user SET defaulttime=%d WHERE fbid='%s'""" % (df, user_id)
    try:
        print("trying to execute")
        cursor.execute(sql)
        db.commit()
        print("set defaulttime")
        db.close()
    except:
        print("could not set defaulttime")
        db.close()


def clean_course(user_id):
    # deletes all relations a user has to courses
    # this is possibly quicker than just calling unsubscrib for all courses a user has
    db = MySQLdb.connect("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
    cursor = db.cursor()
    sql = """DELETE FROM subscribed WHERE userID='%s'""" % str(user_id)
    try:
        cursor.execute(sql)
        db.commit()
        db.close()
    except:
        db.close()


def get_all_courses(user_id):  # if returnvalue is [] then user is not subscribed to any courses or sql failed
    #  finds all courses a user is subscribed to
    db = MySQLdb.connect("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
    cursor = db.cursor()
    sql = """SELECT course FROM subscribed WHERE userID=%s""", user_id
    out = []
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        db.close()
        # results is now a list of lists only containing the coursecode [[coursecode]]
        #  want the result to be [coursecode]
        for row in results:
            out.append(row[0])
    except:
        db.close()
    return out


def get_reminders(user_id):
    # costum reminders
    db = MySQLdb.connect("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
    cursor = db.cursor()
    # find all reminders for a user where coursemade == 0
    sql = """SELECT what, deadline, coursemade FROM reminder
                    WHERE userID=%s AND coursemade=0""", user_id
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        db.close()
        # results format: [[what, deadline]]
        return format_reminders(results)
    except:
        return []


def format_reminders(reminders):
    out = ""
    for row in reminders:
        out += "you have", row[0], "at", row[1], "\n"
    return out


def fix_new_deadline(deadline, df):  # tested: Done
    # deadline is supposed to be a string of format 'YYYY-MM-DD HH:MM:SS'
    daysofmonth = {"1": 31, "2": 28, "3": 31, "4": 30, "5": 31, "6": 30,
                   "7": 31, "8": 31, "9": 30, "10": 31, "11": 30, "12": 31, "13": 29}
    year = int(deadline[:4])
    month = int(deadline[5:7])
    day = int(deadline[8:10])
    print(year, month, day)
    # assumes df is not larger than 28 days
    if day - df < 1:
        # fix day/month/year accordingly
        if month == 1:
            # set back year
            year -= 1
            month = 12
        else:
            month -= 1
        if year % 4 == 0 and month == 2:
            day += daysofmonth["13"] - df
        else:
            day += daysofmonth[str(month)] - df
    else:
        day -= df
    if day < 10:
        day = "0" + str(day)
    else:
        day = str(day)
    if month < 10:
        month = "0" + str(month)
    else:
        month = str(month)
    # might change time of day to a fixed time, because many deadlines are at 23:59:00
    out = str(day) + "-" + str(month) + "-" + str(year) + deadline[10:]
    return out


# unnessisary
def make_datetime_object(deadline):  # tested: Done
    # turns string of format DD-MM-YYYY-HH:MM into a datetime object
    year = int(deadline[6:10])
    month = int(deadline[3:5])
    day = int(deadline[:2])
    hour = int(deadline[11:13])
    minnutt = int(deadline[14:16])
    # datetime.ctime() returns string of format (dayofweek month day HH:MM)
    return datetime.datetime(year, month, day, hour, minnutt)


def test_deadline():
    deadline = '01-03-2012 23:59:00'
    deadline = fix_new_deadline(deadline, 1)
    datetime_deadline = make_datetime_object(deadline)


def test_user():
    # add_user('1214261795354790', 'test', 'test', 'test')
    # print(user_exists('1425853194113509'))
    remove_user('00000000000000')
    # add_user('000000000000', 'navn', 'bruker', 'passord', 0)
    print(user_exists('000000000000'))


def test_course():
    add_course('tdt4100', 'java')
    print(course_exists('tdt4100'))
    remove_course('tdt4100')


def test_subscribe():
    # subscribe_to_course('000000000000', 'tdt4100')
    unsubscribe('000000000000', 'tdt4100')
    print(user_subscribed_to_course('000000000000', 'tdt4100'))


def test_reminder():
    # have also tested if all reminders to a user is deleted if a user is deleted
    add_reminder('dummy course assignment', '2017-03-05 20:00:00', 1, '000000000000')


def test_df():
    print(get_defaulttime('000000000000'))
    set_defaulttime('000000000000', 3)
    print(get_defaulttime('000000000000'))


def test_methods():
    # test_deadline()
    test_user()
    # test_course()
    # test_subscribe()
    # test_reminder()
    # test_df()

test_methods()

