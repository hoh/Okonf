from hashlib import sha256
from tempfile import NamedTemporaryFile

from asyncssh import ProcessError

from okonf.modules.abstract import Module
from okonf.utils import get_local_file_hash


class FilePresent(Module):

    def __init__(self, remote_path: str):
        self.remote_path = remote_path

    async def check(self, host):
        command = "ls -d {}".format(self.remote_path)
        return await host.run(command, check=False) != ''

    async def apply(self, host):
        await host.run("touch {}".format(self.remote_path))


class FileHash(Module):

    def __init__(self, remote_path, hash):
        self.remote_path = remote_path
        self.hash = hash

    async def get_hash(self, host):
        try:
            output = await host.run("sha256sum {}".format(self.remote_path))
        except (ProcessError, FileNotFoundError):
            return False
        return output.split(' ', 1)[0].encode()

    async def check(self, host):
        remote_hash = await self.get_hash(host)
        return remote_hash == self.hash

    async def apply(self, host):
        raise NotImplemented


class FileCopy(Module):

    def __init__(self, remote_path, local_path):
        self.remote_path = remote_path
        self.local_path = local_path

    async def check(self, host):
        local_hash = get_local_file_hash(self.local_path)
        return await FileHash(self.remote_path, local_hash).check(host)

    async def apply(self, host):
        await host.put(self.remote_path, self.local_path)


class FileContent(Module):

    def __init__(self, remote_path, content):
        self.remote_path = remote_path
        self.content = content

    async def check(self, host):
        content_hash = sha256(self.content).hexdigest()
        return await FileHash(self.remote_path, content_hash).check(host)

    async def apply(self, host):
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(self.content)
            tmpfile.seek(0)
            await host.put(self.remote_path, tmpfile.name)
