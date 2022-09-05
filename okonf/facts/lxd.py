import json

from .abstract import Fact
from ..connectors.abstract import Executor


class Container(Fact):
    def __init__(self, name: str, image: str = "images:debian/stretch"):
        self.name = name
        self.image = image

    async def info(self, host: Executor):
        command = "lxc list --format=json"
        result = json.loads(await host.check_output(command))
        existing = [container for container in result if container["name"] == self.name]
        return existing[0] if existing else None

    async def enquire(self, host: Executor):
        existing = await self.info(host)
        return existing is not None

    async def enforce(self, host: Executor):
        await host.check_output("lxc launch {} {}".format(self.image, self.name))
        return True
