from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):#使用了signal
        import users.signals
