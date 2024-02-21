from tg_API.loader import bot
from tg_API.keyboards.low_keyboard import low_markup
from site_API.core import url, params, headers

@bot.message_handler(commands=["low"])
def low_command(message):
    bot.send_message(message.chat.id, "Выберите критерий, по котором хотите отсортировать вакансии:",
                     reply_markup=low_markup())



