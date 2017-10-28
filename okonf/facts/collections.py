import asyncio
import logging

from colorama import Fore

from okonf.facts.abstract import Fact


def all_true(iterable):
    """Recursive version of the all() function"""
    for element in iterable:
        if element is False:
            return False
        elif element is True:
            pass
        elif not all_true(element):
            return False
    return True


def any_true(iterable):
    """Recursive version of the all() function"""
    for element in iterable:
        if element is True:
            return True
        elif element is False or element is None:
            pass
        elif any_true(element):
            return True
    return False


class MultipleCheckResults(list):

    def __bool__(self):
        """Recursive version of the all() function"""
        return all_true(self)

    def __repr__(self):
        return "MultipleCheckResults" + super().__repr__()


class MultipleApplyResults(list):

    def __bool__(self):
        """Recursive version of the any() function"""
        return any_true(self)

    def __repr__(self):
        return "MultipleApplyResults" + super().__repr__()


async def log_check_result(step, coroutine):
    result = await coroutine
    if result:
        logging.info("{}{} {}{}".format(
            Fore.GREEN, 'Present', Fore.WHITE, step))
    else:
        logging.info("{}{} {}{}".format(
            Fore.RED, 'Different', Fore.WHITE, step))
    return result


async def log_apply_result(step, coroutine):
    result = await coroutine
    if result:
        logging.info("{}{} {}{}".format(
            Fore.GREEN, 'Changed', Fore.WHITE, step))
    else:
        logging.info("{}{} {}{}".format(
            Fore.MAGENTA, 'Present', Fore.WHITE, step))
    return result


class Collection(Fact):
    """
    Unordered collection of facts. All will be applied together
    asynchronously.
    """
    def __init__(self, facts):
        self.facts = list(facts)

    async def check(self, host):
        """
        Check the state of the fact; Checks are executed in parallel, not
        in order, as they do not have side-effects.
        :param host:
        :return:
        """
        result = await asyncio.gather(
            *(log_check_result(step, step.check(host))
              for step in self.facts)
        )
        return MultipleCheckResults(result)

    async def apply(self, host):
        result = await asyncio.gather(
            *(log_apply_result(step, step.apply(host))
              for step in self.facts)
        )
        return MultipleApplyResults(result)

    async def check_apply(self, host):
        result = await asyncio.gather(
            *(log_apply_result(step, step.check_apply(host))
              for step in self.facts)
        )
        return MultipleApplyResults(result)

    def __add__(self, other):
        if isinstance(other, Sequence):
            return Sequence([self, other])
        elif isinstance(other, Collection):
            return Collection(self.facts + other.facts)
        else:
            raise TypeError("Unsupported type: %s", type(other))

    def __str__(self):
        fact_names = [str(fact) for fact in self.facts]
        return "\n - ".join([self.__class__.__name__] + fact_names)


class Sequence(Collection):
    """
    Ordered collection of facts. Each will be applied after the previous one.
    """

    async def apply(self, host):
        result = []
        for step in self.facts:
            result.append(await step.apply(host))
        return MultipleApplyResults(result)

    async def check_apply(self, host):
        result = []
        for step in self.facts:
            coroutine = step.check_apply(host)
            result.append(await log_apply_result(step, coroutine))
        return MultipleApplyResults(result)

    def __add__(self, other):
        if isinstance(other, Sequence):
            return Sequence(self.facts + other.facts)
        elif isinstance(other, Collection):
            return Sequence([self, other])
        else:
            raise TypeError("Unsupported type: %s", type(other))
