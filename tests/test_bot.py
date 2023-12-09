import unittest

import telebot

from common import getConfig
from im.tgchat import TgBot
    

class TestBot(unittest.TestCase):
    
    def setUp(self):
        self.config = getConfig()

    def test_echo(self):
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

        bot = TgBot(self.config.telegram.botToken)
        for msg in bot.getMessages():
            chat = msg.getChat()
            print(chat.getSelf().getUserName())
            chat.replyMessage("hell, " + msg.getText(), msg.getID())

            

if __name__ == '__main__':
    unittest.main()