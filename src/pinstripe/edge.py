from .node import Node
from .result import Result

class Edge:
    """
    An entity representing the edge between two Node objects.
    """
    def __init__(self, left: Node, right: Node, *, ignore_failures=False) -> None:
        self.ignore_failures = ignore_failures
        self.left = left
        self.right = right

    def run(self):
        """
        Execute the edge
        """
        self.right.run()

    def wait(self) -> Result:
        return self.right.wait()

    def evaluate() -> bool:
        result = self.right.wait()
        return True