from functools import cached_property
from typing import Union
from pathlib import Path

from .stat import StatInfo
from ..graph import Node, Result

class Entity(Node['Entity', str]):
    def __init__(self, context, *, path: Path, label=None):
        label = label or f"Entity: {path}"
        super().__init__(context=context, label=label)
        self._path = path
        self._state = "exists"
        self._owner = None
        self._mode = None

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
        return self._context.stat(self._path).ignore_failures().wait()