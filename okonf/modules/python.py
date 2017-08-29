from typing import Iterable

from okonf.modules.abstract import Module
from okonf.modules.files import FilePresent


class Virtualenv(Module):
    """Ensure that a virtual environment is present"""

    def __init__(self, path: str, python: str='python3', site_packages=False,
                 always_copy=False):
        self.path = path
        self.python = python
        self.site_packages = site_packages
        self.always_copy = always_copy

    async def check(self, host):
        path = "{}/bin/python".format(self.path)
        return await FilePresent(path).check(host)

    async def apply(self, host):
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


class PipInstalled(Module):

    def __init__(self, packages: Iterable[str], virtualenv: str=None,
                 latest: bool=False):
        self.packages = packages
        self.virtualenv = virtualenv
        self.latest = latest

    async def info(self, host):
        if self.virtualenv:
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

    async def check(self, host):
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

    async def apply(self, host):
        if self.virtualenv:
            pip = "{}/bin/pip".format(self.virtualenv)
        else:
            pip = 'pip'

        command = "{} install {}".format(pip, ' '.join(self.packages))
        await host.run(command)
        return True