# Cyprety Rental Bot

[![CircleCI](https://circleci.com/gh/unmade/cyprety-rental-bot.svg?style=svg)](https://circleci.com/gh/unmade/cyprety-rental-bot)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8d8a56d77fd9400cb72bf6a8e6d4fc86)](https://app.codacy.com/app/unmade/cyprety-rental-bot?utm_source=github.com&utm_medium=referral&utm_content=unmade/cyprety-rental-bot&utm_campaign=Badge_Grade_Dashboard)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/8d61f7e2374e456db5933a8b18666b44)](https://www.codacy.com/app/unmade/cyprety-rental-bot?utm_source=github.com&utm_medium=referral&utm_content=unmade/cyprety-rental-bot&utm_campaign=Badge_Coverage)
[![Updates](https://pyup.io/repos/github/unmade/cyprety-rental-bot/shield.svg)](https://pyup.io/repos/github/unmade/cyprety-rental-bot/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md)

This is backend for [CYRentBot](https://telegram.me/RentTestBot),
that sends you notifications with new advertisements for rent in Limassol district

## Quickstart

To start backend for your own bot install dependencies and start application:

```bash
pipenv install --deploy
TELEGRAM_BOT_TOKEN=<YOUR_BOT_TOKEN> python -m app
```

## History

Initial version of this bot was developed using
[test && commit || revert (TCR)]((https://medium.com/@kentbeck_7670/test-commit-revert-870bbd756864))
workflow with some inspiration from clean architecture. You can read my afterthoughts [here](docs/afterthoughts.md)

## Development

Download copy of this repo and install requirements.

```bash
pipenv install --dev
```

Make changes and ensure linters and tests are pasing:
```bash
make lint && make test
```

### Adding new parser

To add new parser you must subclass from `Parser` and implements all of its abstract method.
See [bazaraki parser](app/parsers.py) for reference.

## Deployment

To deploy code simply create new tag on the master branch.
