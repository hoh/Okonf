from typing import Iterable, List

from .abstract import Fact, FactCheck
from .files import FilePresent
from ..connectors.abstract import Executor


class Virtualenv(Fact):
    """Ensure that a virtual environment is present"""

    def __init__(
        self, path: str, python: str = "python3", site_packages=False, always_copy=False
    ) -> None:
        self.path = path
        self.python = python
        self.site_packages = site_packages
        self.always_copy = always_copy

    async def check(self, host: Executor) -> FactCheck:
        path = "{}/bin/python".format(self.path)
        return await FilePresent(path).check(host)

    async def enquire(self, host: Executor) -> bool:
        # self.check is implemented instead
        raise NotImplementedError()

    async def enforce(self, host: Executor) -> bool:
        command_list: List[str] = [self.python, "-m", "venv"]

        if self.site_packages:
            command_list.append("--system-site-packages")

        if self.always_copy:
            command_list.append("--always-copy")

        command_list.append(self.path)
        command: str = " ".join(command_list)

        await host.check_output(command)
        return True

    @property
    def description(self) -> str:
        return self.path


class PipInstalled(Fact):
    def __init__(
        self, packages: Iterable[str], virtualenv: str = None, latest: bool = False
    ) -> None:
        self.packages = packages
        self.virtualenv = virtualenv
        self.latest = latest

    async def info(self, host: Executor):
        if self.virtualenv:
            if not await Virtualenv(self.virtualenv).check(host):
                return {}
            command = "{}/bin/pip freeze".format(self.virtualenv)
        else:
            command = "pip freeze"
        output = await host.check_output(command)
        lines = (line.split("==", 1) for line in output.strip().split("\n") if line)
        return {key.lower(): value for key, value in lines}

    async def enquire(self, host: Executor) -> bool:
        installed = await self.info(host)
        for pkg in self.packages:
            if "==" in pkg:
                # Version specified
                pkg, version = pkg.split("==")
                if version != installed.get(pkg.lower(), False):
                    return False
            else:
                # No version specified
                if pkg.lower() not in installed:
                    return False
        return True

    async def enforce(self, host: Executor) -> bool:
        if self.virtualenv:
            pip = "{}/bin/pip".format(self.virtualenv)
        else:
            pip = "pip"

        command = "{} install {}".format(pip, " ".join(self.packages))
        await host.check_output(command)
        return True

    @property
    def description(self) -> str:
        return str("{} in {}".format(",".join(self.packages), self.virtualenv))
