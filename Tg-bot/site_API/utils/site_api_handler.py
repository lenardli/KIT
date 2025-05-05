import requests
from typing import Dict, List
from tg_API.utils.callback_data_types import modes


def _get_response(url: str, headers: Dict, params: Dict, status_code=200):
    resp = requests.get(url=url, headers=headers, params=params)
    if resp.status_code == status_code:
        return resp.json()


def _custom_vacancies(
        url: str,
        headers: Dict,
        data: str):
    if data in modes["edu"]:
        params = {"clusters": "true"}
        # print(params)
    elif data in modes["exp"]:
        params = {"experience": data}
    else:
        params = {"salary": data}
    resp = requests.get(url=url, headers=headers, params=params).json()
    if data in modes["edu"]:
        if data == "no_edu":
            items = resp['clusters'][8]['items'][0]['url']
        elif data == "special_secondary":
            items = resp['clusters'][8]['items'][2]['url']
        else:
            items = resp['clusters'][8]['items'][1]['url']
        resp = requests.get(url=items, headers=headers).json()
    items = list(
        filter(
            lambda item: item["snippet"]["responsibility"] is not None and
            item["alternate_url"] is not None,
            resp['items']))
    for i in items[:3]:
        yield ("<b>Обязанности: </b>", i["snippet"]["responsibility"][0].lower() + i["snippet"]["responsibility"][1:], "\n\n", "<b>Cсылка на вакансию:</b> " + i["alternate_url"])
    # else:
    #     yield "Упс, что-то пошло не так. Попробуйте ещё раз."


def _low_vacancies(
        url: str,
        headers: Dict,
        params: Dict,
        data: str,
        func=_get_response,
        cluster_url=None):
    resp = func(url, headers, params)
    mode = {
        "low_salary": [
            "Уровень дохода", 0], "low_edu": [
            "Образование", 0], "low_exp": [
                "Опыт работы", 0]}
    # for i in resp["clusters"]:
    #     print(i)
    if resp is not None:
        for i in resp["clusters"]:
            if i["name"] == mode[data][0]:
                cluster_url = i["items"][mode[data][1]]["url"]
                print( i["items"])
                break

        items = requests.get(url=cluster_url, headers=headers).json()["items"]
        # print(items)
        if data == "low_salary":
            items.sort(key=lambda x: x["salary"]["to"]
                       if x["salary"]["to"] is not None else -1)
            items = list(filter(lambda item: item["salary"]["to"] is not None and item["snippet"][
                         "responsibility"] is not None and item["alternate_url"] is not None, items))
        for i in items[:3]:
            yield "<b>Обязанности: </b>", i["snippet"]["responsibility"][0].lower() + i["snippet"]["responsibility"][1:], "\n\n", "Cсылка на вакансию: " + i["alternate_url"]
    else:
        yield "Упс, что-то пошло не так. Попробуйте ещё раз."


def _high_vacancies(
        url: str,
        headers: Dict,
        params: Dict,
        data: str,
        func=_get_response,
        cluster_url=None):
    resp = func(url, headers, params)
    mode = {
        "high_salary": [
           1, 5], "high_edu": [
            8, 1], "high_exp": [
            3, 3]}
    if resp is not None:
        cluster_url = resp["clusters"][mode[data][0]]["items"][mode[data][1]]["url"]
        items = requests.get(url=cluster_url, headers=headers).json()["items"]
        items = list(item for item in items if item["snippet"][
            "responsibility"] is not None and item["alternate_url"] is not None)
        for i in items[:3]:
            yield "<b>Обязанности: </b>", i["snippet"]["responsibility"][0].lower() + i["snippet"]["responsibility"][1:], "\n\n", "Cсылка на вакансию: " + i["alternate_url"]
    else:
        yield "Упс, что-то пошло не так. Попробуйте ещё раз."


class SiteApiInterface:

    @staticmethod
    def get_low_vacancy():
        return _low_vacancies

    @staticmethod
    def get_custom_vacancy():
        return _custom_vacancies

    @staticmethod
    def get_high_vacancy():
        return _high_vacancies


if __name__ == '__main__':
    SiteApiInterface()
