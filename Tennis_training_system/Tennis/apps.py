from django.apps import AppConfig


class TennisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Tennis'

    def ready(self):
        import Tennis.signals