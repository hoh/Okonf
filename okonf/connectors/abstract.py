import asyncio
from abc import ABC, abstractmethod
from asyncio import Lock
from typing import Dict, Optional
from dataclasses import dataclass

from .exceptions import ShellError, NoSuchFileError


@dataclass
class CommandResult:
    exit_code: Optional[int]
    stdout: bytes
    stderr: bytes


class Executor(ABC):

    locks: Dict[str, Lock]
    is_root: bool

    def __init__(self, is_root: bool):
        self.locks = {}
        self.is_root = is_root

    @abstractmethod
    async def run(
        self,
        command: str,
        env: Optional[Dict] = None,
    ) -> CommandResult:
        raise NotImplementedError()

    async def check_output(
        self, command: str, check=True, no_such_file=False, env: Optional[Dict] = None
    ) -> str:
        result = await self.run(
            command=command,
            env=env,
        )

        if no_such_file and result.exit_code and result.stderr:
            if result.stderr.endswith(b"No such file or directory\n"):
                raise NoSuchFileError(
                    result.exit_code, stdout=result.stdout, stderr=result.stderr
                )

        if check and result.exit_code:
            raise ShellError(
                result.exit_code, stdout=result.stdout, stderr=result.stderr
            )

        return result.stdout.decode()

    @abstractmethod
    async def put(self, path: str, local_path: str) -> None:
        raise NotImplementedError()

    def lock(self, name: str):
        if name not in self.locks:
            self.locks[name] = asyncio.Lock()
        return self.locks[name]

    @property
    def hostname(self):
        raise NotImplementedError()


class Host(ABC):
    @abstractmethod
    async def __aenter__(self) -> Executor:
        raise NotImplementedError()

    @abstractmethod
    async def __aexit__(self, *args, **kwargs):
        raise NotImplementedError()
