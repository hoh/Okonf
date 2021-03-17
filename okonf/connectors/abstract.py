import asyncio
from abc import ABC, abstractmethod
from asyncio import Lock
from typing import Dict


class Host(ABC):

    locks: Dict[str, Lock]

    def __init__(self):
        self.locks = {}

    @abstractmethod
    async def run(self, command: str, check: bool = True, no_such_file: bool = False) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def put(self, path: str, local_path: str) -> None:
        raise NotImplementedError()

    def lock(self, name: str):
        if name not in self.locks:
            self.locks[name] = asyncio.Lock()
        return self.locks[name]
