from typing import Optional, Union
import subprocess

from .ops.command import Command
from .ops.file import File
from .ops.directory import Directory
from .ops.stat import Stat
from .ops.fact_registry import FactRegistry
from .scoped_edge import ScopedEdge
from . import graph
from .types import CommandT, PredicateT


class Context:
    """
    Context is the main global used to keep track of facts and
    generate
    """

    def __init__(
        self,
        parent: Optional["Context"] = None,
        host="localhost",
        scope: dict = {},
    ) -> None:
        self.nodes: list[graph.Node] = []
        self.parent = parent
        self.children: list["Context"] = []
        self.scope = scope
        if parent:
            parent.children.append(self)
            self._facts = None
        else:
            self._facts = FactRegistry(self)
        self.host = host

    def connect(self, left: graph.Node, right: graph.Node) -> graph.Edge:
        if self.scope:
            return ScopedEdge(self.facts, self.scope, left, right)
        return graph.Edge(left, right)

    @property
    def facts(self) -> FactRegistry:
        if self._facts:
            return self._facts
        return self.root._facts

    @property
    def is_root(self) -> bool:
        return self.parent is None

    @property
    def root(self) -> "Context":
        cursor = self
        while cursor.parent:
            cursor = cursor.parent
        return cursor

    def scoped(self, **facts) -> "Context":
        return Context(self, self.host, scope=facts)

    def file(self, path, label: str = "") -> File:
        node = File(context=self, path=path, label=label)
        self.nodes.append(node)
        return node

    def stat(self, path, label: str = "") -> Stat:
        stat = Stat(context=self, path=path, label=label)
        self.nodes.append(stat)
        return stat

    def run(self, command: CommandT) -> Command:
        """
        Create and return a Command node
        """
        cmd = Command(context=self, command=command)
        return cmd

    def directory(self, path, label=None) -> Directory:
        """
        Create and return a Directory node
        """
        node = Directory(context=self, label=label, path=path)
        return node

    def execute_sync(self, cmd: Union[str, list[str]]) -> subprocess.Popen:
        if type(cmd) == str:
            cmd = ["/bin/sh", "-c", cmd]
        if self.host != "localhost":
            cmd = ["ssh", self.host] + cmd
        return subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8"
        )
