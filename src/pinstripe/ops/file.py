from typing import Union

from .node import Node, Result
from .entity import Entity

class File(Entity):
    def __init__(self, context, *, path, label=None):
        name = name or f"File: {path}"
        super().__init__(context=context, label=label)

    def execute(self) -> Result:
        stat = self.stat

        if not stat.ok:
            if self._state == "absent":
                return Result(ok=True, changed=False, reason="Directory already absent")

        if self._state == "absent":
            res = self.execute_command(["rm", "-f", self._path])
            res.changed = True
            return res

        changed = False

        if not stat.ok:
            touch = self.execute_command(["touch", self._path])
            changed = True
            if not touch.ok:
                return touch

        current_mode = None
        current_owner = None
        if stat.ok:
            current_mode = stat.value.mode
            current_owner = stat.value.owner

        if self._owner and self._owner != current_owner:
            chown = self.execute_command(["chown", self._owner, self._path])
            changed = True
            if not chown.ok:
                return chown

        if self._mode and self._mode != current_mode:
            chmod = self.execute_command(["chmod", self._mode])
            changed = True
            if not chmod.ok:
                return chmod

        return Result(ok=True, rc=0, changed=changed)
