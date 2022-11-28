import os
from abc import ABC
from hashlib import sha256
from os.path import join
from tempfile import NamedTemporaryFile
from typing import Optional, Union

from .abstract import Fact, FactCheck, FactResult
from .multiple import Collection, Sequence
from ..connectors.abstract import Executor
from ..utils import get_local_file_hash
from ..connectors.exceptions import NoSuchFileError


class PathPresent(Fact, ABC):
    """Abstract class containing methods common to FilePresent and DirectoryPresent."""

    remote_path: str
    mode_int: Optional[int]
    symbolic_link: bool

    @property
    def mode(self) -> Optional[str]:
        if self.mode_int:
            return oct(self.mode_int).strip("0o")
        else:
            return None

    def __init__(
        self,
        remote_path: str,
        mode: Optional[Union[int, str]] = None,
        symbolic_link: bool = True,
    ) -> None:
        self.mode_int = int(mode, base=8) if isinstance(mode, str) else mode
        self.remote_path = remote_path
        self.symbolic_link = symbolic_link

    async def enquire(self, host: Executor) -> bool:
        command = f'stat -c "%a %F" {self.remote_path}'
        try:
            result = await host.check_output(command, no_such_file=True)
            mode, type_ = result.split(" ", 1)
            type_ = type_.strip("\n")

            if type_ not in self.accepted_types:
                return False
            if self.mode and mode != self.mode:
                return False
            return True

        except NoSuchFileError:
            return False

    @property
    def description(self):
        return str(self.remote_path)


class FilePresent(PathPresent):
    """Ensure that a file is present"""

    @property
    def accepted_types(self):
        if self.symbolic_link:
            return "regular empty file", "regular file", "symbolic link"
        else:
            return "regular empty file", "regular file"

    async def enforce(self, host: Executor) -> bool:
        await host.check_output("touch {}".format(self.remote_path))
        if self.mode:
            await host.check_output(f"chmod {self.mode} {self.remote_path}")
        return True


class FileAbsent(FilePresent):
    """Ensure that a file is absent"""

    async def enquire(self, host: Executor) -> bool:
        return not await FilePresent.enquire(self, host)

    async def enforce(self, host: Executor) -> bool:
        await host.check_output("rm {}".format(self.remote_path))
        return True


class FileHash(Fact):
    """Ensure that a file has a given hash"""

    remote_path: str
    hash: bytes

    def __init__(self, remote_path: str, hash: bytes):
        self.remote_path = remote_path
        self.hash = hash

    async def get_hash(self, host: Executor):
        try:
            output = await host.check_output(
                "sha256sum {}".format(self.remote_path), no_such_file=True
            )
        except NoSuchFileError:
            return False
        return output.split(" ", 1)[0].encode()

    async def enquire(self, host: Executor) -> bool:
        remote_hash = await self.get_hash(host)
        return remote_hash == self.hash

    async def enforce(self, host: Executor) -> bool:
        raise NotImplementedError()


class FileCopy(Fact):
    """Ensure that a file is a copy of a local file"""

    def __init__(self, remote_path, local_path, remote_hash=None):
        """

        :param remote_path:
        :param local_path:
        :param remote_hash: Optional, hash of the remote file if known
        """
        self.remote_path = remote_path
        self.local_path = local_path
        self.remote_hash = remote_hash

    async def enquire(self, host: Executor) -> bool:
        local_hash = await get_local_file_hash(self.local_path)
        if self.remote_hash:
            return local_hash == self.remote_hash
        else:
            return await FileHash(self.remote_path, local_hash).enquire(host)

    async def enforce(self, host: Executor) -> bool:
        await host.put(self.remote_path, self.local_path)
        return True

    @property
    def description(self):
        return str(self.remote_path)


class FileContent(Fact):
    """Ensure that a file has a given content"""

    def __init__(self, remote_path, content):
        self.remote_path = remote_path
        self.content = content

    async def check(self, host: Executor):
        content_hash = sha256(self.content).hexdigest().encode()
        return await FileHash(self.remote_path, content_hash).check(host)

    async def enforce(self, host: Executor):
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(self.content)
            tmpfile.seek(0)
            await host.put(self.remote_path, tmpfile.name)
        return True

    @property
    def description(self) -> str:
        return '{"remote_path": self.remote_path, "content": ...}'


class DirectoryPresent(PathPresent):
    """Ensure that a directory is present"""

    @property
    def accepted_types(self):
        if self.symbolic_link:
            return "directory", "symbolic link"
        else:
            return "directory"

    async def enforce(self, host: Executor) -> bool:
        if self.mode:
            await host.check_output(
                f"mkdir --mode={self.mode} --parents {self.remote_path}"
            )
            # The mode is enforced in a second step since the mode of an existing directory will not be changed.
            await host.check_output(f"chmod {self.mode} {self.remote_path}")
        else:
            await host.check_output(f"mkdir --parents {self.remote_path}")
        return True


class DirectoryAbsent(DirectoryPresent):
    """Ensure that a directory is absent"""

    recursive: bool
    force: bool

    def __init__(
        self, remote_path: str, recursive: bool = False, force: bool = False
    ) -> None:
        self.recursive = recursive
        self.force = force
        super().__init__(remote_path)

    async def enquire(self, host: Executor) -> bool:
        return not await DirectoryPresent.enquire(self, host)

    async def enforce(self, host: Executor) -> bool:
        if self.force:
            recursive = "--recursive" if self.recursive else ""
            force = "--force" if self.force else ""
            await host.check_output(f"rm {recursive} {force} {self.remote_path}")
        else:
            await host.check_output("rmdir {}".format(self.remote_path))
        return True


class DirectoryCopy(Fact):
    """Ensure that a remote directory contains a copy of a local one"""

    def __init__(self, remote_path: str, local_path: str, delete: bool = False) -> None:
        self.remote_path = remote_path
        self.local_path = local_path
        self.delete = delete

    async def info_files_hash(self, host: Executor) -> dict:
        try:
            command = "find %s -type f -exec sha256sum {} +" % self.remote_path
            output = await host.check_output(command, no_such_file=True)
            result = {}
            for line in output.strip().split("\n"):
                if not line:
                    continue
                hash, path = line.split()
                result[path] = hash.encode()
            return result
        except NoSuchFileError:
            return {}

    async def info_dirs_present(self, host: Executor):
        try:
            command = "find {} -type d".format(self.remote_path)
            output = await host.check_output(command, no_such_file=True)
            result = output.strip().split("\n")
            return result if result != [""] else []
        except NoSuchFileError:
            return []

    def _get_remote_path(self, local_path):
        assert local_path.startswith(self.local_path)
        rel_path = local_path[len(self.local_path) :].strip("/")
        return join(self.remote_path, rel_path)

    def _get_local_path(self, remote_path):
        assert remote_path.startswith(self.remote_path)
        rel_path = remote_path[len(self.remote_path) :].strip("/")
        return join(self.local_path, rel_path)

    async def subfacts(self, host: Executor):
        """This fact can be defined entirely using other facts, so
        we return a structure with these facts that can be used for both
        check and apply instead of running code."""

        dirs_to_create = [DirectoryPresent(self._get_remote_path(self.local_path))]
        files_to_copy = []
        dirs_to_remove = []
        files_to_remove = []

        existing_files = await self.info_files_hash(host)

        for root, dirs, files in os.walk(self.local_path):
            remote_root = self._get_remote_path(root)

            for dirname in dirs:
                dirs_to_create.append(DirectoryPresent(join(remote_root, dirname)))

            for filename in files:
                remote_path = join(remote_root, filename)
                files_to_copy.append(
                    FileCopy(
                        remote_path,
                        join(root, filename),
                        remote_hash=existing_files.get(remote_path),
                    )
                )

        if self.delete:
            for filepath in existing_files:
                local_path = self._get_local_path(filepath)
                if not os.path.isfile(local_path):
                    files_to_remove.append(FileAbsent(filepath))

            existing_dirs = await self.info_dirs_present(host)
            for dirname in existing_dirs:
                local_path = self._get_local_path(dirname)
                if not os.path.isdir(local_path):
                    dirs_to_remove.append(DirectoryAbsent(dirname))
        else:
            files_to_remove = []
            dirs_to_remove = []

        return Collection(
            (
                # Both copy/creation and removal can be concurrent:
                Sequence(
                    (
                        Collection(dirs_to_create, title="Directories to be present"),
                        Collection(files_to_copy, title="Files to be present"),
                    ),
                    title="Directories and files to be present",
                ),
                Sequence(
                    (
                        # Must remove files before directories
                        Collection(files_to_remove, title="Files to be absent"),
                        Collection(dirs_to_remove, title="Directories to be absent"),
                    ),
                    title="Directories and files to be absent",
                )
                if self.delete
                else Collection(()),
            ),
            title=f"Directory copy from {self.local_path} to {self.remote_path}",
        )

    async def check(self, host: Executor) -> FactCheck:
        facts = await self.subfacts(host)
        return await facts.check(host)

    async def apply(self, host: Executor) -> FactResult:
        facts = await self.subfacts(host)
        return await facts.apply(host)
