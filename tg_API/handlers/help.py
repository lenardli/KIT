from tg_API.loader import bot


@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(message.chat.id, """<b>\low</b> - вакансии: 
• с самой низкой зарплатой
• без опыта работы
• не требующие специального образования""", parse_mode="HTML")
