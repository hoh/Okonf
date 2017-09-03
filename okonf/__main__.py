import asyncio
import logging

from okonf.utils import run, setup_logger
from okonf.connectors import LocalHost
from okonf.modules.files import FileContent


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
            return await step.check_apply(host)


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
