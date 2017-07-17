import re


async def interface_ipv4(host, name):
    status = await host.run("ip address show {}".format(name))
    ip = re.findall('inet ([\d\.]+)', status)[0]
    return ip
