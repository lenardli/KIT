from database.common.models import db, History
from database.core import crud
from tg_API.core import Bot
import requests


# db_write = crud.create()
# db_read = crud.retrieve_all()

Bot()
# headers = {'User-Agent': 'api-test-agent'}
# params = {"clusters": "true"}
# resp = requests.get(url='https://api.hh.ru/vacancies', headers=headers, params=params)


# data = [{'station_type': "1", 'station_title': "2"}]
# db_write(db, History, data)
#
#retrieved = db_read(db, History, History.station_type, History.station_title)

# for element in retrieved:
#     print(element.station_ru, element.station_eng)
