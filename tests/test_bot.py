import unittest

import telebot

from main import getConfig

    

class TestBot(unittest.TestCase):
    
    def setUp(self):
        self.config = getConfig()

    def test_echo(self):
        bot = telebot.TeleBot(self.config.telegram.botToken)

        @bot.message_handler(func=lambda message: True)
        def echo(message):
            bot.reply_to(message, message.text)

        bot.infinity_polling()
            

if __name__ == '__main__':
    unittest.main()