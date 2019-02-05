class ParserRegistry:

    def __init__(self):
        self.parser_classes = {}

    def add(self, url):
        def wrapper(parser_class):
            self.parser_classes[url] = parser_class
            return parser_class
        return wrapper


_parser_registry = ParserRegistry()  # pylint: disable=invalid-name


def add_parser(url: str):
    return _parser_registry.add(url)


def list_parsers():
    return _parser_registry.parser_classes
