import os
from typing import Optional


class ImproperlyConfigured(Exception):
    pass


class Config:
    _TELEGRAM_BOT_TOKEN = 'TELEGRAM_BOT_TOKEN'
    _DATABASE_PATH = 'DATABASE_PATH'
    _SENTRY_DSN = 'SENTRY_DSN'
    _SENTRY_RELEASE_VERSION = 'SENTRY_RELEASE_VERSION'

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

    @property
    def sentry_dsn(self) -> Optional[str]:
        return os.getenv(self._SENTRY_DSN)

    @property
    def sentry_release_version(self) -> Optional[str]:
        release_version = os.getenv(self._SENTRY_RELEASE_VERSION)
        if release_version:
            return f'cyprety-rental-bot@{release_version}'
        return None
