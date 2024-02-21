from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from site_API.core import url, params, headers, site_api
from tg_API.loader import bot

def low_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Низкооплачиваемые вакансии", callback_data="low_salary"),
               InlineKeyboardButton("Вакансии без требований к образованию", callback_data="cb_no"),
               InlineKeyboardButton("Вакансии без требований к опыту работы", callback_data="vvv"))
    return markup


@bot.callback_query_handler(func=lambda call: call.data == "low_salary")
def low_salary_call(call):
    bot.send_message(call.message.chat.id, "Ищу информацию. Подождите.")
    get_response = site_api.get_low_vacancy()
    for i in get_response(url, headers, params):
        bot.send_message(call.message.chat.id, f"<b>Обязанности:</b> {' '.join(i)}", parse_mode="HTML")
