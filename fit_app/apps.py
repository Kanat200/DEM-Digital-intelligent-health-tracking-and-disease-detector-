from django.apps import AppConfig


class FitAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fit_app'

    def ready(self):
        import fit_app.signals  # noqa
