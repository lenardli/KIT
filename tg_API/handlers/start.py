from tg_API.loader import bot
from telebot import types


@bot.message_handler(commands=['start', 'help',  'hello-world'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hello!")


@bot.message_handler(func=lambda msg: "Привет" in msg.text)
def send_hello(message):
    bot.send_message(message.chat.id, "Привет, человек!")

