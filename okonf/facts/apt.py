import re
from typing import Iterable, Dict, Tuple, Union, Optional

from okonf.connectors import Host
from okonf.facts.abstract import Fact

RE_UPGRADEABLE = r'([^\/]+)\/([^\s]+)\s+([^\s]+)\s+(\w+)\s+' \
                 r'\[upgradable from:\s+([^\s]+)\]$'


def parse_upgradeable(lines: Iterable[str]) -> Iterable[Tuple[str, Dict[str, Union[str, int]]]]:
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


class AptPresent(Fact):
    name: str
    sudo: bool

    def __init__(self, name: str, sudo: bool = True):
        self.name = name
        self.sudo = sudo

    async def enquire(self, host: Host) -> bool:
        status = await host.run("dpkg -l {}".format(self.name), check=False)
        for line in status.split('\n'):
            if re.match(r"ii\s+{}(\:amd64)?\s+".format(self.name), line):
                return True
        return False

    async def enforce(self, host: Host) -> bool:
        if self.sudo:
            await host.run("sudo apt-get install -y {}".format(self.name))
        else:
            await host.run("apt-get install -y {}".format(self.name))
        return True

    @property
    def description(self) -> str:
        return str(self.name)


class AptAbsent(AptPresent):
    purge: bool

    def __init__(self, name: str, purge: bool = False, sudo: bool = True):
        self.purge = purge
        super(AptAbsent, self).__init__(name=name, sudo=sudo)

    async def enquire(self, host) -> bool:
        return not await super().enquire(host)

    async def enforce(self, host) -> bool:
        purge = '--purge' if self.purge else ''
        if self.sudo:
            await host.run("apt-get remove {} -y {}".format(purge, self.name))
        else:
            await host.run("sudo apt-get remove {} -y {}".format(purge, self.name))
        return True


class AptUpdated(Fact):

    def __init__(self, names=tuple()):
        self.names = names

    async def enquire(self, host) -> bool:
        return False

    async def enforce(self, host) -> bool:
        await host.run("sudo apt-get update")
        return True


class AptUpgraded(Fact):
    names: Iterable

    def __init__(self, names: Optional[Iterable] = None):
        self.names = names or tuple()

    async def info(self, host: Host) -> Dict:
        names_str = ' '.join(self.names)
        status = await host.run("apt list --upgradeable {}".format(names_str))

        if status.startswith('Listing...\n'):
            status = status[len('Listing...\n'):]

        return {
            name: values
            for name, values in parse_upgradeable(status.split('\n'))
        }

    async def enquire(self, host) -> bool:
        upgradeable = await self.info(host)
        return len(upgradeable) == 0

    async def enforce(self, host) -> bool:
        await host.run("sudo apt-get upgrade")
        return True
