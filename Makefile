PYTHONPATH := $(CURDIR)
MYPYPATH := $(PYTHONPATH)


nopyc:
	@find . -name "*.pyc" -exec rm -f {} \;


isort:
	@isort --check-only -q


flake8:
	@flake8 app/* tests/*


pylint:
	@pylint app/* tests/*


mypy:
	@MYPYPATH=$(MYPYPATH) mypy app


lint: isort flake8 pylint mypy


test:
	@PYTHONPATH=$(PYTHONPATH) pytest


commit:
	@git commit -am working


revert:
	@git reset --hard


tcr:
	@make lint && (make test && make commit || make revert)
