import asyncio
import logging
from typing import Dict, Optional, Union

import asyncssh
from asyncssh import SSHClientConnection, ChannelOpenError

from .abstract import CommandResult, Host
from .abstract import Executor


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

    async def run(self, command: str, env: Optional[Dict] = None) -> CommandResult:
        logging.info("run {self.connection} {command}")

        # Opening a channel sometimes fails, so this retries a few times until it works.
        for retry in range(5):
            try:
                result = await self.connection.run(command, check=False, env=env)
                break
            except ChannelOpenError:
                logging.debug(f"Retrying {retry}/3")
                await asyncio.sleep(0)

        stdout = to_bytes(result.stdout)
        stderr = to_bytes(result.stderr)

        logging.debug("Result exit code = '%s'", result.exit_status)
        logging.debug("Result stdout = '%s'", result.stdout)
        logging.debug("Result stderr = '%s'", result.stderr)

        return CommandResult(
            exit_code=result.exit_status,
            stdout=stdout,
            stderr=stderr,
        )

    async def put(self, path, local_path) -> None:
        if path.startswith("~/"):
            username: str = self.username
            if username == "root":
                path = "/root/{}".format(path[2:])
            else:
                path = "/home/{}/{}".format(username, path[2:])

        async with self.connection.start_sftp_client() as sftp:
            await sftp.put(local_path, path)

    @property
    def hostname(self):
        return self.connection._host


class SSHHost(Host):
    ssh_settings: Dict
    connection: SSHClientConnection

    def __init__(self, **kwargs):
        self.ssh_settings = kwargs
        super().__init__()

    async def __aenter__(self) -> SSHExecutor:
        self.connection = await asyncssh.connect(**self.ssh_settings).__aenter__()
        return SSHExecutor(
            connection=self.connection,
            username=self.ssh_settings["username"],
            is_root=(self.ssh_settings["username"] == "root"),
        )

    async def __aexit__(self, *args, **kwargs):
        return await self.connection.__aexit__(*args, **kwargs)
