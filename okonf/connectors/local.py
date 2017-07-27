import logging
import asyncio
from shutil import copyfile

from okonf.connectors.exceptions import NoSuchFileError, ShellError


class LocalHost:

    def __init__(self):
        pass

    async def run(self, command, check=True, no_such_file=False):
        logging.info("run $ %s", command)

        process = await asyncio.create_subprocess_shell(
            cmd=command, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        logging.debug('RET %s', [process.returncode])

        print('D', dir(process))

        if no_such_file and process.returncode is None:
            stderr = await process.stderr.read()
            if stderr.endswith(b'No such file or directory\n'):
                raise NoSuchFileError(process.returncode,
                                      stdout=await process.stdout.read(),
                                      stderr=stderr)

        if check and process.returncode not in (None, 0, '0'):
            raise ShellError(process.returncode,
                             stdout=await process.stdout.read(),
                             stderr=await process.stderr.read())

        result = await process.stdout.read()
        logging.debug("Result stdout = '%s'", result)
        logging.debug("Result stderr = '%s'", await process.stderr.read())
        return result.decode()

    async def put(self, path, local_path):
        copyfile(local_path, path)
