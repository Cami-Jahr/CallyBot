import unittest
import iblack_scrape as BB
import ilearn_scrape as IL
from credentials import Credentials
from help_methods import decrypt
feide = Credentials().feide

class TestScraping(unittest.TestCase):

    def test_IL(self):
        reply = IL.scrape(feide[0], decrypt(feide[1]))
        self.assertEqual(reply.__class__, list)
        reply = IL.scrape("Invalid", "Invalid")
        self.assertEqual(reply, "error")
        print(reply)

    def test_BB(self):
        reply = BB.scrape(feide[0], decrypt(feide[1]))
        self.assertEqual(reply.__class__, list)
        reply = BB.scrape("Invalid", "Invalid")
        print(reply)
        self.assertEqual(reply, "error")


if __name__ == '__main__':
    unittest.main()
