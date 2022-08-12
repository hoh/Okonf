import logging
from typing import Dict, Any

import asyncssh

from .abstract import Executor
from .exceptions import NoSuchFileError, ShellError


class SSHExecutor(Executor):
    connection: Any
    username: str

    def __init__(self, connection, username: str, is_root: bool):
        self.connection = connection
        self.username = username
        super().__init__(is_root=is_root)

    async def run(self, command: str, check=True, no_such_file=False) -> str:
        logging.info("run {self.connection} {command}")

        result = await self.connection.run(command, check=False)

        if no_such_file and result.exit_status != 0:
            if result.stderr.endswith("No such file or directory\n"):
                raise NoSuchFileError(
                    result.exit_status, stdout=result.stdout, stderr=result.stderr
                )

        if check and result.exit_status != 0:
            raise ShellError(
                result.exit_status, stdout=result.stdout, stderr=result.stderr
            )

        logging.debug("Result stdout = '%s'", result.stdout)
        return result.stdout

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
    connection: Any

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
