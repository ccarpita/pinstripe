import argparse
import sys
import time

from .context import Context
from .hosts import HOST_GROUPS, DEFAULT_GROUP_NAME
from .graph import Node
from .playbook import PLAYBOOKS
from .ops.facts.os import OsProvider

def fatal(mesg: str, rc=1):
    sys.stderr.write(mesg + "\n")
    sys.exit(rc)

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("playbook")
    parser.add_argument("-l", "--hostgroup")
    args = parser.parse_args()
    hostgroup = args.hostgroup or DEFAULT_GROUP_NAME
    playbook = args.playbook
    if playbook not in PLAYBOOKS:
        pbdesc = ", ".join(PLAYBOOKS.keys())
        fatal(f"Playbook not found: {playbook}. Available playbooks: {pbdesc}")
    playbook_fn = PLAYBOOKS[playbook]

    for host in HOST_GROUPS[hostgroup]:
        context = Context(host=host)
        context.facts.register_provider("os", OsProvider(context))
        playbook_fn(context)
    for node in Node.all():
        node.start()

    # Draw progress graph and status lines
    while any([not n.is_finished for n in Node.all()]):
        num_ok = 0
        num_failed = 0
        num_waiting = 0
        num_running = 0
        num_soft_failed = 0
        for node in Node.all():
            if node.is_finished:
                result = node.wait()
                if result.ok:
                    num_ok += 1
                elif node.can_fail:
                    num_soft_failed += 1
                else:
                    num_failed += 1
            elif node.is_waiting:
                num_waiting += 1
            elif node.is_running:
                num_running += 1
        print(f"Running: {num_running}, Waiting: {num_waiting}, Failed: {num_failed}, Soft Failed: {num_soft_failed}, OK: {num_ok}")
        time.sleep(0.2)
