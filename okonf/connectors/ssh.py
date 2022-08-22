import logging
from typing import Dict, Optional, Union

import asyncssh
from asyncssh import SSHClientConnection

from .abstract import Executor
from .exceptions import NoSuchFileError, ShellError


def to_bytes(value: Union[bytes, str, None]) -> bytes:
    if isinstance(value, bytes):
        return value
    elif isinstance(value, str):
        return value.encode()
    else:
        assert value is None
        return b""


class SSHExecutor(Executor):
    connection: SSHClientConnection
    username: str

    def __init__(self, connection: SSHClientConnection, username: str, is_root: bool):
        self.connection = connection
        self.username = username
        super().__init__(is_root=is_root)

    async def run(
        self, command: str, check=True, no_such_file=False, env: Optional[Dict] = None
    ) -> str:
        logging.info("run {self.connection} {command}")

        result = await self.connection.run(command, check=False, env=env)

        stdout = to_bytes(result.stdout)
        stderr = to_bytes(result.stderr)

        if no_such_file and result.exit_status and stderr:
            if stderr.endswith(b"No such file or directory\n"):
                raise NoSuchFileError(result.exit_status, stdout=stdout, stderr=stderr)

        if check and result.exit_status:
            raise ShellError(result.exit_status, stdout=stdout, stderr=stderr)

        logging.debug("Result stdout = '%s'", stdout)
        return stdout.decode()

    async def put(self, path, local_path) -> None:
        if path.startswith("~/"):
            username: str = self.username
            if username == "root":
                path = "/root/{}".format(path[2:])
            else:
                path = "/home/{}/{}".format(username, path[2:])

        async with self.connection.start_sftp_client() as sftp:
            await sftp.put(local_path, path)


class SSHHost:
    ssh_settings: Dict
    connection: SSHClientConnection

    def __init__(self, **kwargs):
        self.ssh_settings = kwargs
        super().__init__()

    async def __aenter__(self):
        self.connection = await asyncssh.connect(**self.ssh_settings).__aenter__()
        return SSHExecutor(
            connection=self.connection,
            username=self.ssh_settings["username"],
            is_root=(self.ssh_settings["username"] == "root"),
        )

    async def __aexit__(self, *args, **kwargs):
        return await self.connection.__aexit__(*args, **kwargs)
