import logging
import asyncio
from shutil import copyfile


class LocalHost:

    def __init__(self):
        pass

    async def run(self, command, check=True):
        logging.info("run $ %s", command)

        process = await asyncio.create_subprocess_shell(
            cmd=command, stdout=asyncio.subprocess.PIPE)

        logging.debug('RET %s', [process.returncode])

        if check and process.returncode not in (None, '0'):
            logging.debug("Return code '%s'", process.returncode)
            raise FileNotFoundError

        result = await process.stdout.read()
        logging.debug("Result stdout = '%s'", result)
        return result.decode()

    async def put(self, path, local_path):
        copyfile(local_path, path)
