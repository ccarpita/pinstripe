from pathlib import Path

from ..graph import Result
from .entity import Entity

class Directory(Entity):
    def __init__(self, context, path: Path, label=""):
        label = label or f"Directory: {path}"
        super().__init__(context=context, path=path, label=label)

    def execute(self, *result: Result) -> Result:
        stat = self.stat

        if not stat.ok:
            if self._state == "absent":
                return Result(ok=True, changed=False, reason="Directory already absent")

        if self._state == "absent":
            res = self.execute_command(["rm", "-rf", str(self._path)])
            res.changed = True
            return res

        changed = False

        if not stat.ok:
            mkdirp = self.execute_command(["mkdir", "-p", str(self._path)])
            changed = True
            if not mkdirp.ok:
                return mkdirp

        current_mode = None
        current_owner = None
        if stat.ok:
            current_mode = stat.value.mode
            current_owner = stat.value.owner

        if self._owner and self._owner != current_owner:
            chown = self.execute_command(["chown", self._owner, str(self._path)])
            changed = True
            if not chown.ok:
                return chown

        if self._mode and self._mode != current_mode:
            chmod = self.execute_command(["chmod", self._mode, str(self._path)])
            changed = True
            if not chmod.ok:
                return chmod

        return Result(ok=True, rc=0, changed=changed)
