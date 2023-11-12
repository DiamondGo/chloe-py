from definition import MessageBot

class TelegramBot(MessageBot):
    
    def __init__(self, token: str) -> None:
        self.token = token