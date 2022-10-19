from os.path import isfile
import logging
import asyncio
from asyncio.subprocess import create_subprocess_exec
from colorama import Fore


def run_coroutine(task, debug=False):
    loop = asyncio.get_event_loop()
    if debug:
        loop.set_debug(True)
    result = loop.run_until_complete(task)
    return result


async def get_local_file_hash(file_path: str) -> bytes:
    """Get the sha256 hash of a file on the local filesyste."""
    if not isfile(file_path):
        raise FileNotFoundError("No such file or directory: '{}'".format(file_path))

    subprocess = await create_subprocess_exec(
        "sha256sum", file_path, stdout=asyncio.subprocess.PIPE
    )

    if subprocess.stdout:
        local_hash = await subprocess.stdout.read()
        return local_hash.split(b" ", 1)[0]
    else:
        return b""


def setup_logger(debug, info):
    root_logger = logging.getLogger("")

    if debug:
        level = logging.DEBUG
    elif info:
        level = logging.INFO
    else:
        level = logging.WARNING

    root_logger.setLevel(level)


def format_collection_result(result, level: int = 0):
    """Format the result of running check or apply on a collection of facts,
    recursively."""
    output = ""
    if level == 0:
        output += f"{Fore.LIGHTBLUE_EX}{result.hostname}{Fore.WHITE}\n"
    output += "{}- {}\n".format("  " * level, result)
    try:
        for r in result.result:
            output += format_collection_result(r, level=level + 1)
    except TypeError:
        pass
    return output
