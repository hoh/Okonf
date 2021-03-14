import asyncio

from okonf.facts.abstract import Fact, FactCheck, FactResult


class Collection(Fact):
    """
    Unordered collection of facts. All will be applied together
    asynchronously.
    """
    def __init__(self, facts, title=None):
        self.facts = list(facts)
        self.title = title

    async def check(self, host):
        """
        Check the state of the fact; Checks are executed in parallel, not
        in order, as they do not have side-effects.
        :param host:
        :return:
        """
        result = await asyncio.gather(
            *(step.check(host)
              for step in self.facts)
        )
        return FactCheck(self, result)

    async def apply(self, host):
        result = await asyncio.gather(
            *(step.apply(host)
              for step in self.facts)
        )
        return FactResult(self, result)

    def __add__(self, other):
        if isinstance(other, Sequence):
            return Sequence([self, other])
        elif isinstance(other, Collection):
            return Collection(self.facts + other.facts)
        else:
            raise TypeError("Unsupported type: %s", type(other))

    @property
    def description(self):
        if self.title:
            return "{} with {} facts".format(self.title, str(len(self.facts)))
        else:
            return "with {} facts".format(str(len(self.facts)))


class Sequence(Collection):
    """
    Ordered collection of facts. Each will be applied after the previous one.
    """
    async def apply(self, host):
        result = []
        for step in self.facts:
            result.append(await step.apply(host))
        return FactResult(self, result)

    def __add__(self, other):
        if isinstance(other, Sequence):
            return Sequence(self.facts + other.facts)
        elif isinstance(other, Collection):
            return Sequence([self, other])
        else:
            raise TypeError("Unsupported type: %s", type(other))
