import asyncio
import logging
from os.path import expanduser
from shutil import copyfile

import colorama

from .abstract import Host
from .exceptions import NoSuchFileError, ShellError


class LocalHost(Host):

    async def run(self, command: str, check: bool = True, no_such_file: bool = False) -> str:
        logging.debug("run locally " + colorama.Fore.YELLOW + "$ %s", command)
        colorama.reinit()

        process = await asyncio.create_subprocess_shell(
            cmd=command, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout: bytes
        stderr: bytes
        stdout, stderr = await process.communicate()

        logging.debug('RET %s', [process.returncode])

        if no_such_file and process.returncode not in (None, 0, '0'):
            if stderr.endswith(b'No such file or directory\n'):
                raise NoSuchFileError(process.returncode,
                                      stdout=stdout,
                                      stderr=stderr)

        if check and process.returncode not in (None, 0, '0'):
            raise ShellError(process.returncode,
                             stdout=stdout,
                             stderr=stderr)

        result = stdout
        logging.debug("Result stdout = '%s'", result)
        logging.debug("Result stderr = '%s'", stderr)
        return result.decode()

    async def put(self, path, local_path) -> None:
        path = expanduser(path)
        copyfile(local_path, path)
