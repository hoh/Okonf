from .local import LocalHost
from .ssh import SSHHost
from .lxd import LXDHost

assert SSHHost
assert LXDHost
assert LocalHost
