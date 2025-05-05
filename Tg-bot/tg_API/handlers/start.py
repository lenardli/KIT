from tg_API.loader import bot
from telebot import types
from database.common.models import db, History
from database.core import crud
from tg_API.utils.callback_data_types import ru_en_modes

@bot.message_handler(commands=['start'])
def send_welcome(message):
    crud.create()(db, History, {"profession_type": f"Ввод команды /start", "user_id": message.from_user.id})
    bot.send_message(message.chat.id, """Привет! Я расскажу о существующих вакансиях по выбранным тобой критериям.\n
Выбери /help, чтобы подробнее узнать о командах.""")


@bot.message_handler(func=lambda msg: "Привет" in msg.text)
def send_hello(message):
    bot.send_message(message.chat.id, "Привет, человек!")
