from tg_API.loader import bot
from database.common.models import db, History
from database.core import crud
from tg_API.utils.callback_data_types import ru_en_modes


@bot.message_handler(commands=["help"])
def help_command(message):
    crud.create()(db, History, {"profession_type": "Ввод команды /help", "user_id": message.from_user.id})
    bot.send_message(message.chat.id, """<b>/low</b> - вакансии: 
• с самой низкой зарплатой
• без опыта работы
• не требующие специального образования

<b>/custom</b> - вакансии:
• с заданной зарплатой
• с заданным опытом работы
• с заданным уровнем образования

<b>/high</b> - вакансии:
• с самой высокой зарплатой
• с требованием к опыту работы от 3 лет
• с требованием к высшему образованию

<b>/history</b> - история запросов пользователей""",
                     parse_mode="HTML")
