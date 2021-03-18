import asyncio
import logging
import os
from os.path import expanduser
from shutil import copyfile

import colorama

from .abstract import Executor
from .exceptions import NoSuchFileError, ShellError


class LocalExecutor(Executor):

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

        if process.returncode and process.returncode != '0':
            if no_such_file:
                if stderr.endswith(b'No such file or directory\n'):
                    raise NoSuchFileError(process.returncode,
                                          stdout=stdout,
                                          stderr=stderr)
            elif check:
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


class LocalHost:

    async def __aenter__(self):
        return LocalExecutor(is_root=(os.getuid() == 0))

    async def __aexit__(self, *args, **kwargs):
        pass
