from tg_API.config_data.settings import SiteSettings
from site_API.utils.site_api_handler import SiteApiInterface

site = SiteSettings()
params = {"clusters": "true"}
headers = {'User-Agent': "api-test-agent"}

url = "https://api.hh.ru/vacancies"

site_api = SiteApiInterface()

if __name__ == '__main__':
    site_api()
