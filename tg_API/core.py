from tg_API.loader import bot
from tg_API.handlers import start, low, help


class Bot:
    @staticmethod
    def __init__():
        bot.infinity_polling(skip_pending=True)


if __name__ == '__main__':
    bot.infinity_polling(skip_pending=True)

