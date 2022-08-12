from .abstract import Fact
from ..connectors.abstract import Executor
from ..connectors.exceptions import ShellError


class FlatpakPresent(Fact):
    def __init__(self, name, system=False, sudo=False):
        self.name = name
        self.sudo = sudo

    async def enquire(self, host: Executor):
        try:
            await host.run("flatpak info {}".format(self.name), check=True)
            return True
        except ShellError:
            return False

    async def enforce(self, host: Executor):
        if self.sudo:
            await host.run("sudo flatpak install -y {}".format(self.name))
        else:
            await host.run("flatpak install -y {}".format(self.name))
        return True

    @property
    def description(self):
        return str(self.name)


class FlatpakUpdated(Fact):
    def __init__(self, names=tuple(), sudo=False):
        self.names = names
        self.sudo = sudo

    async def enquire(self, host: Executor):
        return False

    async def enforce(self, host: Executor):
        if self.sudo:
            await host.run("sudo flatpak update")
        else:
            await host.run("flatpak update")
        return True
