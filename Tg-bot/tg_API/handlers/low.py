from tg_API.loader import bot
from tg_API.keyboards.low_keyboard import low_markup
from site_API.core import url, params, headers, site_api
from database.common.models import db, History
from database.core import crud
from tg_API.utils.callback_data_types import ru_en_modes


@bot.message_handler(commands=["low"])
def low_command(message):
    bot.send_message(
        message.chat.id,
        "Выберите критерий, по которому хотите отсортировать вакансии:",
        reply_markup=low_markup())


@bot.callback_query_handler(
    func=lambda call: call.data in [
        "low_salary", "low_edu", "low_exp"])
def low_call(call):
    # print(call)
    crud.create()(db,
                  History,
                  {"profession_type": f"Поиск вакансий {ru_en_modes[call.data]}",
                   "user_id": call.from_user.id})
    bot.send_message(call.message.chat.id, "Ищу информацию. Подождите.")
    get_response = site_api.get_low_vacancy()
    for i in get_response(url, headers, params, call.data):
        # print(i)
        bot.send_message(call.message.chat.id, ''.join(i), parse_mode="HTML")


# print("Hi")
