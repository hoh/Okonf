import json

from okonf.facts.abstract import Fact


class Container(Fact):

    def __init__(self, name: str, image: str='images:debian/stretch') -> None:
        self.name = name
        self.image = image

    async def info(self, host):
        command = "lxc list --format=json"
        result = json.loads(await host.run(command))
        existing = [container for container in result
                    if container['name'] == self.name]
        return existing[0] if existing else None

    async def enquire(self, host):
        existing = await self.info(host)
        return existing is not None

    async def enforce(self, host):
        await host.run("lxc launch {} {}"
                       .format(self.image, self.name))
        return True
