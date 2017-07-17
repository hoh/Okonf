import sys
import logging
import asyncio
import subprocess


def run_debug(tasks):
    loop = asyncio.get_event_loop()
    for task in tasks:
        loop.run_until_complete(task)
        print('*' * 20)


def run(*tasks, debug=False):
    if debug or '--debug' in sys.argv:
        return run_debug(tasks)
    else:
        asyncio.get_event_loop().run_until_complete(
            asyncio.gather(*tasks)
        )


def get_file_hash(file_path):
    local_hash = subprocess.check_output(['sha256sum', file_path])
    return local_hash.split(b' ', 1)[0]


def setup_logger(level=None):
    rootLogger = logging.getLogger('')

    if level:
        rootLogger.setLevel(level)
    elif '--debug' in sys.argv:
        rootLogger.setLevel(logging.DEBUG)
    elif '--info' in sys.argv:
        rootLogger.setLevel(logging.INFO)
    else:
        rootLogger.setLevel(logging.WARNING)