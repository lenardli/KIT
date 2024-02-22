from tg_API.loader import bot
from telebot import types


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, """Привет! Я расскажу о существующих вакансиях по выбранным тобой критериям.\n
Выбери \help, чтобы подробнее узнать о командах.""")


@bot.message_handler(func=lambda msg: "Привет" in msg.text)
def send_hello(message):
    bot.send_message(message.chat.id, "Привет, человек!")
