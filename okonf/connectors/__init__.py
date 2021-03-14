import logging

from .local import LocalHost
from .ssh import SSHHost

try:
    from .lxd import LXDHost
    assert LXDHost
except ImportError:
    logger = logging.getLogger(__name__)
    logger.debug("Clound not import LXD")

assert SSHHost
assert LocalHost
