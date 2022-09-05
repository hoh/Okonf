import logging

from .abstract import Fact
from .files import DirectoryPresent
from ..connectors.abstract import Executor


class GitClone(Fact):
    def __init__(self, repository: str, directory: str, branch: str = None) -> None:
        self.repository = repository
        self.directory = directory
        self.branch = branch

    async def get_branch(self, host: Executor) -> str:
        if not await DirectoryPresent(self.directory).check(host):
            logging.debug("Git directory absent: {}".format(self.directory))
            return ""
        command = "git -C {} rev-parse --abbrev-ref HEAD".format(self.directory)
        branch_name = await host.check_output(command)
        return branch_name.strip()

    async def enquire(self, host: Executor) -> bool:
        branch = await self.get_branch(host)
        if branch and not self.branch:
            return True
        else:
            return branch == self.branch

    async def enforce(self, host: Executor) -> bool:
        await host.check_output(
            "git clone {} {}".format(self.repository, self.directory)
        )
        return True

    @property
    def description(self) -> str:
        return str(self.directory)
