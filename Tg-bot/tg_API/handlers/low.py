from tg_API.loader import bot
from tg_API.keyboards.low_keyboard import low_markup
from site_API.core import url, params, headers,  site_api


@bot.message_handler(commands=["low"])
def low_command(message):
    bot.send_message(message.chat.id, "Выберите критерий, по которому хотите отсортировать вакансии:",
                     reply_markup=low_markup())


@bot.callback_query_handler(func=lambda call: call.data in ["low_salary", "low_edu", "low_exp"])
def low_call(call):
    print("55555")
    bot.send_message(call.message.chat.id, "Ищу информацию. Подождите.")
    get_response = site_api.get_low_vacancy()
    for i in get_response(url, headers, params, call.data):
        # print(i)
        bot.send_message(call.message.chat.id, ''.join(i), parse_mode="HTML")
