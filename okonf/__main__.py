import asyncio
import logging
from colorama import Fore

from okonf.utils import run, setup_logger
from okonf.connectors import LocalHost
from okonf.modules.files import FileContent

STEP_FORMAT = "{}{} {}{}"


def format_check(step, result: bool):
    "Format step and result in a readable colorful format"
    if result is True:
        return STEP_FORMAT.format(Fore.GREEN, 'Present', Fore.WHITE, step)
    else:
        return STEP_FORMAT.format(Fore.RED, 'Different', Fore.WHITE, step)


def format_apply(step, result: bool):
    "Format step and result in a readable colorful format"
    if result is True:
        return STEP_FORMAT.format(Fore.GREEN, 'Changed', Fore.WHITE, step)
    else:
        return STEP_FORMAT.format(Fore.MAGENTA, 'Kept', Fore.WHITE, step)


async def check_apply(step, host):
    if isinstance(step, list):
        # ordered
        result = []
        for s in step:
            result.append(await check_apply(s, host))
        return result
    elif isinstance(step, tuple):
        # unordered
        return await asyncio.gather(
            *(check_apply(s, host)
              for s in step)
        )
    else:
        if hasattr(step, 'submodules'):
            return await check_apply(await step.submodules(host), host)
        else:
            result = await step.check_apply(host)
            logging.info(format_apply(step, result))
            return result


async def check(step, host):
    if isinstance(step, tuple) or isinstance(step, list):
        # ordered or unordered won't make a difference when reading status
        result = await asyncio.gather(
            *(check(step, host)
              for step in step)
        )
        return result
    else:
        result = await step.check(host)
        logging.info(format_check(step, result))
        return result


config_list = [
    FileContent('/tmp/Hello_from_Okonf', b"Hello from Okonf"),
]


def main():
    setup_logger()
    host = LocalHost()
    result = run(check_apply(config_list, host))
    logging.info(result)


if __name__ == '__main__':
    main()
