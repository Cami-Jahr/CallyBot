import unittest
import help_methods as HM


class TestHelpMethods(unittest.TestCase):
    """Tests functions in help_method files"""

    def test_decrypt(self):
        """Tests encrypt and decrypt, and implicitly add_padding and remove_padding"""
        passwords = ["A", "Hei", "Vary", "Looong password, with_some|chars", "I guess this is enough?",
                     "Ill throw in a few extra weird chars",
                     "The next string are all the supported spessial chars for feide:",
                     " !#()*+,.=?@[]_{}~- "]
        for password in passwords:
            encrypted = HM.encrypt(password)
            decrypted = HM.decrypt(encrypted)
            self.assertEqual(password, decrypted)


if __name__ == '__main__':
    unittest.main()
