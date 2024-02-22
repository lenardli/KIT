import requests


def get_response(url, headers, params, status_code=200):
    resp = requests.get(url=url+"2", headers=headers, params=params)
    if resp.status_code == status_code:
        return resp.json()


def _low_salary_vacancy(url, headers, params, data, func=get_response, cluster_url=None):
    resp = func(url, headers, params)
    print(resp)
    mode = {"low_salary": ["Уровень дохода", 0], "low_edu": ["Образование", 0], "low_exp": ["Опыт работы", 1]}
    if resp is not None:
        for i in resp["clusters"]:
            if i["name"] == mode[data][0]:
                cluster_url = i["items"][mode[data][1]]["url"]
                break
        items = requests.get(url=cluster_url, headers=headers).json()["items"]
        # print(items)
        if data == "low_salary":
            items.sort(key=lambda x: x["salary"]["to"] if x["salary"]["to"] is not None else 0)
            items = list(filter(lambda item: item["salary"]["to"] is not None, items))
        for i in items[:3]:
            yield "<b>Обязанности:</b>", i["snippet"]["responsibility"], "\n", i["alternate_url"]

    else:
        yield "Упс, что-то пошло не так. Попробуйте ещё раз."



class SiteApiInterface:

    @staticmethod
    def get_low_vacancy():
        return _low_salary_vacancy

    @staticmethod
    def get_low_edu():
        return _low_edu

if __name__ == '__main__':
    SiteApiInterface()
