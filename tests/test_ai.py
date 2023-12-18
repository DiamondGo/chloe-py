import unittest


from definition import ChatID
from common import getConfig
#from im.tgchat import TgBot
from ai.talkfact import AITalkFactory
    
import google.ai.generativelanguage as glm
import google.generativeai as genai

class TestBot(unittest.TestCase):
    
    def setUp(self):
        self.config = getConfig()

    def test_ai(self):
        self.skipTest("skip")
        factory = AITalkFactory(self.config)

        oai = factory.getTalk(ChatID("0"))

        a = oai.ask("tell me a love store about 2000 words.")
        print(a)

        print("---------------------")

        a = oai.ask("another please")
        print(a)

        print("---------------------")

        a = oai.ask("another please")
        print(a)

    def test_gemini(self):
        config = self.config.gemini
        
        genai.configure(api_key=config.apiKey)
        model = genai.GenerativeModel('gemini-pro')
        
        response = model.generate_content("What is the meaning of life?")

        print(response)



if __name__ == '__main__':
    unittest.main()