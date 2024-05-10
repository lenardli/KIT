from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from tg_API.loader import bot

def custom_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Вакансии, отсортированные по заплате", callback_data="custom_salary"),
               InlineKeyboardButton("Вакансии, отсортированные по требованию к образованию", callback_data="custom_edu"),
               InlineKeyboardButton("Вакансии, отсортированные по требованию к опыту работы", callback_data="custom_exp"))
    return markup


def custom_edu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Вакансии, требующие высшего образования",
                                    callback_data="higher"),
               InlineKeyboardButton("Вакансии, требующие среднего специального образования",
                                    callback_data="especial_secondary"),
               InlineKeyboardButton("Вакансии, в которых образование не указано или не требуется",
                                    callback_data="no_edu")
               )
    return markup


def custom_exp():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Вакансии, требующие опыта работы от 1 до 3 лет",
                                    callback_data="between1And3"),
               InlineKeyboardButton("Вакансии, не требующие опыта работы",
                                    callback_data="noExperience"),
               InlineKeyboardButton("Вакансии, требующие опыта работы от 3 до 6 лет",
                                    callback_data="between3And6")
               )
    return markup
