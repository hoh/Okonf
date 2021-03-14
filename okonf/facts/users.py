from okonf.facts.abstract import Fact


class GroupMember(Fact):
    """Ensure that a user is member of a group"""

    def __init__(self, username: str, group: str) -> None:
        self.username = username
        self.group = group

    async def info(self, host):
        command = "groups {}".format(self.username)
        result = await host.run(command, check=False)

        prefix = "{} : ".format(self.username)
        assert result.startswith(prefix)
        return result[len(prefix):].split()

    async def enquire(self, host):
        info = await self.info(host)
        return self.group in info

    async def enforce(self, host):
        await host.run("sudo adduser {} {}".format(self.username, self.group))
        return True

    @property
    def description(self):
        return str("{} in {}".format(self.username, self.group))


class UserShell(Fact):
    """Ensure that a user uses the given shell"""

    def __init__(self, username: str, shell: str) -> None:
        self.username = username
        self.shell = shell

    async def enquire(self, host) -> bool:
        existing_shells = await host.run("cat /etc/shells", check=False)
        if self.shell not in existing_shells.split('\n'):
            raise ValueError(f"Unknown shell: '{self.shell}'")

        user_shells = await host.run("cat /etc/passwd", check=False)
        for line in user_shells.split('\n'):
            line = line.split(':')
            username = line[0]
            shell = line[-1]
            if username == self.username:
                if shell == self.shell:
                    return True
                else:
                    return False
        raise ValueError(f"Unknown user: '{self.username}'")

    async def enforce(self, host):
        raise NotImplementedError()

    @property
    def description(self):
        return f"Shell {self.shell} for {self.username}"

