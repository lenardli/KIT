from tg_API.loader import bot
from tg_API.keyboards.high_keyboard import high_markup
from site_API.core import url, params, headers, site_api
from tg_API.utils.callback_data_types import ru_en_modes
from database.common.models import db, History
from database.core import crud


@bot.message_handler(commands=["high"])
def high_command(message):
    bot.send_message(
        message.chat.id,
        "Выберите критерий, по которому хотите отсортировать вакансии:",
        reply_markup=high_markup())


@bot.callback_query_handler(
    func=lambda call: call.data in [
        "high_salary",
        "high_edu",
        "high_exp"])
def high_call(call):
    # print(ru_en_modes[call.data])
    crud.create()(db,
                  History,
                  {"profession_type": f"Поиск вакансий {ru_en_modes[call.data]}",
                   "user_id": call.from_user.id})
    bot.send_message(call.message.chat.id, "Ищу информацию. Подождите.")
    get_response = site_api.get_high_vacancy()
    get_response(url, headers, params, call.data)
    for i in get_response(url, headers, params, call.data):
        # print(i)
        bot.send_message(call.message.chat.id, ''.join(i), parse_mode="HTML")
