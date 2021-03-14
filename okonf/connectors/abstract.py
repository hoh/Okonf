from abc import ABC, abstractmethod


class Host(ABC):

    @abstractmethod
    async def run(self, command, check=True, no_such_file=False) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    async def put(self, path, local_path) -> None:
        raise NotImplementedError()
