

class ShellError(Exception):

    def __init__(self, exit_code, stdout=None, stderr=None):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return "ShellError [{}] '{}' '{}'".format(self.exit_code,
                                                  self.stderr, self.stdout)


class NoSuchFileError(ShellError):
    pass
