from pathlib import Path

from ..graph import Node
from ..result import Result


class StatInfo:
    def __init__(self, is_link: bool, mode: str, owner: str, path: str, size: int):
        self.is_link = is_link
        self.mode = mode
        self.owner = owner
        self.path = path
        self.size = size

    def __str__(self) -> str:
        return f"Stat(path={self.path}, size={self.size}, is_link={self.is_link})"


class Stat(Node['Stat', StatInfo]):
    def __init__(self, context, *, path: Path, label: str = ""):
        label = label or f'Stat: {path}'
        super().__init__(context, label=label)
        self._path = path

    def execute(self, *results: Result) -> Result[StatInfo]:
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
