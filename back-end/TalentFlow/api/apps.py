from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'TalentFlow.api'
    def ready(self):
        # import signals so they are registered
        import TalentFlow.api.signals  # noqa