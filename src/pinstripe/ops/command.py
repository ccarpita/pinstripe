from typing import Union

from ..context import Context
from ..node import Node
from ..result import Result

class Command(Node):
    def __init__(self, context: Context, command: Union[str, list[str]]):
        super().__init__(context)
        self.command = command

    def execute(self) -> Result:
        return self.execute_command(self.command)
