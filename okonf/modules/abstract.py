import colorama
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

    @property
    def description(self):
        return str(self.__dict__)

    def __str__(self):
        arguments = (colorama.Fore.CYAN +
                     str(self.description) +
                     colorama.Style.RESET_ALL)
        return ' '.join((self.__class__.__name__, arguments))

    def __repr__(self):
        return "<{}[{}]>".format(self.__class__.__name__,
                                 self.description)
