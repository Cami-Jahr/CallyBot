import unittest
import iblack_scrape as BB
import ilearn_scrape as IL
from credentials import Credentials
from help_methods import decrypt

login_info = Credentials().feide


class TestScraping(unittest.TestCase):
    def test_IL(self):
        successful = IL.scrape(login_info[0], decrypt(login_info[1]))
        self.assertEqual(successful.__class__, list)
        unsuccessful = IL.scrape("Invalid", "Invalid")
        self.assertEqual(unsuccessful, "error")

    def test_BB(self):
        successful = BB.scrape(login_info[0], decrypt(login_info[1]))
        self.assertEqual(successful.__class__, list)
        unsuccessful = BB.scrape("Invalid", "Invalid")
        self.assertEqual(unsuccessful, "error")


if __name__ == '__main__':
    unittest.main()
