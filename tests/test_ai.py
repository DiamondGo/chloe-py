import unittest


from definition import ChatID
from common import getConfig
#from im.tgchat import TgBot
from ai.openaitalk import TalkFactory
    

class TestBot(unittest.TestCase):
    
    def setUp(self):
        self.config = getConfig()

    def test_ai(self):
        factory = TalkFactory(self.config)

        oai = factory.getTalk(ChatID("0"))

        a = oai.ask("tell me a love store about 2000 words.")
        print(a)

        print("---------------------")

        a = oai.ask("another please")
        print(a)

        print("---------------------")

        a = oai.ask("another please")
        print(a)

if __name__ == '__main__':
    unittest.main()