import os

import pytest

from app import config


def test_config_raises_improperly_configured(amocker):
    with amocker.patch.dict(os.environ):
        os.environ.pop('TELEGRAM_BOT_TOKEN', None)  # in case it is set in ENV
        with pytest.raises(config.ImproperlyConfigured):
            config.Config()


def test_bot_token(amocker, fake_bot_token):
    with amocker.patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': fake_bot_token}):
        conf = config.Config()
        assert conf.bot_token == fake_bot_token


def test_database_default_value(amocker, fake_bot_token):
    with amocker.patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': fake_bot_token}):
        conf = config.Config()
        assert conf.database == 'sqlite.db'


def test_database_env_value(amocker, fake_bot_token):
    envs = {'TELEGRAM_BOT_TOKEN': fake_bot_token, 'DATABASE_PATH': 'db.db'}
    with amocker.patch.dict(os.environ, envs):
        conf = config.Config()
        assert conf.database == 'db.db'


def test_database_sentry_dsn_is_none(amocker, fake_bot_token):
    envs = {'TELEGRAM_BOT_TOKEN': fake_bot_token}
    with amocker.patch.dict(os.environ, envs):
        os.environ.pop('SENTRY_DSN', None)  # in case it is set in ENV
        conf = config.Config()
        assert conf.sentry_dsn is None


def test_database_sentry_dsn(amocker, fake_bot_token):
    sentry_dsn = 'https://969f72@sentry.io/913'
    envs = {'TELEGRAM_BOT_TOKEN': fake_bot_token, 'SENTRY_DSN': sentry_dsn}
    with amocker.patch.dict(os.environ, envs):
        conf = config.Config()
        assert conf.sentry_dsn == sentry_dsn


def test_database_sentry_release_version_is_none(amocker, fake_bot_token):
    envs = {'TELEGRAM_BOT_TOKEN': fake_bot_token}
    with amocker.patch.dict(os.environ, envs):
        os.environ.pop('SENTRY_RELEASE_VERSION', None)  # in case it is set in ENV
        conf = config.Config()
        assert conf.sentry_release_version is None


def test_database_sentry_release_version(amocker, fake_bot_token):
    envs = {'TELEGRAM_BOT_TOKEN': fake_bot_token, 'SENTRY_RELEASE_VERSION': '2.2.0'}
    with amocker.patch.dict(os.environ, envs):
        conf = config.Config()
        assert conf.sentry_release_version == 'cyprety-rental-bot@2.2.0'
