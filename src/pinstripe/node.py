from typing import Generic, TypeVar
import threading

from .context import Context
from .result import Result

ResultT = TypeVar('ResultT')
NodeT = TypeVar('NodeT', 'Node')

class Node(Generic[ResultT]):
    def __init__(self, context: Context, label: str = ""):
        self.label = label or self.__name__
        self._context = context
        self._depends_on: list["Node"] = []
        self._result = None
        self._running = False
        self._waiting = False
        self._thread = None
        self._joined = False
        self._state_lock = threading.Lock()
        self._join_lock = threading.Lock()

    def depends_on(self, node: "Node"):
        self._depends_on.append(node)

    @property
    def is_running(self):
        with self._state_lock:
            return self._running

    @property
    def is_waiting(self):
        with self._state_lock:
            return self._waiting

    def execute(self) -> Result[ResultT]:
        """
        The main operation of a Node, to be overridden in subclasses.
        """
        return Result(ok=False, reason="Not implemented")

    def execute_command(self, command) -> Result:
        proc = self._context.execute_sync(command)
        proc.wait()
        result = Result(
            ok=True,
            rc=proc.returncode,
            stdout=proc.stdout.readlines(),
            stderr=proc.stderr.readlines()
        )
        if result.rc != 0:
            result.ok = False
            result.reason = "Execution failed"
            return result
        return result

    def wait(self) -> Result[ResultT]:
        """
        Wait for a node to complete running, then return the Result.
        """
        if not self._thread:
            self.run()
        with self._join_lock:
            if self._thread and not self._joined:
                self._thread.join()
                self._joined = True
        return self._result

    def _main(self):
        """
        Main operation for the Node's thread.
        """
        with self._state_lock:
            self._waiting = True
        for node in self._depends_on:
            result = node.wait()
            if not result.ok:
                self._result = Result(
                    ok=False, rc=result.rc, reason=f"Dependency failed: {str(node)}"
                )
                return
            if result.skipped:
                self._result = Result(
                    ok=True, skipped=True, reason=f"Dependency skipped: {str(node)}"
                )
                return

        with self._state_lock:
            self._waiting = False
            self._running = True
        result = self.execute()
        with self._state_lock:
            self._result = result

    def run(self):
        if self._thread:
            return
        for node in self._depends_on:
            node.run()
        self._thread = threading.Thread(target=self._main)
        self._thread.run()

    def then(self, node: NodeT) -> NodeT:
        node.depends_on(self)
        return node
