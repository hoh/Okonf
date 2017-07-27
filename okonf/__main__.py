import asyncio

from okonf.utils import run, setup_logger
from okonf.connectors import SSHHost, LXDHost, LocalHost
from okonf.modules.files import FilePresent, FileCopy, FileContent


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


async def main_async(host):
    sequence = [
        FilePresent('/tmp/plop'),
        FileCopy('/tmp/README2', 'README.md'),
        (
            FilePresent('/tmp/async'),
            FilePresent('/tmp/asonc'),
        ),
        FileContent('/tmp/LOL', b'lol'),
    ]
    print(await check(sequence, host))
    print(await check_apply(sequence, host))


def main():
    setup_logger()

    # host = SSHHost(host='10.42.101.251', username='ubuntu',
    #                password='plopplop')
    # host = LXDHost(name='test-dyscover')
    host = LocalHost()
    run(main_async(host))


if __name__ == '__main__':
    main()
