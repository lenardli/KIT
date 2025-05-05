from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def high_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Высокооплачиваемые вакансии", callback_data="high_salary"),
               InlineKeyboardButton("Вакансии с высокими требованиями к образованию", callback_data="high_edu"),
               InlineKeyboardButton("Вакансии с высокими требованиями к опыту работы", callback_data="high_exp"))
    return markup
