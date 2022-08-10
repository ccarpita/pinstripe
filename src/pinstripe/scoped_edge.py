from .graph import Edge, Node
from .result import Result
from .ops.fact_registry import FactRegistry


class ScopedEdge(Edge):
    def __init__(
        self,
        facts: FactRegistry,
        match: dict[str, str],
        left: Node,
        right: Node,
    ) -> None:
        self.facts = facts
        self.match = match
        for key in self.match.keys():
            self.facts.needs_fact(key)
        super().__init__(left, right)

    def start(self):
        self.facts.start()

    def wait(self) -> Result:
        for k in self.match.keys():
            expected = self.match[k]
            actual = self.facts.get(k)
            if expected != actual:
                return Result(
                    ok=True,
                    skipped=True,
                    reason=f"Fact does not match scope ({actual} (actual) != {expected} (expected))",
                )
        return super().wait()
