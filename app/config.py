import os


class ImproperlyConfigured(Exception):
    pass


class Config:
    _TELEGRAM_BOT_TOKEN = 'TELEGRAM_BOT_TOKEN'
    _DATABASE_PATH = 'DATABASE_PATH'

    REQUIRED_ENVS = [_TELEGRAM_BOT_TOKEN]

    def __init__(self):
        for env in self.REQUIRED_ENVS:
            try:
                os.environ[env]
            except KeyError:
                raise ImproperlyConfigured(f'Variable is not set: `{env}`')

    @property
    def bot_token(self) -> str:
        return os.environ[self._TELEGRAM_BOT_TOKEN]

    @property
    def database(self) -> str:
        return os.getenv(self._DATABASE_PATH, 'sqlite.db')
