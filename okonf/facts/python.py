from typing import Iterable

from .abstract import Fact
from .files import FilePresent
from ..connectors.abstract import Host


class Virtualenv(Fact):
    """Ensure that a virtual environment is present"""

    def __init__(self, path: str, python: str = 'python3', site_packages=False,
                 always_copy=False) -> None:
        self.path = path
        self.python = python
        self.site_packages = site_packages
        self.always_copy = always_copy

    async def check(self, host: Host) -> bool:
        path = "{}/bin/python".format(self.path)
        return await FilePresent(path).check(host)

    async def enforce(self, host: Host) -> bool:
        command = ['virtualenv']

        if self.python:
            command.append('-p {0}'.format(self.python))

        if self.site_packages:
            command.append('--system-site-packages')

        if self.always_copy:
            command.append('--always-copy')

        command.append(self.path)
        command = ' '.join(command)

        await host.run(command)
        return True

    @property
    def description(self) -> str:
        return self.path


class PipInstalled(Fact):

    def __init__(self, packages: Iterable[str], virtualenv: str = None,
                 latest: bool = False) -> None:
        self.packages = packages
        self.virtualenv = virtualenv
        self.latest = latest

    async def info(self, host: Host):
        if self.virtualenv:
            if not await Virtualenv(self.virtualenv).check(host):
                return {}
            command = "{}/bin/pip freeze".format(self.virtualenv)
        else:
            command = "pip freeze"
        output = await host.run(command)
        lines = (
            line.split('==', 1)
            for line in output.strip().split('\n')
        )
        return {
            key.lower(): value
            for key, value in lines
        }

    async def enquire(self, host: Host) -> bool:
        installed = await self.info(host)
        for pkg in self.packages:
            if '==' in pkg:
                # Version specified
                pkg, version = pkg.split('==')
                if version != installed.get(pkg.lower(), False):
                    return False
            else:
                # No version specified
                if pkg.lower() not in installed:
                    return False
        return True

    async def enforce(self, host: Host) -> bool:
        if self.virtualenv:
            pip = "{}/bin/pip".format(self.virtualenv)
        else:
            pip = 'pip'

        command = "{} install {}".format(pip, ' '.join(self.packages))
        await host.run(command)
        return True

    @property
    def description(self) -> str:
        return str("{} in {}".format(','.join(self.packages), self.virtualenv))
