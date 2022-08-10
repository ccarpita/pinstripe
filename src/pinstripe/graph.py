from typing import Generic, Optional, TypeVar
import threading

from .types import CommandT, PredicateT
from .result import Result

ResultT = TypeVar("ResultT")
NodeT = TypeVar("NodeT")

DEFAULT_PREDICATE: PredicateT = lambda result: result.ok and not result.skipped

class Edge:
    """
    An entity representing the edge between two Node objects.
    """
    def __init__(self, left: 'Node', right: 'Node', predicate: PredicateT = DEFAULT_PREDICATE, predicate_failure_reason: str = ""):
        self.left = left
        self.right = right
        self.predicate = predicate
        self.predicate_failure_reason = predicate_failure_reason

    def start(self):
        """
        Start running the right node of the edge.
        """
        self.right.start()

    def wait(self) -> Result:
        """
        Wait for the right node of the edge to complete and return the Result.
        """
        return self.right.wait()

    def evaluate(self) -> bool:
        return self.predicate(self.wait())

class Node(Generic[NodeT, ResultT]):
    """
    Represents a single Node in the Pinstripe graph which is expected
    to execute some kind of action that produces a Result.
    """

    _counter = 0

    _all: list['Node'] = []

    @classmethod
    def all(cls) -> list['Node']:
        return cls._all

    def __init__(self, context, label: str = ""):

        Node._counter += 1
        """
        Increment a counter for unique hashing/identity
        """

        self._id = Node._counter
        """
        Local unique identifier for the Node.
        """

        Node._all.append(self)

        self.label = label or (self.__class__.__name__ + ":" + str(self._id))
        """
        Short descriptor for the node.
        """

        self._context = context
        """
        Current playbook Context, used to execute commands.
        """

        self._depends_on: list[Edge] = []
        """
        List of dependencies for the node, structured as an Edge between
        this node and the dependency.
        """

        self._result: Optional[Result] = None
        """
        The final Result after execute() is called.
        """

        self._running = False
        """
        True if the Node is currently running.
        """

        self._waiting = False
        """
        True if the Node is currently waiting on dependencies.
        """

        self._thread = None
        """
        Thread execution object for the Node.
        """

        self._joined = False
        """
        True if the thread has been joined.
        """

        self.can_fail = False
        """
        Marker set to True if the Node is allowed to fail.
        """

        self._state_lock = threading.Lock()
        """
        Lock for manipulating state such as _running and _waiting that
        is accessed on both the main thread and the Node execution thread.
        """

        self._join_lock = threading.Lock()
        """
        Lock for joining the thread to get the final Result.
        """

    def __eq__(self, node):
        if self is node:
            return True
        return False

    def __hash__(self) -> int:
        return self._id

    @property
    def is_running(self) -> bool:
        with self._state_lock:
            return self._running

    @property
    def is_waiting(self) -> bool:
        with self._state_lock:
            return self._waiting

    @property
    def is_finished(self) -> bool:
        with self._state_lock:
            return self._result and not self._running

    def labelled(self, label: str) -> NodeT:
        self.label = label
        return self

    def ignore_failures(self) -> NodeT:
        self.can_fail = True
        return self

    def execute(self, *dependency_results: Result) -> Result[ResultT]:
        """
        The main operation of a Node, to be overridden in subclasses.
        """
        return Result(ok=False, reason="Not implemented")

    def execute_command(self, command: CommandT) -> Result:
        proc = self._context.execute_sync(command)
        proc.wait()
        result = Result(
            ok=True,
            rc=proc.returncode,
            stdout=proc.stdout.readlines(),
            stderr=proc.stderr.readlines(),
        )
        if result.rc != 0:
            result.ok = False
            result.reason = "Execution failed"
            return result
        if result.stdout:
            result.value = result.stdout[0].strip()
        else:
            result.value = str(proc.returncode)
        return result

    def wait(self) -> Result[ResultT]:
        """
        Wait for a node to complete running, then return the Result.
        """
        if not self._thread:
            self.start()
        with self._join_lock:
            if self._thread and not self._joined:
                while not self._thread.is_alive():
                    import time
                    time.sleep(1)
                self._thread.join()
                self._joined = True
        return self._result

    def __str__(self) -> str:
        return self.label

    def _main(self):
        """
        Main operation for the Node's thread.
        """
        with self._state_lock:
            self._waiting = True

        results: list[Result] = []
        # Wait for dependencies
        for edge in self._depends_on:
            result = edge.wait()
            results.append(result)
            if not edge.evaluate():
                reason = edge.predicate_failure_reason or "predicate returned False"
                self._result = Result(
                    ok=True,
                    skipped=True,
                    rc=result.rc,
                    reason=f"Skipping for reason: {reason}"
                )
                return

        with self._state_lock:
            self._waiting = False
            self._running = True

        result = self.execute(*results)
        with self._state_lock:
            self._result = result
            self._running = False

    def start(self):
        """
        Start running the thread executing the main operation of the Node,
        which will wait for all of its dependent edges to complete
        """
        with self._state_lock:
            if self._thread:
                return
            for node in self._depends_on:
                node.start()
            self._thread = threading.Thread(target=self._main)
        self._thread.start()

    def depends_on(self, node: NodeT) -> Edge:
        """
        Add a dependency between the current node and the given node.
        """
        edge = self._context.connect(self, node)
        self._depends_on.append(edge)
        return edge

    def then(self, node: NodeT, predicate: PredicateT = DEFAULT_PREDICATE) -> NodeT:
        """
        Creates a reverse dependency with optional Predicate to evaluate
        the final result of the current Node.
        """
        edge = node.depends_on(self)
        edge.predicate = predicate
        return node

    def catch(self, node: NodeT) -> NodeT:
        """
        Creates a reverse dependency with a Predicate requiring that the
        current Node fails in order to execute the given Node.
        """
        self.can_fail = True
        edge = node.depends_on(self)
        edge.predicate = lambda result: not result.ok
        edge.predicate_failure_reason = "No errors caught"
        return node
