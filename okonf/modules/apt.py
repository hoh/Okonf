import re
from okonf.modules.abstract import Module


def parse_upgradeable(lines):
    for line in lines:
        match = re.match(RE_UPGRADEABLE, line)
        if match:
            name, source, next_version, arch, version = match.groups()
            yield name, {
                'source': source,
                'next_version': next_version,
                'arch': arch,
                'version': version,
            }


class AptPresent(Module):

    def __init__(self, name):
        self.name = name

    async def check(self, host):
        status = await host.run("dpkg -l {}".format(self.name), check=False)
        for line in status.split('\n'):
            if re.match(r"ii\s+{}\s+".format(self.name), line):
                return True
        return False

    async def apply(self, host):
        await host.run("sudo apt-get install -y {}".format(self.name))


class AptUpdated(Module):

    def __init__(self, names=tuple()):
        self.names = names

    async def info(self, host):
        names_str = ' '.join(self.names)
        status = await host.run("apt list --upgradeable {}".format(names_str))

        if status.startswith('Listing...\n'):
            status = status[len('Listing...\n'):]

        return {
            name: values
            for name, values in parse_upgradeable(status.split('\n'))
        }

    async def check(self, host):
        upgradeable = await self.check(host)
        return len(upgradeable) == 0

    async def apply(self, host):
        await host.run("sudo apt-get update")
