from tg_API.config_data.settings import SiteSettings
from site_API.utils.site_api_handler import SiteApiInterface

site = SiteSettings()
params = {}

url = "https://" + site.host_api

site_api = SiteApiInterface()

if __name__ == '__main__':
    site_api()


