import asyncio
from typing import Tuple

from apistar import Command
from apistar.frameworks.asyncio import ASyncIOApp as App

from okonf.facts.abstract import Fact
from okonf.utils import run, format_collection_result, setup_logger


def load_config(file_path: str) -> Tuple[Fact, dict]:
    locals = {}
    exec(open(file_path).read(), locals)
    file_hosts = locals['hosts']
    file_configs = locals['configs']
    return file_configs, file_hosts


def check(file_path: str, host: str,
          debug: bool=False, info: bool=False):
    setup_logger()

    file_configs, file_hosts = load_config(file_path)
    target_host = file_hosts[host]
    target_config = file_configs[host]

    result = run(target_config.check(target_host))
    print(format_collection_result(result))

    asyncio.get_event_loop().close()
    return {'checked': result}


def apply(file_path: str, host: str,
          debug: bool=False, info: bool=False):
    setup_logger()

    file_configs, file_hosts = load_config(file_path)
    target_host = file_hosts[host]
    target_config = file_configs[host]

    result = run(target_config.apply(target_host))
    print(format_collection_result(result))

    asyncio.get_event_loop().close()
    return {'applied': result}


commands = [
    Command('check', check),
    Command('apply', apply)
]

app = App(commands=commands)

if __name__ == '__main__':
    app.main()
