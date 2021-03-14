import logging

from okonf.connectors import Host
from okonf.facts.abstract import Fact
from okonf.facts.files import DirectoryPresent


class GitClone(Fact):

    def __init__(self, repository: str, directory: str,
                 branch: str = None) -> None:
        self.repository = repository
        self.directory = directory
        self.branch = branch

    async def get_branch(self, host: Host) -> str:
        if not await DirectoryPresent(self.directory).check(host):
            logging.debug("Git directory absent: {}".format(self.directory))
            return False
        command = "git -C {} rev-parse --abbrev-ref HEAD" \
            .format(self.directory)
        branch_name = await host.run(command)
        return branch_name.strip()

    async def enquire(self, host: Host) -> bool:
        branch = await self.get_branch(host)
        if branch and not self.branch:
            return True
        else:
            return branch == self.branch

    async def enforce(self, host: Host) -> bool:
        await host.run("git clone {} {}"
                       .format(self.repository, self.directory))
        return True

    @property
    def description(self) -> str:
        return str(self.directory)
