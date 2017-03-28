import unittest
import help_methods as HM
AES_key = "This_is_the_test_key.very_secret"
print(len(AES_key))


class TestHelpMethods(unittest.TestCase):
    """Tests functions in help_method files"""

    def test_decrypt(self):
        """Tests decrypt and remove_padding"""
        passwords = ["A", "Hei", "Vary", "Looong password, with_some|chars", "I guess this is enough?",
                     "Ill throw in a few extra weird chars", "@£$€{[]}@£$§!'\"#¤%&/()=?", "1234567890\¨'*^`=´~\\"]
        for password in passwords:
            encrypted = HM.encrypt(password)
            decrypted = HM.decrypt(encrypted)
            self.assertEqual(password, decrypted)


if __name__ == '__main__':
    unittest.main()
