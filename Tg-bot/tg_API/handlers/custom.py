from tg_API.loader import bot, MyStates
from tg_API.keyboards.custom_keyboard import custom_markup, custom_edu, custom_exp
from site_API.core import url, headers, site_api
from tg_API.utils.callback_data_types import modes


@bot.message_handler(commands=["custom"])
def custom_command(message):
    bot.send_message(
        message.chat.id,
        "Выберите критерий, по которому хотите отсортировать вакансии:",
        reply_markup=custom_markup())


@bot.callback_query_handler(
    func=lambda call: call.data in [
        "custom_salary",
        "custom_edu",
        "custom_exp"])
def custom_call(call):
    if call.data == "custom_salary":
        # print(call.message.chat)
        bot.send_message(call.message.chat.id, "Введите уровень зарплаты: ")
        bot.set_state(
            call.from_user.id,
            MyStates.custom_salary,
            call.message.chat.id)
    elif call.data == "custom_edu":
        bot.send_message(
            call.message.chat.id,
            "Выберите, о вакансиях, с каким уровнем образования хотите узнать:",
            reply_markup=custom_edu())
    elif call.data == "custom_exp":
        bot.send_message(
            call.message.chat.id,
            "Выберите, о вакансиях, с каким опытом работы хотите узнать:",
            reply_markup=custom_exp())


@bot.callback_query_handler(func=lambda call: call.data in modes["edu"] or
                            call.data in modes["exp"])
def custom_param(call):
    if isinstance(call, tuple):
        message_id = call[1]
        data = call[0]
    else:
        message_id = call.message.chat.id
        data = call.data

    bot.send_message(message_id, "Ищу информацию. Подождите.")
    get_response = site_api.get_custom_vacancy()
    for i in get_response(url, headers, data):
        bot.send_message(message_id, "".join(i), parse_mode="html")


@bot.message_handler(state=MyStates.custom_salary)
def cust_salary(message):
    # print(message.text)
    custom_param((message.text, message.chat.id))
