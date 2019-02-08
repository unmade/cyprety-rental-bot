import os

import pytest

from app import config


def test_config_raises_improperly_configured(amocker):
    with amocker.patch.dict(os.environ):
        del os.environ['TELEGRAM_BOT_TOKEN']
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
