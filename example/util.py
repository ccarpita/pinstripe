from typing import Callable, Union
from pinstripe import Context


class MacosDefaults:
    def __init__(self, ctx: Context):
        self.ctx = ctx.scoped(os="darwin")

    def set(self, domain, key, value):
        self.ctx.run(f"defaults read \"{domain}\" {key}")\
            .then(
                self.ctx.run(f"defaults write \"{domain}\" {key} '{value}'"),
                lambda result: "1" not in result.value)
