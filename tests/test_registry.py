from app import parsers, registry


def test_parser_registry():
    parser_registry = registry.ParserRegistry()
    assert parser_registry.parser_classes == {}


def test_parser_registry_add():
    url = 'https://real.estates.com'
    parser_registry = registry.ParserRegistry()
    parser_registry.add(url)(parsers.BazarakiParser)
    assert parser_registry.parser_classes == {url: parsers.BazarakiParser}


def test_add_parser(amocker):
    url = 'https://real.estates.com'
    with amocker.patch('app.registry._parser_registry.add') as add_mock:
        registry.add_parser(url)

    assert add_mock.called


def test_list_parsers(amocker):
    expected_parser = {}
    with amocker.patch('app.registry._parser_registry') as parser_registry_mock:
        parser_registry_mock.parser_classes = expected_parser
        assert registry.list_parsers() == expected_parser
