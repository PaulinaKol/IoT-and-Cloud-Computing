from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        import signals