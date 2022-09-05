from dataclasses import dataclass
from typing import Optional


@dataclass
class ShellError(Exception):
    exit_code: Optional[int]
    stdout: bytes
    stderr: bytes

    def __str__(self):
        return "ShellError [{}] '{}' '{}'".format(
            self.exit_code, self.stderr, self.stdout
        )


class NoSuchFileError(ShellError):
    pass
