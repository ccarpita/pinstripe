from functools import cached_property
from typing import Union

from pinstripe.ops.stat import StatInfo

from ..node import Node, Result

class Entity(Node):
    def __init__(self, context, *, path, label=None):
        name = name or f"Entity: {path}"
        super().__init__(context=context, label=label)
        self._path = path
        self._state = "exists"

    def exists(self) -> 'Entity':
        self._state = "exists"
        return self

    def owner(self, owner: str) -> 'Entity':
        self._owner = owner
        return self

    def mode(self, mode: Union[int, str]) -> 'Entity':
        if type(mode) == int:
            mode = oct(mode).replace('o', '')
        self._mode = mode

    def absent(self) -> 'Entity':
        self._state = "absent"
        return self

    def contents_if_empty(self, contents) -> 'Entity':
        self._contents_if_empty = contents
        return self

    @cached_property
    def stat(self) -> Result[StatInfo]:
        return self._context.stat(self._path).wait()