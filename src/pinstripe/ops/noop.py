from ..graph import Node
from ..result import Result

class Noop(Node['Noop', bool]):
    def execute(self, *dependency_results: Result) -> Result[bool]:
        return Result(ok=True, value=True, reason="noop")