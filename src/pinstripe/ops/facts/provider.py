from ..fact_registry import FactRegistry
from ..node import Node
from ...result import Result

class Provider(Node):
    NAME = ""
    """
    Name of the provider variable to register.
    """

    COMMAND = []
    """
    Command arguments to execute. The value of the returned result will be set
    to the first line of output lowercased with whitespace stripped.
    """

    def register(self, facts: FactRegistry):
        facts.register_provider(self.NAME, self)

    def execute(self) -> Result[str]:
        result = self.execute_command(self.COMMAND)
        if result.ok:
            result.value = result.stdout[0].lower().strip()
        return result
