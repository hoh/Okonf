
# Test to setup a website in a LXD container

import asyncio

import aiohttp
from pylxd import Client as LXDClient

from okonf.contracts.lxd import container_present
from okonf.utils import run
from okonf.facts.ip import interface_ipv4
from okonf.connectors import LocalHost, LXDHost
from okonf.contracts.apt import apt_present, apt_updated
from okonf.contracts.files import file_content, file_mode
from okonf.utils import setup_logger


async def get_http(url):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        return await resp.text()


async def setup_website(host):
    await apt_updated(host)
    await apt_present(host, 'nginx')
    ip = await interface_ipv4(host, 'eth0')

    html = await get_http("http://{}/".format(ip))
    assert '<em>Thank you for using nginx.</em>' in html


async def setup_container_website():
    lxdhost = LXDClient()
    await container_present(lxdhost, name='test-okonf-website')

    container = LXDHost(name='test-okonf-website')
    await setup_website(container)

    print('OK')


def main():
    setup_logger()
    run(setup_container_website())


if __name__ == '__main__':
    main()