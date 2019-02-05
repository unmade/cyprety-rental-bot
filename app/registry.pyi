from typing import Awaitable, Callable, Dict, Type

from . import parsers

ParserClass = Type[parsers.Parser]
Task = Callable[..., Awaitable[None]]


class ParserRegistry:

    parser_classes: Dict[str, ParserClass]

    def __init__(self): ...

    def add(self, url: str) -> Callable[[ParserClass], ParserClass]: ...


parser_registry: ParserRegistry


def add_parser(url: str) -> Callable[[ParserClass], ParserClass]: ...


def list_parsers() -> Dict[str, ParserClass]: ...
