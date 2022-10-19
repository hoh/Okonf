import asyncio
import logging
from typing import Tuple, Dict, NewType, Optional, Callable, Union, Awaitable

from typer import Typer

from .connectors.abstract import Executor, Host
from .facts.abstract import Fact, FactResult, FactCheck
from .utils import run_coroutine, format_collection_result, setup_logger

logging.basicConfig(level=logging.DEBUG)

app = Typer()
Hosts = NewType("Hosts", Dict[str, Host])


def load_config(file_path: str) -> Tuple[Dict[str, Fact], Hosts]:
    locals_: Dict = {}
    exec(open(file_path).read(), locals_)
    file_hosts: Hosts = locals_["hosts"]
    file_configs = locals_["configs"]
    return file_configs, file_hosts


async def run_on_host(
    host: Host, operation: Callable[[Executor], Awaitable[Union[FactCheck, FactResult]]]
):
    async with host as executor:
        return await operation(executor)


@app.command()
def check(
    file_path: str,
    hosts: Optional[str] = None,
    sequential: bool = False,
    debug: bool = False,
    info: bool = False,
):
    setup_logger(debug, info)

    file_configs, file_hosts = load_config(file_path)

    if not hosts:
        hosts_list = list(file_hosts.keys())
    else:
        hosts_list = hosts.split(",")

    coroutines = [
        run_on_host(file_hosts[host], file_configs[host].check) for host in hosts_list
    ]

    if sequential:
        results = []
        for coroutine in coroutines:
            result = run_coroutine(coroutine, debug=debug)
            print(format_collection_result(result))
            results.append(result)
    else:
        results = run_coroutine(asyncio.gather(*coroutines))
        for result in results:
            print(format_collection_result(result))

    asyncio.get_event_loop().close()
    return {"checked": results}


@app.command()
def apply(
    file_path: str,
    hosts: Optional[str] = None,
    sequential: bool = False,
    debug: bool = False,
    info: bool = False,
):
    setup_logger(debug, info)

    file_configs: Dict[str, Fact]
    file_configs, file_hosts = load_config(file_path)

    if not hosts:
        hosts_list = list(file_hosts.keys())
    else:
        hosts_list = hosts.split(",")

    coroutines = [
        run_on_host(file_hosts[host], file_configs[host].apply) for host in hosts_list
    ]

    if sequential:
        results = []
        for coroutine in coroutines:
            result = run_coroutine(coroutine, debug=debug)
            print(format_collection_result(result))
            results.append(result)
    else:
        results = run_coroutine(asyncio.gather(*coroutines))
        for result in results:
            print(format_collection_result(result))

    asyncio.get_event_loop().close()
    return {"applied": results}


if __name__ == "__main__":
    app()
