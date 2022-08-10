from ..result import Result
from .entity import Entity

class File(Entity):
    def __init__(self, context, *, path, label=None):
        label = label or f"File: {path}"
        super().__init__(context=context, label=label, path=path)

    def execute(self, *results) -> Result:
        stat = self.stat

        if not stat.ok:
            if self._state == "absent":
                return Result(ok=True, reason="Directory already absent")

        if self._state == "absent":
            res = self.execute_command(["rm", "-f", str(self._path)])
            res.changed = True
            return res

        changed = False

        if not stat.ok:
            touch = self.execute_command(["touch", str(self._path)])
            changed = True
            if not touch.ok:
                return touch

        current_mode = None
        current_owner = None
        if stat.ok:
            current_mode = stat.value.mode
            current_owner = stat.value.owner

        if (not stat.ok or stat.value.size == 0) and self._contents_if_empty:
            set_contents = self.execute_command(f"""
cat > '{self._path}' << __PINSTRIPE:HERE__
{self._contents_if_empty}
__PINSTRIPE:HERE__
            """.strip())
            if not set_contents.ok:
                return set_contents
            changed = True

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
