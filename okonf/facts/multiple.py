import asyncio

from okonf.facts.abstract import Fact, FactCheck, FactResult


class Collection(Fact):
    """
    Unordered collection of facts. All will be applied together
    asynchronously.
    """
    def __init__(self, facts):
        self.facts = list(facts)

    async def check(self, host, parent=None):
        """
        Check the state of the fact; Checks are executed in parallel, not
        in order, as they do not have side-effects.
        :param host:
        :return:
        """
        result = await asyncio.gather(
            *(step.check(host, parent=self)
              for step in self.facts)
        )
        # pprint(result)
        return FactCheck(self, result)

    async def apply(self, host):
        result = await asyncio.gather(
            *(step.apply(host)
              for step in self.facts)
        )
        print(result)
        return FactResult(self, result)

    def __add__(self, other):
        if isinstance(other, Sequence):
            return Sequence([self, other])
        elif isinstance(other, Collection):
            return Collection(self.facts + other.facts)
        else:
            raise TypeError("Unsupported type: %s", type(other))

    def __str__(self):
        module_names = [str(module_) for module_ in self.facts]
        return "\n - ".join([self.__class__.__name__] + module_names)


class Sequence(Collection):
    """
    Ordered collection of facts. Each will be applied after the previous one.
    """
    async def apply(self, host):
        result = []
        for step in self.facts:
            result.append(await step.apply(host))
            print(result)
        return FactResult(self, result)

    def __add__(self, other):
        if isinstance(other, Sequence):
            return Sequence(self.facts + other.facts)
        elif isinstance(other, Collection):
            return Sequence([self, other])
        else:
            raise TypeError("Unsupported type: %s", type(other))
