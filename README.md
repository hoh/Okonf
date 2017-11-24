# Okonf

Asynchronous configuration management system based on Python Asyncio.

Okonf manages the state and configuration of POSIX compatible systems.
You can use it to configure your personal computers, servers, routers, ...

Okonf promotes a **declarative syntax**, where the goal is to ensure a given
state of the target host instead of running commands on it.

Okonf emphasizes on being **easy to use as a library** in your own applications,
and **easy to extend with reusable components**.

Okonf also focuses on excellent performance by running asynchronously.

Inspired by: [pyinfra](), [Ansible](), [SaltStack]().

## Usage

```python
from okonf.connectors import LocalHost
from okonf.facts.files import FileContent
from okonf.utils import run

host = LocalHost()

run(
    FileContent('/tmp/some_file', b'Some Content').apply(host),
)
```

More advanced usage:

```python
import asyncio
from okonf.connectors.ssh import SSHHost
from okonf import Collection
from okonf.facts.files import FileContent
from okonf.facts.git import GitClone

host = SSHHost(host='127.0.0.1', username='myuser')

facts = Collection([
    FileContent('/tmp/some_file', b'Some Content'),
    GitClone('git@github.com:okeso/Okonf.git', '/opt/Okonf'),
])

loop = asyncio.get_event_loop()
loop.run_until_complete(
    Collection.apply(host),
)
```

## Collections

Okonf provides two types of collections to group tasks into new higher level
tasks: `Collection` and `Sequence`.

A `Collection` of facts will apply each of them in parallel, asynchronously.

A `Sequence` of facts will apply each fact after the previous one,
in a sequential manner.

In the example below, the two facts help prividing a common functionnality,
but they do not depend on each other and can be applied in parallel:

```python
vim_configured = Collection([
    AptPresent('vim'),
    FileCopy('~/.vimrc', 'vimrc'),
])
```

In this other example however, each fact depends on the previous one,
so they are applied sequentially:

```python
ipython_virtualenv = Sequence([
    AptPresent('virtualenv'),
    DirectoryPresent('~/.virtualenvs/'),
    Virtualenv('~/.virtualenvs/venv-ipython'),
    PipInstalled(['itpython'], '~/.virtualenvs/venv-ipython'),
])
```

## Creating facts

The example below shows the definition of the fact to ensure that a file is
present on disk. The `enquire` method returns whether the file is present,
and the `enforce` method is called if the file is absent to create it by
running shell commands on the host.


```python
from okonf.facts.abstract import Fact

class FilePresent(Fact):
    """Ensure that a file is present"""

    def __init__(self, remote_path: str) -> None:
        self.remote_path = remote_path

    async def enquire(self, host):
        command = "ls -d {}".format(self.remote_path)
        return await host.run(command, check=False) != ''

    async def enforce(self, host):
        await host.run("touch {}".format(self.remote_path))
        return True
```

## License

Okonf is licensed under the Apache License 2.0.
