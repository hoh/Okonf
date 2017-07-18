from okonf.utils import run, setup_logger


from okonf.connectors import SSHHost, LXDHost, LocalHost
from okonf.facts import apt_upgradeable
from okonf.contracts import (apt_updated, apt_present, apt_absent,
                             file_present, file_absent, file_content,
                             file_copy)


def main():
    setup_logger()

    # host = SSHHost(host='10.42.101.251', username='ubuntu',
    #                password='plopplop')
    # host = LXDHost(name='test-dyscover')
    host = LocalHost()

    run(
        apt_upgradeable(host, ['vlan', 'wget', 'plop']),
        # apt_updated(host),
        apt_present(host, 'wget'),
        apt_present(host, 'nginx'),
        # apt_absent(host, 'nginx', autoremove=True),
        file_present(host, '/tmp/plop'),
        file_absent(host, '/tmp/plop2'),
        file_content(host, '/tmp/yolo', b'HEY'),
        file_copy(host, '/tmp/copy', 'README.md'),
    )


if __name__ == '__main__':
    main()
