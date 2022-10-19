import asyncio
from typing import Union, Any

from .abstract import Fact, FactCheck, FactResult
from ..connectors.abstract import Executor


class Collection(Fact):
    """
    Unordered collection of facts. All will be applied together
    asynchronously.
    """

    facts: Any
    title: str

    def __init__(self, facts, title: str = ""):
        self.facts = list(facts)
        self.title = title

    async def check(self, host: Executor) -> FactCheck:
        """
        Check the state of the fact; Checks are executed in parallel, not
        in order, as they do not have side-effects.
        :param host:
        :return:
        """
        result = await asyncio.gather(*(step.check(host) for step in self.facts))
        return FactCheck(fact=self, result=result, host=host)

    async def apply(self, host: Executor) -> FactResult:
        result = await asyncio.gather(*(step.apply(host) for step in self.facts))
        return FactResult(fact=self, result=result, host=host)

    async def enquire(self, host: Executor) -> bool:
        raise NotImplementedError()

    async def enforce(self, host: Executor) -> bool:
        raise NotImplementedError()

    def __add__(self, other: Union["Sequence", "Collection"]) -> "Collection":
        if isinstance(other, Sequence):
            return Sequence([self, other])
        elif isinstance(other, Collection):
            return Collection(self.facts + other.facts)
        else:
            raise TypeError("Unsupported type: %s", type(other))

    @property
    def description(self) -> str:
        if self.title:
            return "{} with {} facts".format(self.title, str(len(self.facts)))
        else:
            return "with {} facts".format(str(len(self.facts)))


class Sequence(Collection):
    """
    Ordered collection of facts. Each will be applied after the previous one.
    """

    async def apply(self, host: Executor):
        result = []
        for step in self.facts:
            result.append(await step.apply(host))
        return FactResult(self, result, host)

    def __add__(self, other: Union[Collection, "Sequence"]) -> Collection:
        if isinstance(other, Sequence):
            return Sequence(self.facts + other.facts)
        elif isinstance(other, Collection):
            return Sequence([self, other])
        else:
            raise TypeError("Unsupported type: %s", type(other))
