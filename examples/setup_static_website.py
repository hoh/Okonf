
# Test to setup a website on a server using okonf

import asyncio

import aiohttp

from okonf.utils import run
from okonf.facts.ip import interface_ipv4
from okonf.connectors import SSHHost, LXDHost
from okonf.contracts.apt import apt_present
from okonf.contracts.files import file_content, file_mode
from okonf.utils import setup_logger


async def nginx_ready(host):
    await apt_present(host, 'nginx')


async def site_ready(host):
    await file_content(host, '/var/www/html/index.html',
                       b"<html><body><h1>Hello World</h1></body></html>",
                       sudo=True)
    await file_mode(host, '/var/www/html/index.html', '644')


async def get_http(url):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        return await resp.text()



async def setup_website(host):
    _, _, ip = await asyncio.gather(
        nginx_ready(host),
        site_ready(host),
        interface_ipv4(host, 'eth0'),
    )
    html = await get_http("http://{}/".format(ip))
    assert '<h1>Hello World</h1>' in html


def main():
    setup_logger()

    host = SSHHost(host='10.42.101.251', username='ubuntu',
                   password='plopplop')

    # host = LXDHost(name='test-dyscover')

    run(
        setup_website(host)
    )
    print("OK")


if __name__ == '__main__':
    main()