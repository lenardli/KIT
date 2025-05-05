from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def low_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Низкооплачиваемые вакансии", callback_data="low_salary"),
               InlineKeyboardButton("Вакансии без требований к образованию", callback_data="low_edu"),
               InlineKeyboardButton("Вакансии без требований к опыту работы", callback_data="low_exp"))
    return markup





