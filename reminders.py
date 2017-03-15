from datetime import datetime, timedelta


class Reminders:

    def __init__(self, db):
        self.db = db

    def search_reminders(self):
        listing = self.db.get_all_reminders()
        print(listing)
        minago = datetime.now() - timedelta(minutes=1)
        mintil = datetime.now() + timedelta(minutes=1)
        current = []
        app = current.append
        for line in listing:
            if minago < line[0] < mintil:
                app(line)
        print(current)
