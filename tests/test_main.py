import importlib
import runpy


def test_executes__main__(amocker):
    with amocker.patch('app.executor.run') as run_mock:
        runpy.run_module('app', run_name='__main__')
    assert run_mock.called


def test_imports__main__(amocker):
    with amocker.patch('app.executor.run') as run_mock:
        importlib.import_module('app.__main__')
    assert not run_mock.called
