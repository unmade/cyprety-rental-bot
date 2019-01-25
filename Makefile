nopyc:
	@find . -name "*.pyc" -exec rm -f {} \;


isort:
	@isort --check-only -q


flake8:
	@flake8 app/* tests/*


pylint:
	@pylint app/* tests/*


lint: isort flake8 pylint


test:
	@pytest


commit:
	@git commit -am working


tc: lint && test && commit
