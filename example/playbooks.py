#!/usr/bin/env python3

from pinstripe import Context, cli, playbook, add_default_hostgroup

from pathlib import Path

from util import MacosDefaults

add_default_hostgroup(["localhost"])

def example_playbook(ctx: Context):

    (ctx.file(Path("~/.pinstripe-example-data.yml").expanduser())
        .exists()
        .contents_if_empty("---"))

    (ctx.directory(Path("~/.pinstripe-example-dir").expanduser())
        .exists())

    (ctx.directory(Path("~/.pinstripe-legacy").expanduser())
        .exists())

    ctx.run("sw_vers").ignore_failures()

    mac_defaults = MacosDefaults(ctx)
    mac_defaults.set("Apple Global Domain", "com.apple.trackpad.forceClick", 1)

playbook("example", example_playbook)

if __name__ == "__main__":
    cli()
