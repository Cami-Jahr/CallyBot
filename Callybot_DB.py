import MySQLdb


class CallybotDB:
	# Cally_Database turned into an object class

	def __init__(self, host, username, password, DB_name):
		print("trying to connect")
		self.db = MySQLdb.connect(host, username, password, DB_name)
		print("successful connect")
		self.cursor = self.db.cursor()

	def close(self):
		self.db.close()

	def add_user(self, user_id, navn, username=None, password=None, df=0):  # test: DONE
		# add user to database
		if username is None or password is None:  # remember to change default value of username and password to null
			print("no username or password")
			sql = "INSERT INTO user(fbid, name, defaulttime)" \
				  " VALUES('%s', '%s', '%d')" % (user_id, navn, df)
		else:
			sql = "INSERT INTO user(fbid, name, username, password, defaulttime)" \
				  " VALUES('%s', '%s', '%s', '%s', '%d')" % (user_id, navn, username, password, df)
		if not self.user_exists(user_id):
			try:
				print("try to execute add user")
				self.cursor.execute(sql)
				self.db.commit()
				print("added user")
			except:
				print("closed in except")

	def remove_user(self, user_id):  # test: DONE
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
		# returns True if user is in database
		sql = """SELECT * FROM user WHERE fbid=""" + str(user_id)
		try:
			print("try to execute")
			self.cursor.execute(sql)
			print("executed sql")
			result = self.cursor.fetchall()
			return len(result) != 0
		except:
			return False

	def set_username_password(self, user_id, username, password):
		# adds username and password to a user if attributes are null
		sql = """UPDATE user SET username='%s' AND password='%s' WHERE fbid='%s'""" % (username, password, user_id)
		if self.user_exists(user_id):
			try:
				self.cursor.execute(sql)
				self.db.commit()
			except:
				print("could not set username and password for user", user_id)

	def add_course(self, course, coursename):  # test: DONE
		# adds course to database if it does not already exist
		sql = """INSERT INTO course(coursecode, courseName) VALUES ('%s', '%s')""" % (course, coursename)
		if not self.course_exists(course):
			try:
				print("trying to add course")
				self.cursor.execute(sql)
				self.db.commit()
				print("added course")
			except:
				print("could not add course", course)
		else:
			print("course is already in database")

	def remove_course(self, course):  # test: DONE
		# removes course from the database
		sql = """DELETE FROM course WHERE coursecode='%s'""" % str(course)
		if self.course_exists(course):
			try:
				self.cursor.execute(sql)
				self.db.commit()
				print("removed course", course)
			except:
				print("could not remove course")

	def course_exists(self, course):  # test: DONE
		# returns if the course exists or False if it could not execute the sql
		sql = """SELECT * FROM course WHERE coursecode='%s'""" % str(course)
		try:
			print("try to execute")
			self.cursor.execute(sql)
			print("executed sql")
			result = self.cursor.fetchall()
			return len(result) != 0
		except:
			return False

	def subscribe_to_course(self, user_id, course):  # test: DONE
		# adds user to course
		# assums user and course are already in the database
		sql = """INSERT INTO subscribed (userID, course) VALUES ('%s', '%s')""" % (user_id, course)
		if not self.user_subscribed_to_course(user_id, course):
			try:
				self.cursor.execute(sql)
				self.db.commit()
			except:
				print("could not subscribe")

	def user_subscribed_to_course(self, user_id, course):  # test: DONE
		# checks if a user is subscribed to this course
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
		# adds a reminder to the database
		# change the deadline specified by the defaulttime
		df = self.get_defaulttime(user_id)
		# only alter deadline if coursemade == 1
		newdeadline = deadline
		# assumes deadline is a string of format 'YYYY-MM-DD hh:mm:ss'
		if coursemade:
			newdeadline = fix_new_deadline(deadline, df)
		sql = "INSERT INTO reminder(what, deadline, userID, coursemade) " \
			  "VALUES ('%s', '%s', '%s', '%d')" % (what, newdeadline, user_id, coursemade)
		print(sql)
		try:
			print("trying to execute")
			self.cursor.execute(sql)
			self.db.commit()
			print("added reminder")
		except:
			print("could not add reminder")

	def get_defaulttime(self, user_id):  # test: DONE
		# gets the defaulttime set by the user of how long before a deadline the user wish to reminded of it
		sql = """SELECT defaulttime FROM user WHERE fbid='%s'""" % user_id
		try:
			self.cursor.execute(sql)
			result = self.cursor.fetchall()
			dt = result[0][0]
			return dt
		except:
			# could possibly be changed to whatever we decide wil be the defaulttime
			return 0

	def set_defaulttime(self, user_id, df):  # test: DONE
		# set the defaulttime of a user
		sql = """UPDATE user SET defaulttime=%d WHERE fbid='%s'""" % (df, user_id)
		try:
			print("trying to execute")
			self.cursor.execute(sql)
			self.db.commit()
			print("set defaulttime")
		except:
			print("could not set defaulttime")

	def clean_course(self, user_id):
		# deletes all relations a user has to courses
		# this is possibly quicker than just calling unsubscrib for all courses a user has
		sql = """DELETE FROM subscribed WHERE userID='%s'""" % str(user_id)
		try:
			self.cursor.execute(sql)
			self.db.commit()
		except:
			print("could not execute")

	def get_all_courses(self, user_id):  # if returnvalue is [] then user is not subscribed to any courses or sql failed
		#  finds all courses a user is subscribed to
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
		# costum reminders
		# find all reminders for a user where coursemade == 0
		sql = """SELECT what, deadline, coursemade FROM reminder
                        WHERE userID='%s'""" % user_id
		try:
			self.cursor.execute(sql)
			results = self.cursor.fetchall()
			print(results)
			# results format: [[what, deadline]]
			return results
		except:
			return []

	def get_all_reminders(self):
		sql = """SELECT deadline, userID, what, coursemade FROM reminder"""
		try:
			self.cursor.execute(sql)
			results = self.cursor.fetchall()
			# results format: [[what, deadline]]
			return results
		except:
			return []


def fix_new_deadline(deadline, df):  # tested: Done
	print(deadline, df)
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
	out = str(year) + "-" + str(month) + "-" + str(day) + deadline[10:]
	print(out)
	return out
