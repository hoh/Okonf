import asyncio
import logging

from pylxd import Client

from .abstract import Host
from .exceptions import NoSuchFileError, ShellError


class LXDHost(Host):
    def __init__(self, name):
        self._client = Client()
        self._container = self._client.containers.get(name)
        super(LXDHost, self).__init__()

    async def run(self, command: str, check: bool = True, no_such_file: bool = False):
        logging.info("run %s$ %s", self._container.name, command)

        command = command.split(' ')

        result = await asyncio.get_event_loop().run_in_executor(
            None, self._container.execute, command)

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
        result = self._container.files.put(path, content)
        print('put result', result)
