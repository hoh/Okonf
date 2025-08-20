import os
import pytest
from shutil import rmtree

from okonf.connectors.local import LocalHost
from okonf.facts.files import (
    FilePresent,
    FileAbsent,
    FileHash,
    FileCopy,
    FileContent,
    DirectoryPresent,
    DirectoryAbsent,
    DirectoryCopy,
)


@pytest.mark.asyncio
async def test_FilePresent():
    async with LocalHost() as host:
        assert await FilePresent("/etc/hostname").check(host)

        filename = "/tmp/filename"
        assert not os.path.isfile(filename)
        assert not await FilePresent(filename).check(host)

        try:
            assert await FilePresent(filename).apply(host)
            assert os.path.isfile(filename)
            assert await FilePresent(filename).check(host)
        finally:
            os.remove(filename)


@pytest.mark.asyncio
async def test_FileMode():
    async with LocalHost() as host:
        assert os.stat("/etc/hostname").st_mode & 0o777 == 0o644
        assert await FilePresent("/etc/hostname", mode=0o644).check(host)
        assert await FilePresent("/etc/hostname", mode="644").check(host)

        filename = "/tmp/filename"
        assert not await FilePresent(filename, mode=0o644).check(host)

        try:
            assert await FilePresent(filename, mode=0o644).apply(host)
            assert os.path.isfile(filename)
            assert os.stat(filename).st_mode & 0o777 == 0o644

            # Change mode
            assert await FilePresent(filename, mode=0o644).check(host)
            assert not await FilePresent(filename, mode=0o666).check(host)
            assert await FilePresent(filename, mode=0o666).apply(host)
            assert os.stat(filename).st_mode & 0o777 == 0o666
            assert await FilePresent(filename, mode=0o666).check(host)
        finally:
            os.remove(filename)


@pytest.mark.asyncio
async def test_FileAbsent():
    async with LocalHost() as host:
        filename = "/tmp/filename"
        assert await FileAbsent(filename).check(host)
        open(filename, "wb").write(b"content")
        assert not await FileAbsent(filename).check(host)
        assert await FileAbsent(filename).apply(host)
        assert not os.path.isfile(filename)


@pytest.mark.asyncio
async def test_FileHash():
    async with LocalHost() as host:
        filename = "/tmp/filename"
        expected_hash = (
            b"ed7002b439e9ac845f22357d822bac1444730fbdb6016d3ec9432297b9ec9f73"
        )

        assert not os.path.isfile(filename)
        assert not await FileHash(filename, b"hash").check(host)
        try:
            open(filename, "wb").write(b"content")
            assert await FileHash(filename, b"").get_hash(host) == expected_hash
            assert await FileHash(filename, expected_hash).check(host)
        finally:
            os.remove(filename)


@pytest.mark.asyncio
async def test_FileCopy():
    async with LocalHost() as host:
        remote_path = "/tmp/filename"
        local_path = "tests/facts/test_files.py"

        assert not os.path.isfile(remote_path)
        assert not await FileCopy(remote_path, local_path).check(host)
        try:
            assert await FileCopy(remote_path, local_path).apply(host)
            assert open(local_path, "rb").read() == open(remote_path, "rb").read()
        finally:
            os.remove(remote_path)


@pytest.mark.asyncio
async def test_FileContent():
    async with LocalHost() as host:
        remote_path = "/tmp/filename"
        content = b"content"

        assert not os.path.isfile(remote_path)
        assert not await FileContent(remote_path, content).check(host)
        try:
            assert await FileContent(remote_path, content).apply(host)
            assert open(remote_path, "rb").read() == content
        finally:
            os.remove(remote_path)


@pytest.mark.asyncio
async def test_DirectoryPresent():
    async with LocalHost() as host:
        assert await DirectoryPresent("/etc").check(host)

        remote_path = "/tmp/filename"
        assert not os.path.isdir(remote_path)
        assert not await DirectoryPresent(remote_path).check(host)

        try:
            assert await DirectoryPresent(remote_path).apply(host)
            assert os.path.isdir(remote_path)
            assert await DirectoryPresent(remote_path).check(host)
        finally:
            os.rmdir(remote_path)


@pytest.mark.asyncio
async def test_DirectoryMode():
    async with LocalHost() as host:
        remote_path = "/tmp/filename"
        assert not os.path.isdir(remote_path)
        assert not await DirectoryPresent(remote_path, mode=0o644).check(host)

        try:
            assert await DirectoryPresent(remote_path, mode=0o644).apply(host)
            assert os.path.isdir(remote_path)
            assert os.stat(remote_path).st_mode & 0o777 == 0o644

            # Change mode
            assert await DirectoryPresent(remote_path, mode=0o644).check(host)
            assert not await DirectoryPresent(remote_path, mode=0o666).check(host)
            assert await DirectoryPresent(remote_path, mode=0o666).apply(host)
            assert os.stat(remote_path).st_mode & 0o777 == 0o666
            assert await DirectoryPresent(remote_path, mode=0o666).check(host)
        finally:
            os.rmdir(remote_path)


@pytest.mark.asyncio
async def test_DirectoryAbsent():
    async with LocalHost() as host:
        remote_path = "/tmp/dirname"
        assert await DirectoryAbsent(remote_path).check(host)
        try:
            os.makedirs(remote_path)
            assert not await DirectoryAbsent(remote_path).check(host)
            assert await DirectoryAbsent(remote_path).apply(host)
        finally:
            assert not os.path.isdir(remote_path)


@pytest.mark.asyncio
async def test_DirectoryCopy():
    async with LocalHost() as host:
        local_path = "tests"
        remote_path = "/tmp/dirname"

        # TODO: handle recursive facts, check() should return False
        assert not await DirectoryCopy(remote_path, local_path).check(host)
        try:
            result = await DirectoryCopy(remote_path, local_path).apply(host)
            assert len(result.result) == 2
            # assert len(result.result[0][0]) > 0
            # assert len(result.result[0][1]) > 0
            # TODO: handle recursive facts, check() should return False
            assert await DirectoryCopy(remote_path, local_path).check(host)
        finally:
            rmtree(remote_path)


@pytest.mark.asyncio
async def test_DirectoryCopyDelete():
    async with LocalHost() as host:
        local_path = "tests"
        remote_path = "/tmp/dirname"

        # TODO: handle recursive facts, check() should return False
        assert not await DirectoryCopy(remote_path, local_path, delete=True).check(host)
        try:
            result = await DirectoryCopy(remote_path, local_path, delete=True).apply(
                host
            )
            assert len(result.result) == 2
            # assert len(result.result[0][0]) > 0
            # assert len(result.result[0][1]) > 0
            # TODO: handle recursive facts, check() should return False
            assert await DirectoryCopy(remote_path, local_path, delete=True).check(host)
        finally:
            rmtree(remote_path)
