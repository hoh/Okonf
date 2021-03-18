import asyncio
from typing import Tuple, Dict, NewType

from typer import Typer

from .connectors.abstract import Executor
from .facts.abstract import Fact
from .utils import run_coroutine, format_collection_result, setup_logger

app = Typer()

Hosts = NewType('Hosts', Dict[str, Executor])


def load_config(file_path: str) -> Tuple[Dict[str, Fact], Hosts]:
    locals_: Dict = {}
    exec(open(file_path).read(), locals_)
    file_hosts: Hosts = locals_['hosts']
    file_configs = locals_['configs']
    return file_configs, file_hosts


async def run_on_host(host, operation):
    async with host as connection:
        return await operation(connection)


@app.command()
def check(file_path: str, host: str,
          debug: bool = False, info: bool = False):
    setup_logger(debug, info)

    file_configs, file_hosts = load_config(file_path)
    if host is None and len(file_hosts) == 1:
        host = list(file_hosts.keys())[0]
    target_host: Executor = file_hosts[host]
    target_config = file_configs[host]

    result = run_coroutine(run_on_host(target_host, target_config.check))
    print(format_collection_result(result))

    asyncio.get_event_loop().close()
    return {'checked': result}


@app.command()
def apply(file_path: str, host: str,
          debug: bool = False, info: bool = False):
    setup_logger(debug, info)

    file_configs, file_hosts = load_config(file_path)

    target_host: Executor = file_hosts[host]
    target_config = file_configs[host]

    result = run_coroutine(run_on_host(target_host, target_config.apply))
    print(format_collection_result(result))

    asyncio.get_event_loop().close()
    return {'applied': result}


if __name__ == '__main__':
    app()
