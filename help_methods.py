import ilearn_scrape
import iblack_scrape
import requests
import MySQLdb


def get_course_info(course):
    # Other information may be fetched later, by reading from the info data
    info = requests.get('http://www.ime.ntnu.no/api/course/'+course).json()
    exam_date = info["course"]["assessment"][0]["date"]
    return course, exam_date


def get_user_info(access_token,user_id): #Get user info from profile
    user_details_url="https://graph.facebook.com/v2.8/"+str(user_id)
    user_details_params={'fields':'first_name,last_name,profile_pic','access_token':access_token}
    user_details = requests.get(user_details_url,user_details_params).json()
    lastname=user_details['last_name']
    firstname=user_details['first_name']
    picture=user_details['profile_pic']
    return firstname,lastname,picture


def IL_scrape(user_id, course, until):
    course = course.upper()
    # Open database connection
    db = MySQLdb.connect("mysql.stud.ntnu.no","halvorkm","kimjong","ingritu_callybot" )

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = "SELECT * FROM user WHERE fbid="+str(user_id)
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        result=results[0]
        info = ilearn_scrape.scrape(result[2], result[3])
        msg=""
        max_day = int(until.split("/")[0])
        max_month = int(until.split("/")[1])
        # Max time it should get deadlines to
        if course == "ALL":
            for line in info:
                due_day = int(line[3].split(".")[0])
                due_month = int(line[3].split(".")[1])
                if max_month > due_month or (max_month == due_month and max_day >= due_day): # Before max deadlines
                    msg += line[0] + "\nin " + line[1] + " " + line[2] + "\nDue date: " + line[3] + " " + line[4] + "\n\n"  # Format to default ###NOTE### does support time as line[4]
        else:
            for line in info:
                due_day = int(line[3].split(".")[0])
                due_month = int(line[3].split(".")[1])
                if line[1] == course and (max_month > due_month or (max_month == due_month and max_day >= due_day)): # Before  max deadlines and correct course
                    msg += line[0] + "\nin " + line[1] + " " + line[2] + "\nDue date: " + line[3] + " " + line[4] + "\n\n"  # Format to default ###NOTE### does support time as line[4]
    except IndexError:
        msg = "SQLerror"
    # disconnect from server
    db.close()
    return msg


def BB_scrape(user_id, course, until):
    course = course.upper()
    # Open database connection
    db = MySQLdb.connect("mysql.stud.ntnu.no","halvorkm","kimjong","ingritu_callybot" )

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = "SELECT * FROM user WHERE fbid="+str(user_id)
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        result=results[0]
        info = iblack_scrape.scrape(result[2], result[3])
        msg = ""
        max_day = int(until.split("/")[0])
        max_month = int(until.split("/")[1])
        # Max time it should get deadlines to
        if course == "ALL":
            for line in info:
                due_day = int(line[3].split(".")[0])
                due_month = int(line[3].split(".")[1])
                if max_month > due_month or (max_month == due_month and max_day >= due_day): # Before  max deadlines
                    msg += line[0] + "\nin " + line[1] + " " + line[2] + "\nDue date: " + line[3] + "\n\n"  # Format to default ###NOTE### do NOT support time as line[4]
        else:
            for line in info:
                due_day = int(line[3].split(".")[0])
                due_month = int(line[3].split(".")[1])
                if line[1] == course and (max_month > due_month or (max_month == due_month and max_day >= due_day)): # Before  max deadlines and correct course
                    msg += line[0] + "\nin " + line[1] + " " + line[2] + "\nDue date: " + line[3] + "\n\n"  # Format to default ###NOTE### do NOT support time as line[4]
    except IndexError:
        msg = "SQLerror"
    # disconnect from server
    db.close()
    return msg
