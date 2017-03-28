import unittest
import help_methods as HM


class TestHelpMethods(unittest.TestCase):
    """Tests functions in help_method files"""
    def test_decrypt(self):
        """Tests decrypt and remove_padding"""
        passwords = ["A", "Hei", "Vary", "Looong password, with_some|chars", "I guess this is enough?",
                     "Ill throw in a few extra weird chars", "@£$€{[]}@£$§!'\"#¤%&/()=?", "1234567890\¨'*^`=´~\\"]
        for password in passwords:
            encrypted = encrypt(password)
            # TODO: @Halvor. encrypt varying length and format passwords, and decrypt them with decrypt
            decrypted = HM.decrypt(encrypted)
            self.assertEqual(password, decrypted)


if __name__ == '__main__':
    unittest.main()
