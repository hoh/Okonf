from abc import abstractmethod


class Module:
    @abstractmethod
    async def check(self, host):
        pass

    @abstractmethod
    async def apply(self, host):
        pass

    async def check_apply(self, host):
        if not await self.check(host):
            return await self.apply(host)
