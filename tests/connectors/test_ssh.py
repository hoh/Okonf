import os
import pytest
from shutil import copyfile

from okonf.connectors import SSHHost
from okonf.facts.files import FilePresent, FileContent


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


@pytest.mark.asyncio
async def test_SSHHost_put():
    host = SSHHost(host='localhost', username='root')

    os.system("service ssh start")
    os.makedirs("/root/.ssh", exist_ok=True)
    os.system("ssh-keygen -t rsa -N '' -f /root/.ssh/id_rsa")
    os.system("ssh-keyscan localhost >> ~/.ssh/known_hosts")
    copyfile('/root/.ssh/id_rsa.pub', '/root/.ssh/authorized_keys')

    assert await FilePresent('/etc/hostname').check(host) is True

    filename1 = '/tmp/tmpfile'
    filename2 = '~/filename'
    filepath2 = '/root/filename'

    assert filepath2 == '/root' + filename2[1:]

    fact1 = FileContent(filename1, b'tmpfilecontent')
    fact2 = FileContent(filename2, b'filecontent')

    assert not os.path.isfile(filename1)
    assert not os.path.isfile(filename2)
    assert await fact1.check(host) is False
    assert await fact2.check(host) is False

    try:
        assert await fact1.apply(host) is True
        assert await fact2.apply(host) is True
        assert os.path.isfile(filename1)
        assert os.path.isfile(filepath2)
        assert await fact1.check(host) is True
        assert await fact2.check(host) is True
    finally:
        os.remove(filename1)
        os.remove(filepath2)
