from .abstract import Fact
from ..connectors.abstract import Executor
from ..connectors.exceptions import ShellError

DEFAULT_REMOTE = "flathub"


class FlatpakRemoteAdded(Fact):
    name: str
    url: str

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    async def enquire(self, host: Executor) -> bool:
        output = await host.check_output("flatpak remotes")
        print("OUTPUT", [output])
        for line in output.split("\n"):
            if line.startswith(f"{self.name}\t"):
                return True
        return False

    async def enforce(self, host: Executor) -> bool:
        await host.check_output(
            f"flatpak remote-add --if-not-exists {self.name} {self.url}"
        )
        return True


class FlatpakPresent(Fact):
    def __init__(self, name, remote: str = DEFAULT_REMOTE, system=False, sudo=False):
        self.name = name
        self.sudo = sudo
        self.remote = remote

    async def enquire(self, host: Executor) -> bool:
        try:
            await host.check_output("flatpak info {}".format(self.name), check=True)
            return True
        except ShellError:
            return False

    async def enforce(self, host: Executor) -> bool:
        if self.sudo:
            await host.check_output(
                "sudo flatpak install -y {} {}".format(self.remote, self.name)
            )
        else:
            await host.check_output(
                "flatpak install -y {} {}".format(self.remote, self.name)
            )
        return True

    @property
    def description(self):
        return str(self.name)


class FlatpakUpdated(Fact):
    def __init__(self, names=tuple(), sudo=False):
        self.names = names
        self.sudo = sudo

    async def enquire(self, host: Executor) -> bool:
        return False

    async def enforce(self, host: Executor) -> bool:
        if self.sudo:
            await host.check_output("sudo flatpak -y update")
        else:
            await host.check_output("flatpak -y update")
        return True


flathub_remote_added = FlatpakRemoteAdded(
    name="flathub", url="https://flathub.org/repo/flathub.flatpakrepo"
)
