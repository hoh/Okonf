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
