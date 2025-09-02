from django.apps import AppConfig


class ReedsdataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reedsdata'


class AppConfig(AppConfig):
    name = 'app'