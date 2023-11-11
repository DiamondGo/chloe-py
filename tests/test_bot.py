import unittest

class TestBot(unittest.TestCase):

    def test_helloworld(self):
        self.assertEqual('bot'.upper(), "BOT")

if __name__ == '__main__':
    unittest.main()