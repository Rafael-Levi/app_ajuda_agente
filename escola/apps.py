from django.apps import AppConfig

class EscolaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'escola'

    def ready(self):
        try:
          import escola.signals
        except Exception:
            pass