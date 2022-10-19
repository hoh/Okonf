import asyncio
import logging
import os
from os.path import expanduser
from shutil import copyfile
from typing import Optional, Dict

import colorama

from .abstract import Executor, CommandResult, Host


class LocalExecutor(Executor):
    async def run(
        self,
        command: str,
        env: Optional[Dict] = None,
    ) -> CommandResult:
        logging.debug("run locally " + colorama.Fore.YELLOW + "$ %s", command)
        colorama.reinit()

        process = await asyncio.create_subprocess_shell(
            cmd=command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        stdout: bytes
        stderr: bytes
        stdout, stderr = await process.communicate()

        logging.debug("Result exit code = '%s'", process.returncode)
        logging.debug("Result stdout = '%s'", stdout)
        logging.debug("Result stderr = '%s'", stderr)

        return CommandResult(
            exit_code=process.returncode,
            stdout=stdout,
            stderr=stderr,
        )

    async def put(self, path, local_path) -> None:
        path = expanduser(path)
        copyfile(local_path, path)

    @property
    def hostname(self):
        return "local host"


class LocalHost(Host):
    async def __aenter__(self) -> LocalExecutor:
        return LocalExecutor(is_root=(os.getuid() == 0))

    async def __aexit__(self, *args, **kwargs):
        pass
