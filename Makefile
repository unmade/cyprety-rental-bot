PYTHONPATH := $(CURDIR)
MYPYPATH := $(PYTHONPATH)


nopyc:
	@find . -name "*.pyc" -exec rm -f {} \;


isort:
	@pipenv run isort --check-only -q


flake8:
	@pipenv run flake8 app/* tests/*


pylint:
	@pipenv run pylint app/* tests/*


mypy:
	@MYPYPATH=$(MYPYPATH) pipenv run mypy app


lint: isort flake8 pylint mypy


test:
	@PYTHONPATH=$(PYTHONPATH) pipenv run pytest


commit:
	@git commit -am working


revert:
	@git reset --hard


tcr:
	@make lint && (make test && make commit || make revert)
