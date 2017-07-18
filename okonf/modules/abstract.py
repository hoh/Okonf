from abc import abstractmethod


class Module:
    @abstractmethod
    async def check(self, host):
        pass

    @abstractmethod
    async def apply(self, host):
        pass
