DEFAULT_GROUP_NAME = "__default__"

HOST_GROUPS = {}

def _parse_hostlist(hostlist: str) -> list[str]:
    return [h for h in hostlist.splitlines() if h]

def add_hostgroup(name, hosts):
    if type(hosts) == list:
        HOST_GROUPS[name] = hosts
    else:
        HOST_GROUPS[name] = _parse_hostlist(hosts)

def add_default_hostgroup(hosts):
    add_hostgroup(DEFAULT_GROUP_NAME, hosts)