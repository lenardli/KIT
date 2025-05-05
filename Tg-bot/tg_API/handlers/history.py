from tg_API.loader import bot
from database.common.models import db, History
from database.core import crud


@bot.message_handler(commands=["history"])
def low_command(message):
    # print(message.from_user.id)
    crud.create()(db, History, {"profession_type": "Ввод команды /history",
                                "user_id": message.from_user.id})
    db_read = crud.retrieve_single()
    retrieved = db_read(
        db,
        History,
        message.from_user.id)
    retrieved = [
        element.created_at.strftime("%d.%m.%Y %H:%M") +
        " " +
        element.profession_type for element in retrieved]
    str_retrieved = "\n".join(retrieved)
    bot.send_message(message.chat.id, f"История запросов:\n\n{str_retrieved}")
