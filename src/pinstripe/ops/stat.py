from ..node import Node
from ..result import Result
from ..context import Context


class StatInfo:
    def __init__(self, is_link: bool, mode: str, owner: str, path: str, size: int):
        self.is_link = is_link
        self.mode = mode
        self.owner = owner
        self.path = path
        self.size = size


class Stat(Node[StatInfo]):
    def __init__(self, context: Context, *, path: str, label: str = ""):
        super().__init__(label, context, label=label)
        self._path = path

    def execute(self) -> Result[StatInfo]:
        path = self._path
        stat = self.execute_command(
            f"""
if [ $(uname -s) == "Darwin" ]; then
    stat -x '{path}';
else
    stat '{path}';
fi
"""
        )
        size = -1
        is_link = False
        owner = ""
        mode = ""
        for line in stat.stdout:
            stripped = line.strip()
            if stripped.startswith("Size:"):
                try:
                    size = int(stripped.split()[1])
                except ValueError:
                    pass
            if "FileType: Symbolic Link" in line:
                is_link = True
            if stripped.startswith("Mode:") or stripped.startswith("Access:"):
                tokens = stripped.split()[1]
                mode = tokens.split("/")[0].lstrip("(")
            if "Uid: (" in stripped:
                uidgid = stripped.split("Uid: (")[1].strip()
                uid = uidgid.split(")")[0].strip()
                owner = uid.split("/")[1]

        stat.value = StatInfo(
            is_link=is_link, owner=owner, mode=mode, path=path, size=size
        )
        return stat
