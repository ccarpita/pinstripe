from typing import Optional, TypeVar, Generic
T = TypeVar("T")

class Result(Generic[T]):
    def __init__(
        self,
        ok: bool,
        changed: bool = False,
        rc: int = 0,
        reason: str = "",
        skipped: bool = False,
        stdout: Optional[list[str]] = None,
        stderr: Optional[list[str]] = None,
        value: Optional[T] = None
    ) -> None:
        self.ok = ok
        self.rc = rc
        self.changed = changed
        self.skipped = skipped
        self.reason = reason
        self.stdout = stdout or []
        self.stderr = stderr or []
        self.value = value

    def __str__(self) -> str:
        return f"(ok={self.ok}, changed={self.changed}, value={self.value})"
