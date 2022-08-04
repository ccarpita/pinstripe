from ..src.pinstripe import Context

class MacosDefaults:
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def set(self, domain, key, value):
        darwin = self.ctx.scoped(os="darwin")

        def _ensure_value(context, result):
            if "1" in result.stdout:
                return
            (darwin.run(f"defaults write \"{domain}\" {key} '{value}'"))
        (darwin.run(f"defaults read \"{domain}\" {key}")
            .then(_ensure_value))
