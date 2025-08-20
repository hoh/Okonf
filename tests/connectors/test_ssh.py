import os
import pytest
from shutil import copyfile

from okonf.connectors import SSHHost
from okonf.facts.files import FilePresent, FileContent


def start_sshd():
    os.system("service ssh start")
    os.makedirs("/root/.ssh", exist_ok=True)
    if not os.path.isfile("/root/.ssh/id_rsa"):
        os.system("ssh-keygen -t rsa -N '' -f /root/.ssh/id_rsa")
        os.system("ssh-keyscan localhost > ~/.ssh/known_hosts")
        copyfile("/root/.ssh/id_rsa.pub", "/root/.ssh/authorized_keys")


@pytest.mark.asyncio
async def test_FilePresent():
    start_sshd()

    ssh_host = SSHHost(host="localhost", username="root")
    async with ssh_host as host:
        assert await FilePresent("/etc/hostname").check(host)

        filename = "/tmp/filename"
        assert not os.path.isfile(filename)
        assert not await FilePresent(filename).check(host)

        try:
            assert await FilePresent(filename).apply(host)
            assert os.path.isfile(filename)
            assert await FilePresent(filename).check(host)
        finally:
            os.remove(filename)


@pytest.mark.asyncio
async def test_SSHHost_put():
    start_sshd()

    ssh_host = SSHHost(host="localhost", username="root")
    async with ssh_host as host:
        assert await FilePresent("/etc/hostname").check(host)

        filename1 = "/tmp/tmpfile"
        filename2 = "~/filename"
        filepath2 = "/root/filename"

        assert filepath2 == "/root" + filename2[1:]

        fact1 = FileContent(filename1, b"tmpfilecontent")
        fact2 = FileContent(filename2, b"filecontent")

        assert not os.path.isfile(filename1)
        assert not os.path.isfile(filename2)
        assert not await fact1.check(host)
        assert not await fact2.check(host)

        try:
            assert await fact1.apply(host)
            assert await fact2.apply(host)
            assert os.path.isfile(filename1)
            assert os.path.isfile(filepath2)
            assert await fact1.check(host)
            assert await fact2.check(host)
        finally:
            os.remove(filename1)
            os.remove(filepath2)
