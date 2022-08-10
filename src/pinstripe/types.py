from typing import Callable, Union

from .result import Result

CommandT = Union[str, list[str]]
PredicateT = Callable[[Result], bool]