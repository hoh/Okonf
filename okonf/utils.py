import sys
from os.path import isfile
import logging
import asyncio
import subprocess


def run(task, debug=False):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(task)
    return result


def get_local_file_hash(file_path):
    if not isfile(file_path):
        raise FileNotFoundError("No such file or directory: '{}'"
                                .format(file_path))
    local_hash = subprocess.check_output(['sha256sum', file_path])
    return local_hash.split(b' ', 1)[0]


def setup_logger(level=None):
    root_logger = logging.getLogger('')

    if level:
        root_logger.setLevel(level)
    elif '--debug' in sys.argv:
        root_logger.setLevel(logging.DEBUG)
    elif '--info' in sys.argv:
        root_logger.setLevel(logging.INFO)
    else:
        root_logger.setLevel(logging.WARNING)
