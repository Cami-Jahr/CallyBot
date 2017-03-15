from datetime import datetime, timedelta


class Reminders:

    def __init__(self, db):
        self.db = db

    def search_reminders(self):
        """Returns all reminders for the next hours, in format [datetime.datetime, user_id, message, course_made]"""
        listing = self.db.get_all_reminders()
        print(listing)
        minago = datetime.now() - timedelta(minutes=30)
        mintil = datetime.now() + timedelta(minutes=30)
        current = []
        app = current.append
        for line in listing:
            if minago < line[0] < mintil:
                app(line)
        print(current)
        return current
