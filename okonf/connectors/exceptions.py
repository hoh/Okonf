from dataclasses import dataclass


@dataclass
class ShellError(Exception):
    exit_code: int
    stdout: bytes
    stderr: bytes

    def __str__(self):
        return "ShellError [{}] '{}' '{}'".format(self.exit_code,
                                                  self.stderr, self.stdout)


class NoSuchFileError(ShellError):
    pass
