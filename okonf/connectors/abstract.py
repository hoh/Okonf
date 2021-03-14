from abc import ABC, abstractmethod


class Host(ABC):

    @abstractmethod
    async def run(self, command: str, check: bool = True, no_such_file: bool = False) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def put(self, path: str, local_path: str) -> None:
        raise NotImplementedError()
