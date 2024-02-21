from tg_API.loader import bot


@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(message.chat.id, """\low - вакансии:
    
* с самой низкой з\п,
* без опыта работы,
* не требующие специального образования""")
