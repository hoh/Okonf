import logging
import asyncio

from pylxd import Client

from okonf.connectors.exceptions import NoSuchFileError, ShellError


class LXDHost:
    def __init__(self, name):
        self._client = Client()
        self._container = self._client.containers.get(name)

    async def run(self, command, check=True, no_such_file=False):
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

    async def put(self, path, local_path):
        if path.startswith('~/'):
            path = '/root/' + path[2:]
        content = open(local_path, 'rb')
        result = self._container.files.put(path, content)
        print('put result', result)
