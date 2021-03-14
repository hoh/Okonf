import asyncio
from typing import Tuple, Dict, NewType

from okonf.connectors import Host
from typer import Typer

from okonf.facts.abstract import Fact
from okonf.utils import run, format_collection_result, setup_logger

app = Typer()

Hosts = NewType('Hosts', Dict[str, Host])


def load_config(file_path: str) -> Tuple[Fact, Hosts]:
    locals: Dict = {}
    exec(open(file_path).read(), locals)
    file_hosts: Hosts = locals['hosts']
    file_configs = locals['configs']
    return file_configs, file_hosts


@app.command()
def check(file_path: str, host: str,
          debug: bool=False, info: bool=False):
    setup_logger(debug, info)

    file_configs, file_hosts = load_config(file_path)
    if host is None and len(file_hosts) == 1:
        host = list(file_hosts.keys())[0]
    target_host: Host = file_hosts[host]
    target_config = file_configs[host]

    result = run(target_config.check(target_host))
    print(format_collection_result(result))

    asyncio.get_event_loop().close()
    return {'checked': result}


@app.command()
def apply(file_path: str, host: str,
          debug: bool=False, info: bool=False):
    setup_logger(debug, info)

    file_configs, file_hosts = load_config(file_path)

    target_host: Host = file_hosts[host]
    target_config = file_configs[host]

    result = run(target_config.apply(target_host))
    print(format_collection_result(result))

    asyncio.get_event_loop().close()
    return {'applied': result}


if __name__ == '__main__':
    app()

