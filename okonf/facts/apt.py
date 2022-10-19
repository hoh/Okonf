import re
from typing import Iterable, Dict, Tuple, Union, Optional
from pathlib import Path

from .abstract import Fact
from ..connectors.abstract import Executor

RE_UPGRADEABLE = (
    r"([^\/]+)\/([^\s]+)\s+([^\s]+)\s+(\w+)\s+" r"\[upgradable from:\s+([^\s]+)\]$"
)


def parse_upgradeable(
    lines: Iterable[str],
) -> Iterable[Tuple[str, Dict[str, Union[str, int]]]]:
    for line in lines:
        match = re.match(RE_UPGRADEABLE, line)
        if match:
            name, source, next_version, arch, version = match.groups()
            yield name, {
                "source": source,
                "next_version": next_version,
                "arch": arch,
                "version": version,
            }


class AptPresent(Fact):
    name: str
    version: Optional[str] = None
    path: Optional[Path] = None

    def __init__(
        self, name: str, version: Optional[str] = None, path: Optional[Path] = None
    ):
        self.name = name
        self.version = version
        self.path = path

    async def enquire(self, host: Executor) -> bool:
        status = await host.check_output("dpkg -l {}".format(self.name), check=False)
        version = self.version or ""
        for line in status.split("\n"):
            if re.match(r"ii\s+{}(:amd64)?\s+{}\s+".format(self.name, version), line):
                return True
        return False

    async def enforce(self, host: Executor) -> bool:
        name = self.path or self.name
        async with host.lock("apt"):
            if host.is_root:
                await host.check_output("apt-get install -y {}".format(name))
            else:
                await host.check_output("sudo apt-get install -y {}".format(name))

        return True

    @property
    def description(self) -> str:
        result = self.name
        if self.version:
            result += f" version {self.version}"
        if self.path:
            result += f" from {self.path}"
        return result


class AptAbsent(AptPresent):
    purge: bool

    def __init__(self, name: str, purge: bool = False, sudo: bool = True):
        self.purge = purge
        super(AptAbsent, self).__init__(name=name)

    async def enquire(self, host: Executor) -> bool:
        return not await super().enquire(host)

    async def enforce(self, host: Executor) -> bool:
        purge = "--purge" if self.purge else ""
        async with host.lock("apt"):
            if host.is_root:
                await host.check_output(
                    "apt-get remove {} -y {}".format(purge, self.name)
                )
            else:
                await host.check_output(
                    "sudo apt-get remove {} -y {}".format(purge, self.name)
                )
        return True


class AptUpdated(Fact):
    is_stateless = True

    def __init__(self, names=tuple()):
        self.names = names

    async def enquire(self, host: Executor) -> bool:
        return False

    async def enforce(self, host: Executor) -> bool:
        async with host.lock("apt-update"):
            await host.check_output("sudo apt-get update")
        return True


class AptUpgraded(Fact):
    names: Iterable

    def __init__(self, names: Optional[Iterable] = None):
        self.names = names or tuple()

    async def info(self, host: Executor) -> Dict:
        names_str = " ".join(self.names)
        status = await host.check_output("apt list --upgradeable {}".format(names_str))

        if status.startswith("Listing...\n"):
            status = status[len("Listing...\n") :]

        return {name: values for name, values in parse_upgradeable(status.split("\n"))}

    async def enquire(self, host: Executor) -> bool:
        upgradeable = await self.info(host)
        return len(upgradeable) == 0

    async def enforce(self, host: Executor) -> bool:
        async with host.lock("apt"):
            await host.check_output(
                "sudo apt-get upgrade --yes", env={"DEBIAN_FRONTEND": "noninteractive"}
            )
        return True
