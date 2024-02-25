from database.common.models import db, History
from database.core import crud
from tg_API.core import Bot
import requests

# db_write = crud.create()
# db_read = crud.retrieve_all()
Bot()


# params = {"clusters": "true"}
# headers = {'User-Agent': "api-test-agent"}
# url = "https://api.hh.ru/vacancies"
#
# resp = requests.get(url, headers=he:aders, params=params).json()
# for i in resp["clusters"]:
#     print(i)
    # if i["name"] == "Образование":
        # cluster_url = i["items"][0]["url"]
        # print(requests.get(i['items'][0]["url"], headers=headers).json()['clusters'])
        # break
#
# data = [{'station_type': "1", 'station_title': "2"}]
# db_write(db, History, data)
#
#retrieved = db_read(db, History, History.station_type, History.station_title)

# for element in retrieved:
#     print(element.station_ru, element.station_eng)
