from okonf.connectors.abstract import Executor
from okonf.connectors.exceptions import ShellError
from okonf.facts.abstract import Fact


class DaemonReloaded(Fact):
    """Ensure that Systemd has been reloaded."""

    def __init__(self) -> None:
        pass

    async def enquire(self, host: Executor) -> bool:
        # The config should always be reloaded
        return False

    async def enforce(self, host: Executor) -> bool:
        async with host.lock("systemctl-daemon-reload"):
            await host.run("sudo systemctl daemon-reload")
        return True


class ServiceStarted(Fact):
    """Ensure that a Systemd service is started."""

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    async def enquire(self, host: Executor) -> bool:
        command = "systemctl is-active --quiet {}".format(self.name)
        try:
            await host.run(command, check=True)
            return True
        except ShellError:
            return False

    async def enforce(self, host: Executor) -> bool:
        async with host.lock(f"systemctl-start-service-{self.name}"):
            await host.run(f"sudo systemctl start {self.name}")
        return True
