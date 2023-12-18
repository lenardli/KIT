import telebot

token= "6851372913:AAG0D8oouK_wstkjKRudUX3scgrzPzhqpmk"
bot = telebot.TeleBot(token)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    print(message)
    bot.reply_to(message, "Hello world!")
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

if __name__ == '__main__':
    bot.infinity_polling()
