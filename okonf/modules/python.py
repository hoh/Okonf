from okonf.modules.abstract import Module
from okonf.modules.files import FilePresent


class Virtualenv(Module):
    """Ensure that a virtual environment is present"""

    def __init__(self, path: str, python: str='python3', site_packages=False,
                 always_copy=False):
        self.path = path
        self.python = python
        self.site_packages = site_packages
        self.always_copy = always_copy

    async def check(self, host):
        path = "{}/bin/python".format(self.path)
        return await FilePresent(path).check(host)

    async def apply(self, host):
        command = ['virtualenv']

        if self.python:
            command.append('-p {0}'.format(self.python))

        if self.site_packages:
            command.append('--system-site-packages')

        if self.always_copy:
            command.append('--always-copy')

        command.append(self.path)
        command = ' '.join(command)

        await host.run(command)
        return True
