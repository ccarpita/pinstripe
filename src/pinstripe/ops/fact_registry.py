from node import Node
from typing import Mapping

from ..result import Result

class FactRegistry(Node):
    def __post_init__(self):
        self._fact_providers: Mapping[str, Node] = {}
        self._result_cache: Mapping[str, Result] = {}
        self._needs_facts: set[str] = set()

    def register_provider(self, name: str, provider: Node):
        self._fact_providers[name] = provider

    def has_provider(self, name: str):
        return name in self._fact_providers

    def needs_fact(self, name: str):
        self._needs_facts.add(name)

    def execute(self) -> Result[dict[str,str]]:
        for name in self._needs_facts:
            if not self.has_provider(name):
                return Result(ok=False, rc=1, reason=f"No provider found for {name}")
        for name in self._needs_facts:
            self._fact_providers[name].run()
        facts: dict[str, str] = {}
        for name in self._needs_facts:
            value = self.get(name)
            facts[name] = value

        return Result(ok=True, value=facts)

    def get(self, name: str) -> str:
        if not self.has_provider(name):
            return ""
        if name not in self._result_cache:
            self._result_cache[name] = self._fact_providers[name].wait()
        value = self._result_cache[name].value
        if value is None:
            return ""
        return str(value)
