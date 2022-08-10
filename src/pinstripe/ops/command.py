from typing import Callable, Union

from .. import graph
from ..result import Result
from ..types import CommandT


def default_predicate(result: Result) -> bool:
    return True

class Command(graph.Node["Command", str]):
    """
    A Node which runs a subprocess and returns the Result of its execution.
    """
    def __init__(
        self,
        context,
        command: CommandT,
        *,
        label: str = "",
    ):
        label = label or f"Command: {command}"
        super().__init__(context, label=label)
        self.command = command

    def execute(self, *dependency_results: Result) -> Result[str]:
        return self.execute_command(self.command)
