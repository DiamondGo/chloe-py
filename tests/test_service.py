import unittest

import telebot

from common import getConfig, getAcl
    

class TestBot(unittest.TestCase):
    
    def setUp(self):
        self.config = getConfig()
        self.acl = getAcl()

    def test_config(self):
        # bot = telebot.TeleBot(self.config.telegram.botToken)

        # @bot.message_handler(func=lambda message: True)
        # def echo(message):
        #     bot.reply_to(message, message.text)
        #     #bot.send_voice
        #     bot.get_updates

        # bot.infinity_polling()
    
        # updates = bot.get_updates()
        # for update in updates:
        #     if update.message != None:
        #         print(update.message.text)
        pass


            

if __name__ == '__main__':
    unittest.main()