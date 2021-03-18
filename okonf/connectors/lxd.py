import asyncio
import logging
from typing import Any

from pylxd import Client

from .abstract import Executor
from .exceptions import NoSuchFileError, ShellError


class LXDExecutor(Executor):

    def __init__(self, connection, is_root: bool):
        self.connection = connection
        super().__init__(is_root=is_root)

    async def run(self, command: str, check: bool = True, no_such_file: bool = False):
        logging.info("run %s$ %s", self.connection.name, command)

        command_list = command.split(' ')

        result = await asyncio.get_event_loop().run_in_executor(
            None, self.connection.execute, command_list)

        if check and result.exit_code != 0:
            if no_such_file and result.stderr.endswith(
                    'No such file or directory\n'):
                raise NoSuchFileError(result.exit_code, stdout=result.stdout,
                                      stderr=result.stderr)
            else:
                raise ShellError(result.exit_code, stdout=result.stdout,
                                 stderr=result.stderr)
        return result.stdout

    async def put(self, path: str, local_path: str):
        if path.startswith('~/'):
            path = '/root/' + path[2:]
        content = open(local_path, 'rb')
        result = self.connection.files.put(path, content)
        print('put result', result)


class LXDHost:
    container_name: str
    connection: Any

    def __init__(self, container_name: str):
        self.container_name = container_name
        super().__init__()


    async def __aenter__(self):
        self.connection = await Client()
        client = Client()
        self.connection = client.containers.get(self.container_name)
        return LXDExecutor(connection=self.connection, is_root=True)

    async def __aexit__(self, *args, **kwargs):
        pass
