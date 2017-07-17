import sys
import logging
import asyncio

from okonf.contracts.apt import apt_updated, apt_installed, apt_removed
from okonf.connectors.ssh import SSHHost
from okonf.connectors.lxd import LXDHost
from okonf.facts.apt import apt_upgradeable, apt_is_installed
from okonf.contracts.files import (
    file_present, file_absent, file_, file_content, file_copy)

def run(*tasks):
    asyncio.get_event_loop().run_until_complete(
        asyncio.gather(*tasks)
    )


if __name__ == '__main__':
    rootLogger = logging.getLogger('')
    if '--debug' in sys.argv:
        rootLogger.setLevel(logging.DEBUG)
    elif '--info' in sys.argv:
        rootLogger.setLevel(logging.INFO)
    else:
        rootLogger.setLevel(logging.WARNING)

    # host = SSHHost(host='10.42.101.251', username='ubuntu',
    #                password='plopplop')

    host = LXDHost(name='test-dyscover')

    run(
        # apt_upgradeable(host, ['vlan', 'wget', 'plop']),
        # apt_updated(host),
        # apt_is_installed(host, 'wget'),
        # apt_is_installed(host, 'nginx'),
        # apt_removed(host, 'nginx', autoremove=True),
        file_present(host, '/tmp/plop'),
        file_absent(host, '/tmp/plop2'),
        file_content(host, '/tmp/yolo', b'HEY'),
        file_copy(host, '/tmp/copy', 'README.md'),
    )
