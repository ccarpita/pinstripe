from .provider import Provider

class OsProvider(Provider):
    NAME = "os"
    COMMAND = ["/usr/bin/uname", "-s"]