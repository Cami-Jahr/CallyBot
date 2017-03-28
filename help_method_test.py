import unittest
import help_methods as HM
from Crypto.Cipher import AES  # pip pycrypto
import base64
AES_key = "This_is_the_test_key. Not_very_secret"


def encrypt(word):
    iv = 16 * '\x00' #init vector
    obj = AES.new(AES_key, AES.MODE_CBC, iv)
    data = obj.encrypt(base64.b64decode(word))
    print(data)
    return data

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
