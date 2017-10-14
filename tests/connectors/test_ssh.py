import os
import pytest
from shutil import copyfile

from okonf.connectors import SSHHost
from okonf.modules.files import FilePresent


@pytest.mark.asyncio
async def test_FilePresent():
    host = SSHHost(host='localhost', username='root')

    os.system("service ssh start")
    os.mkdir("/root/.ssh")
    os.system("ssh-keygen -t rsa -N '' -f /root/.ssh/id_rsa")
    os.system("ssh-keyscan localhost >> ~/.ssh/known_hosts")
    copyfile('/root/.ssh/id_rsa.pub', '/root/.ssh/authorized_keys')

    assert await FilePresent('/etc/hostname').check(host) is True

    filename = '/tmp/filename'
    assert not os.path.isfile(filename)
    assert await FilePresent(filename).check(host) is False

    try:
        assert await FilePresent(filename).apply(host) is True
        assert os.path.isfile(filename)
        assert await FilePresent(filename).check(host) is True
    finally:
        os.remove(filename)
