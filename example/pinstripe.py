
from ..src.pinstripe import Context, cli, playbook, add_default_hostgroup

from util import MacosDefaults

add_default_hostgroup("""
www.google.com
www.bing.com
www.yahoo.com
""")

def example_playbook(ctx: Context):

    ctx.run()

    (ctx.file("~/.pinstripe-example-data.yml")
        .exists()
        .contents_if_empty("---"))

    (ctx.directory("~/.pinstripe-example-dir")
        .exists())

    (ctx.directory("~/.pinstripe-legacy")
        .exists())

    ctx.run("sw_vers").can_fail()

    mac_defaults = MacosDefaults(ctx)
    mac_defaults.set("Apple Global Domain", "com.apple.trackpad.forceClick", 1)

playbook("example", example_playbook)

if __name__ == "__main__":
    cli()
