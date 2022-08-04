from typing import Optional, Union
import subprocess

from .node import Node
from .ops.file import File
from .ops.stat import Stat
from .ops.fact_registry import FactRegistry

from pinstripe.ops.facts.os import OsProvider
from pinstripe.ops.stat import Stat

DEFAULT_FACT_PROVIDERS = [OsProvider()]


class Context:
    """
    Context is the main global used to keep track of facts and
    generate
    """

    def __init__(
        self,
        parent: Optional["Context"] = None,
        host="localhost",
        match_facts: dict = {},
    ) -> None:
        self.nodes: list[Node] = []
        self.parent = parent
        self.children: list["Context"] = []
        self.match_facts = match_facts
        if parent:
            parent.children.append(self)
            self._facts = None
        else:
            self._facts = FactRegistry()
            for provider in DEFAULT_FACT_PROVIDERS:
                provider.register(self._facts)
        self.host = host

    def check_facts(self) -> bool:
        pass

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
        return Context(self, self.host, match_facts=facts)

    def file(self, path, label: str = "") -> File:
        node = File(path=path, label=label)
        self.nodes.append(node)
        return node

    def stat(self, path, label: str = "") -> Stat:
        stat = Stat(path=path, label=label)
        self.nodes.append(stat)
        return stat

    def run(self, command) -> Command:
        cmd = Command(context=self, command=command)
        self.nodes.append(cmd)
        return cmd

    def directory(self, path, name=None) -> Directory:
        node = Directory(name=name, path=path)
        self.nodes.append(node)
        return node

    def execute_sync(self, cmd: Union[str, list[str]]) -> subprocess.Popen:
        if type(cmd) == str:
            cmd = ["/bin/sh", "-c", cmd]
        if self.host != "localhost":
            cmd = ["ssh", self.host] + cmd
        return subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8"
        )
