import requests


def get_response(url, headers, params, status_code=200):
    resp = requests.get(url=url, headers=headers, params=params)
    if resp.status_code == 200:
        return resp.json()


def _low_salary_vacancy(url, headers, params, func=get_response, cluster_url=None):
    resp = func(url, headers, params)
    if type(resp is not None):
        for i in resp["clusters"]:
            if i["name"] == "Уровень дохода":
                cluster_url = i["items"][0]["url"]
        items = requests.get(url=cluster_url, headers=headers).json()["items"]
        items.sort(key=lambda x: x["salary"]["to"] if x["salary"]["to"] is not None else 0)
        items = list(filter(lambda item: item["salary"]["to"] is not None, items))
        for i in items[:3]:
            yield i["snippet"]["responsibility"], "\n\n<b>Ссылка на вакансию:</b>", i["alternate_url"]
        else:
            return "Упс, что-то пошло не так. Попробуйте ещё раз."

class SiteApiInterface:

    @staticmethod
    def get_low_vacancy():
        return _low_salary_vacancy


if __name__ == '__main__':
    SiteApiInterface()
