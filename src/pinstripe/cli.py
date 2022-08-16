import argparse
from re import I
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

    node_statusline: dict[Node, str] = {}
    def print_stats():
        num_ok = 0
        num_failed = 0
        num_waiting = 0
        num_running = 0
        num_soft_failed = 0
        num_changed = 0
        num_skipped = 0
        result = None
        for node in Node.all():
            if node.__class__.__name__ == "Noop":
                continue
            status = "UNKNOWN"
            if node.is_finished:
                result = node._result
                if result.skipped:
                    num_skipped += 1
                    status = "SKIPPED"
                    print(f"[SKIPPED] {node} {result}")
                elif result.ok:
                    num_ok += 1
                    status = "OK"
                elif node.can_fail:
                    num_soft_failed += 1
                    status = "SOFT-FAILED"
                else:
                    num_failed += 1
                    status = "FAILED"
                if result.changed:
                    num_changed += 1
                    status = "CHANGED"
            elif node.is_waiting:
                num_waiting += 1
                status = "WAITING"
            elif node.is_running:
                num_running += 1
                status = "RUNNING"
            result_desc = ""
            if node.is_finished:
                result_desc = f" {node.wait()}"
                statusline = f"[{status}] {node}{result_desc}"
                if node not in node_statusline or node_statusline[node] != statusline:
                    print(statusline)
                    node_statusline[node] = statusline
        print(f"Running: {num_running}, Waiting: {num_waiting}, Failed: {num_failed}, Soft Failed: {num_soft_failed}, OK: {num_ok}, Changed: {num_changed}, Skipped: {num_skipped}")

    # Draw progress graph and status lines
    while any([not n.is_finished for n in Node.all()]):
        print_stats()
        time.sleep(0.1)
    print_stats()
