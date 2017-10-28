import logging

from okonf.facts.abstract import Fact
from okonf.facts.files import DirectoryPresent


class GitClone(Fact):

    def __init__(self, repository: str, directory: str,
                 branch: str=None) -> None:
        self.repository = repository
        self.directory = directory
        self.branch = branch

    async def get_branch(self, host):
        if not await DirectoryPresent(self.directory).check(host):
            logging.debug("Git directory absent: {}".format(self.directory))
            return False
        command = "git -C {} rev-parse --abbrev-ref HEAD" \
                  .format(self.directory)
        branch_name = await host.run(command)
        return branch_name.strip()

    async def check(self, host):
        branch = await self.get_branch(host)
        if branch and not self.branch:
            return True
        else:
            return branch == self.branch

    async def apply(self, host):
        await host.run("git clone {} {}"
                       .format(self.repository, self.directory))
        return True

    @property
    def description(self):
        return str(self.directory)
