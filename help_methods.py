import ilearn_scrape
import iblack_scrape
import requests
import MySQLdb


def get_course_info(course):
    # Other information might be fetched later, by adding in the findall statement, or add other findall statements
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


def IL_scrape(user_id):
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
        for line in info:
            msg += line[0] + "\n" + line[1].rsplit(" ", 2)[0] + "\nDue date: " + line[2] + "\n\n"
    except:
        msg="error"
    # disconnect from server
    db.close()
    return msg

def BB_scrape(user_id):
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
        msg=""
        for line in info:
            msg += line[0] + "\nin " + line[1] + "\nDue date: " + line[2] + "\n\n"
    except:
        msg="error"
    # disconnect from server
    db.close()
    return msg
