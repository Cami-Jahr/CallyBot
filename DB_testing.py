import unittest
import Callybot_DB as CDB


class Test_Callybot_DB(unittest.TestCase):  # alot of failures still

    def test_add_user(self):
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        user_id = '0000'
        name = 'testbruker'
        # check if user does not exist
        self.assertFalse(db.user_exists(user_id))
        # add user
        db.add_user(user_id, name)
        # check that user exist now
        self.assertTrue(db.user_exists(user_id))
        db.close()
        print("tested add user")

    def test_add_course(self):
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        coursecode = 'WOF4120'
        coursename = 'hundelufting'
        self.assertFalse(db.course_exists(coursecode))
        db.add_course(coursecode, coursename)
        self.assertTrue(db.course_exists(coursecode))
        db.close()
        print("tested add course")

    def test_subscribe(self):
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        user_id = '0000'
        course = 'WOF4120'
        self.assertFalse(db.user_subscribed_to_course(user_id, course))
        db.subscribe_to_course(user_id, course)
        self.assertTrue(db.user_subscribed_to_course(user_id, course))
        db.close()
        print("tested subscribe")

    def test_set_defaulttime(self):
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        user_id = '0000'
        new_df = 3
        old_df = db.get_defaulttime(user_id)
        self.assertEqual(old_df, 0)
        db.set_defaulttime(user_id, new_df)
        self.assertEqual(new_df, db.get_defaulttime())
        db.close()
        print("tested set defaulttime")

    def test_make_custom_reminder(self):
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        what = 'gå på abakus revyen'
        deadline = '2017-03-16 19:00:00'
        coursemade = False
        user_id = '0000'
        self.assertEqual(db.get_reminders(user_id), [])
        db.add_reminder(what, deadline, coursemade, user_id)
        self.assertEqual(db.get_reminders(user_id), "you have " + what + " at " + deadline + "\n")
        db.close()
        print("tested make custom reminder")

    def test_unsubscribe(self):
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        user_id = '0000'
        course = 'WOF4120'
        self.assertTrue(db.user_subscribed_to_course(user_id, course))
        db.unsubscribe(user_id, course)
        self.assertFalse(db.user_subscribed_to_course(user_id, course))
        db.close()
        print("tested usubscribe")

    def test_remove_course(self):
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        course = 'WOF4120'
        self.assertTrue(db.course_exists(course))
        db.remove_course(course)
        self.assertFalse(db.course_exists(course))
        db.close()
        print("tested remove course")

    def test_get_all_courses(self):
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        user_id = '0000'
        c1, n1 = 'WOF4120', 'hundelufting'
        c2, n2 = 'PNG2191', 'kanoner'
        db.add_course(c1, n1)
        db.add_course(c2, n2)
        db.subscribe_to_course(user_id, c1)
        db.subscribe_to_course(user_id, c2)
        ac = db.get_all_courses(user_id)
        self.assertEqual(ac, [c1, c2])
        db.close()
        print("tested get all courses")

    def test_foreignkeys(self):
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        c1 = 'WOF4120'
        c2 = 'PNG2191'
        user_id = '0000'
        db.remove_course(c1)
        # check if user-course relation is gone after c1 is removed
        self.assertFalse(db.user_subscribed_to_course(user_id, c1))
        self.assertFalse(db.course_exists(c1))
        db.remove_user(user_id)
        self.assertFalse(db.user_subscribed_to_course(user_id, c2))
        self.assertTrue(db.course_exists(c2))
        self.assertEqual(db.get_reminders(user_id), "")
        db.remove_course(c2)
        db.close()
        print("tested foreign keys")


if __name__ == '__main__':
    unittest.main()


'''
Current functions and relevant information 23/03/17

import Callybot_DB


c = Callybot_DB.CallybotDB("mysql.stud.ntnu.no", "joachija", "Tossu796", "ingritu_callybot")
u = "1550995208259075"
co = "TEST"
con = "_test"
from time import sleep

print(c.remove_user(u))
print(c.add_user(u, "j",))
print(c.get_credential(u))
print(c.add_reminder("text", "2020-10-10 10:10:10", 0, u))
print(c.get_defaulttime(u))
print(c.set_defaulttime(u, 2))
print(c.get_all_courses(u))
print(c.get_reminders(u))
print(c.delete_all_coursemade_reminders(u))
print(c.delete_all_reminders(u))
print(c.delete_reminder(1))
print(c.clean_course(u))

print(c.user_exists(u))
print(c.set_username_password(u, "J", "l"))
print(c.get_credential(u))
print("\n\n")

print(c.add_course(co, con))
print(c.remove_course(co))
print(c.course_exists(co))

print(c.subscribe_to_course(u, co))
print(c.user_subscribed_to_course(u, co))
print(c.unsubscribe(u, co))
print(c.get_all_reminders())
print(c.get_user_ids())
'''