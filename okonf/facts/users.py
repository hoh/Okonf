from typing import List

from .abstract import Fact
from ..connectors.abstract import Executor


class GroupMember(Fact):
    """Ensure that a user is member of a group"""

    username: str
    group: str

    def __init__(self, username: str, group: str) -> None:
        self.username = username
        self.group = group

    async def info(self, host: Executor) -> List[str]:
        command = "groups {}".format(self.username)
        result = await host.check_output(command, check=False)

        prefix = "{} : ".format(self.username)
        assert result.startswith(prefix)
        return result[len(prefix) :].split()

    async def enquire(self, host: Executor) -> bool:
        info = await self.info(host)
        return self.group in info

    async def enforce(self, host: Executor) -> bool:
        await host.check_output("sudo adduser {} {}".format(self.username, self.group))
        return True

    @property
    def description(self) -> str:
        return str("{} in {}".format(self.username, self.group))


class UserShell(Fact):
    """Ensure that a user uses the given shell"""

    username: str
    shell: str

    def __init__(self, username: str, shell: str) -> None:
        self.username = username
        self.shell = shell

    async def enquire(self, host: Executor) -> bool:
        existing_shells = await host.check_output("cat /etc/shells", check=False)
        if self.shell not in existing_shells.split("\n"):
            raise ValueError(f"Unknown shell: '{self.shell}'")

        user_shells = await host.check_output("cat /etc/passwd", check=False)
        for line in user_shells.split("\n"):
            fields = line.split(":")
            username = fields[0]
            shell = fields[-1]
            if username == self.username:
                if shell == self.shell:
                    return True
                else:
                    return False
        raise ValueError(f"Unknown user: '{self.username}'")

    async def enforce(self, host: Executor):
        await host.check_output(f"chsh --shell {self.shell} {self.username}")
        return True

    @property
    def description(self) -> str:
        return f"Shell {self.shell} for {self.username}"
