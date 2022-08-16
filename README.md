# Pinstripe

A Python DSL for high-speed provisioning 

## Example

```py
from pinstripe import Context, cli, playbook, add_default_hostgroup

from pathlib import Path

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

    ctx.scoped(os="debian").run("lsb_release")


playbook("example", example_playbook)
```
