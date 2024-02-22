from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from site_API.core import url, params, headers, site_api
from tg_API.loader import bot

def low_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Низкооплачиваемые вакансии", callback_data="low_salary"),
               InlineKeyboardButton("Вакансии без требований к образованию", callback_data="low_edu"),
               InlineKeyboardButton("Вакансии без требований к опыту работы", callback_data="low_exp"))
    return markup


@bot.callback_query_handler(func=lambda call: call.data in ["low_salary", "low_edu", "low_exp"])
def low_salary_call(call):
    bot.send_message(call.message.chat.id, "Ищу информацию. Подождите.")
    get_response = site_api.get_low_vacancy()
    for i in get_response(url, headers, params, call.data):
        # print(i)
        bot.send_message(call.message.chat.id, ''.join(i), parse_mode="HTML")


