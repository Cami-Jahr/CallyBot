import unittest
import callybot_database as CDB
from datetime import datetime


class TestCallybotDB(unittest.TestCase):
    def test_a_add_user(self):  # 200 OK
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        user_id = '0000'
        username = 'rubbish'
        password = 'trash'
        user2 = '1111'
        user3 = '2222'
        user4 = '3333'
        # check user does not exist
        self.assertFalse(db.user_exists(user_id))
        creds = db.get_credential(user_id)
        self.assertTrue(len(creds) == 0)
        # check if callybot could add user
        self.assertTrue(db.add_user(user_id) != 0)
        # check user now exist
        self.assertTrue(db.user_exists(user_id))
        # check that callybot does not add a user that is already in the database
        self.assertTrue(db.add_user(user_id) == 0)
        creds = db.get_credential(user_id)
        self.assertEqual(creds[0], user_id)
        self.assertEqual(creds[1], None)
        self.assertEqual(creds[2], None)
        self.assertEqual(creds[3], 1)
        # test update username and password, testing if it is done or not
        self.assertTrue(db.set_username_password(user_id, username, password) != 0)
        # test get credentials
        creds = db.get_credential(user_id)
        self.assertEqual(creds[0], user_id)
        self.assertEqual(creds[1], username)
        self.assertEqual(creds[2], password)
        self.assertEqual(creds[3], 1)
        # test user2, user3 and user4
        self.assertFalse(db.user_exists(user2))
        self.assertTrue(db.add_user(user2, username) != 0)
        self.assertTrue(db.user_exists(user2))
        creds = db.get_credential(user2)
        self.assertEqual(creds[0], user2)
        self.assertEqual(creds[1], None)
        self.assertEqual(creds[2], None)
        self.assertEqual(creds[3], 1)
        # user3
        self.assertFalse(db.user_exists(user3))
        self.assertTrue(db.add_user(user3, username, password) != 0)
        self.assertTrue(db.user_exists(user3))
        creds = db.get_credential(user3)
        self.assertEqual(creds[0], user3)
        self.assertEqual(creds[1], username)
        self.assertEqual(creds[2], password)
        self.assertEqual(creds[3], 1)
        # user4
        self.assertFalse(db.user_exists(user4))
        self.assertTrue(db.add_user(user4, username, password, 2) != 0)
        self.assertTrue(db.user_exists(user4))
        creds = db.get_credential(user4)
        self.assertEqual(creds[0], user4)
        self.assertEqual(creds[1], username)
        self.assertEqual(creds[2], password)
        self.assertEqual(creds[3], 2)
        db.close()
        print("tested add user")

    def test_b_add_course(self):  # 200 OK
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        coursecode = 'WOF4120'
        coursename = 'hundelufting'
        # check course does not exist
        self.assertFalse(db.course_exists(coursecode))
        # check that callybot could add course
        self.assertTrue(db.add_course(coursecode, coursename) != 0)
        # check course now exist
        self.assertTrue(db.course_exists(coursecode))
        # check that callybot does not add a course already in database
        self.assertTrue(db.add_course(coursecode, coursename) == 0)
        db.close()
        print("tested add course")

    def test_c_subscribe(self):  # 200 OK
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        user_id = '0000'
        course = 'WOF4120'
        badcourse = 'TUL4321'
        baduser = '321'
        self.assertFalse(db.user_exists(baduser))
        self.assertFalse(db.course_exists(badcourse))
        # check user cannot subscribe to bad course
        self.assertTrue(db.subscribe(user_id, badcourse) == 0)
        # check bad user cannot subscribe to course
        self.assertTrue(db.subscribe(baduser, course) == 0)
        # check bad user cannot subscribe to bad course
        self.assertTrue(db.subscribe(baduser, badcourse) == 0)
        # check that callybot can make a user subscribed to a course
        self.assertTrue(db.subscribe(user_id, course) != 0)
        # check that callybot does not make relation if it already exists
        self.assertTrue(db.subscribe(user_id, course) == 0)
        db.close()
        print("tested subscribe")

    def test_d_set_defaulttime(self):  # 200 OK
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        user_id = '0000'
        baduser = '321'
        new_df = 3
        old_df = db.get_defaulttime(user_id)
        self.assertEqual(old_df, 1)
        self.assertTrue(db.set_defaulttime(user_id, new_df) != 0)
        self.assertEqual(new_df, db.get_defaulttime(user_id))
        self.assertEqual(db.get_defaulttime(baduser), 0)
        db.close()
        print("tested set defaulttime")

    def test_e_make_custom_reminder(self):  # must also test for not ok values
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        what = 'gå på abakus revyen'
        deadline = '2020-03-16 19:00:00'
        dt = datetime(2020, 3, 16, 19, 0)
        coursemade = False
        user_id = '0000'
        baduser = '321'
        self.assertEqual(db.get_reminders(user_id), ())
        self.assertEqual(db.get_reminders(baduser), ())
        self.assertTrue(db.add_reminder(what, deadline, coursemade, user_id) != 0)
        reminders = db.get_reminders(user_id)
        get_what = reminders[0][0]
        get_datetime = reminders[0][1]
        get_coursemade = reminders[0][2]
        self.assertEqual(get_what, what)
        self.assertEqual(get_datetime, dt)
        self.assertEqual(get_coursemade, coursemade)
        # test for bad user
        self.assertTrue(db.add_reminder(what, deadline, coursemade, baduser) == 0)
        self.assertEqual(db.get_reminders(baduser), ())
        db.close()
        print("tested make custom reminder")

    def test_f_make_assignment(self):
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        what = 'Øving 0 in WOF4120'
        deadline = '2020-10-16 19:00:00'
        dt = datetime(2020, 10, 13, 19, 0)  # 13 not 16 because of default-time = 3
        coursemade = True
        user_id = '0000'
        self.assertTrue(len(db.get_reminders(user_id)) == 1)
        self.assertTrue(db.add_reminder(what, deadline, coursemade, user_id) != 0)
        reminders = db.get_reminders(user_id)  # resturns all reminders sorted on deadline
        get_what = reminders[1][0]
        get_datetime = reminders[1][1]
        get_coursemade = reminders[1][2]
        RID = reminders[1][3]
        self.assertEqual(get_what, what)
        self.assertEqual(get_datetime, dt)
        self.assertEqual(get_coursemade, coursemade)
        self.assertTrue(db.delete_reminder(RID) != 0)
        self.assertTrue(len(db.get_reminders(user_id)) == 1)
        self.assertTrue(db.add_reminder(what, deadline, coursemade, user_id) != 0)
        self.assertTrue(db.add_reminder(what, deadline, coursemade, user_id) != 0)
        self.assertTrue(db.add_reminder(what, deadline, coursemade, user_id) != 0)
        self.assertTrue(db.add_reminder(what, deadline, coursemade, user_id) != 0)
        self.assertTrue(db.delete_all_coursemade_reminders(user_id) != 0)
        self.assertTrue(len(db.get_reminders(user_id)) == 1)
        self.assertTrue(db.add_reminder(what, deadline, coursemade, user_id) != 0)
        self.assertTrue(db.delete_all_reminders(user_id) != 0)
        self.assertTrue(len(db.get_reminders(user_id)) == 0)
        self.assertTrue(db.add_reminder(what, deadline, coursemade, user_id) != 0)
        self.assertTrue(len(db.get_reminders(user_id)) == 1)
        db.close()
        print("tested make assignment")

    def test_g_unsubscribe(self):  # 200 OK
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        user_id = '0000'
        course = 'WOF4120'
        baduser = '321'
        badcourse = 'TUL4321'
        self.assertTrue(db.user_subscribed_to_course(user_id, course))
        self.assertTrue(db.unsubscribe(user_id, course) != 0)
        self.assertFalse(db.user_subscribed_to_course(user_id, course))
        self.assertTrue(db.unsubscribe(user_id, course) == 0)
        # test for bad user and bad course
        self.assertFalse(db.user_subscribed_to_course(baduser, course))
        self.assertFalse(db.user_subscribed_to_course(user_id, badcourse))
        self.assertFalse(db.user_subscribed_to_course(baduser, badcourse))
        self.assertTrue(db.unsubscribe(baduser, course) == 0)
        self.assertTrue(db.unsubscribe(user_id, badcourse) == 0)
        self.assertTrue(db.unsubscribe(baduser, badcourse) == 0)
        db.close()
        print("tested usubscribe")

    def test_h_remove_course(self):  # 200 OK
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        course = 'WOF4120'
        self.assertTrue(db.course_exists(course))
        self.assertTrue(db.remove_course(course) != 0)
        self.assertFalse(db.course_exists(course))
        db.close()
        print("tested remove course")

    def test_i_get_all_courses(self):
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        user_id = '0000'
        c1, n1 = 'WOF4120', 'hundelufting'
        c2, n2 = 'PNG2191', 'kanoner'
        badcourse = 'TUL4321'
        self.assertTrue(db.add_course(c1, n1) != 0)
        self.assertTrue(db.add_course(c2, n2) != 0)
        self.assertTrue(db.subscribe(user_id, c1) != 0)
        self.assertTrue(db.subscribe(user_id, c2) != 0)
        ac = db.get_all_courses(user_id)
        self.assertTrue(badcourse not in ac)
        self.assertTrue(ac == [c1, c2] or ac == [c2, c1])
        # test clean course
        self.assertTrue(db.clean_course(user_id) != 0)
        self.assertTrue(len(db.get_all_courses(user_id)) == 0)
        self.assertFalse(db.user_subscribed_to_course(user_id, c1))
        self.assertFalse(db.user_subscribed_to_course(user_id, c2))
        # setup for next test
        self.assertTrue(db.subscribe(user_id, c1) != 0)
        self.assertTrue(db.subscribe(user_id, c2) != 0)
        self.assertTrue(db.user_subscribed_to_course(user_id, c1))
        self.assertTrue(db.user_subscribed_to_course(user_id, c2))
        db.close()
        print("tested get all courses")

    def test_j_foreignkeys(self):
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        c1 = 'WOF4120'
        c2 = 'PNG2191'
        user_id = '0000'
        db.remove_course(c1)
        # check if user-course relation is gone after c1 is removed
        self.assertFalse(db.user_subscribed_to_course(user_id, c1))
        self.assertFalse(db.course_exists(c1))
        # remove user
        self.assertTrue(db.remove_user(user_id) != 0)
        self.assertFalse(db.user_subscribed_to_course(user_id, c2))
        self.assertTrue(db.course_exists(c2))
        self.assertEqual(db.get_reminders(user_id), ())
        db.remove_course(c2)
        db.close()
        print("tested foreign keys")

    def test_k_extra(self):
        db = CDB.CallybotDB("mysql.stud.ntnu.no", "ingritu", "FireFly33", "ingritu_callybot")
        ids = db.get_user_ids()
        allreminders = db.get_all_reminders()
        self.assertTrue(isinstance(ids, type([])))
        self.assertTrue(isinstance(allreminders, type(())))
        self.assertTrue(db.remove_user('1111') != 0)
        self.assertFalse(db.user_exists('1111'))
        self.assertTrue(db.remove_user('2222') != 0)
        self.assertFalse(db.user_exists('2222'))
        self.assertTrue(db.remove_user('3333') != 0)
        self.assertFalse(db.user_exists('3333'))
        db.close()
        print("tested extra")


if __name__ == '__main__':
    unittest.main()
