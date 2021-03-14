import logging
import asyncio

import colorama
from os.path import expanduser
from shutil import copyfile

from okonf.connectors.exceptions import NoSuchFileError, ShellError


class LocalHost:

    def __init__(self):
        pass

    async def run(self, command, check=True, no_such_file=False):
        logging.debug("run locally " + colorama.Fore.YELLOW + "$ %s", command)
        colorama.reinit()

        process = await asyncio.create_subprocess_shell(
            cmd=command, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

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

    async def put(self, path, local_path):
        path = expanduser(path)
        copyfile(local_path, path)
