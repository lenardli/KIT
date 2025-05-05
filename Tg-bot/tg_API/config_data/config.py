from tg_API.config_data.settings import SiteSettings


site = SiteSettings()
token = site.TG_key.get_secret_value()



