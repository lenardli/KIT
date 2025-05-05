import telebot
from telebot import custom_filters
from telebot.storage import StateMemoryStorage
from tg_API.config_data.config import token
from telebot.handler_backends import State, StatesGroup


state_storage = StateMemoryStorage()
bot = telebot.TeleBot(token, state_storage=state_storage)
bot.add_custom_filter(custom_filters.StateFilter(bot))


class MyStates(StatesGroup):
    custom_salary = State()






