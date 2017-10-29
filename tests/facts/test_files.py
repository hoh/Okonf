import os
import pytest
from shutil import rmtree

from okonf.connectors import LocalHost
from okonf.facts.files import FilePresent, FileAbsent, FileHash, FileCopy, \
    FileContent, DirectoryPresent, DirectoryAbsent, DirectoryCopy


@pytest.mark.asyncio
async def test_FilePresent():
    host = LocalHost()
    assert await FilePresent('/etc/hostname').check(host)

    filename = '/tmp/filename'
    assert not os.path.isfile(filename)
    assert not await FilePresent(filename).check(host)

    try:
        assert await FilePresent(filename).apply(host)
        assert os.path.isfile(filename)
        assert await FilePresent(filename).check(host)
    finally:
        os.remove(filename)


@pytest.mark.asyncio
async def test_FileAbsent():
    host = LocalHost()
    filename = '/tmp/filename'
    assert await FileAbsent(filename).check(host)
    open(filename, 'wb').write(b'content')
    assert not await FileAbsent(filename).check(host)
    assert await FileAbsent(filename).apply(host)
    assert not os.path.isfile(filename)


@pytest.mark.asyncio
async def test_FileHash():
    host = LocalHost()
    filename = '/tmp/filename'
    expected_hash = b'ed7002b439e9ac845f22357d822bac14' \
                    b'44730fbdb6016d3ec9432297b9ec9f73'

    assert not os.path.isfile(filename)
    assert not await FileHash(filename, 'hash').check(host)
    try:
        open(filename, 'wb').write(b'content')
        assert await FileHash(filename, '').get_hash(host) == expected_hash
        assert await FileHash(filename, expected_hash).check(host)
    finally:
        os.remove(filename)


@pytest.mark.asyncio
async def test_FileCopy():
    host = LocalHost()
    remote_path = '/tmp/filename'
    local_path = 'tests/facts/test_files.py'

    assert not os.path.isfile(remote_path)
    assert not await FileCopy(remote_path, local_path).check(host)
    try:
        assert await FileCopy(remote_path, local_path).apply(host)
        assert open(local_path, 'rb').read() == open(remote_path, 'rb').read()
    finally:
        os.remove(remote_path)


@pytest.mark.asyncio
async def test_FileContent():
    host = LocalHost()
    remote_path = '/tmp/filename'
    content = b'content'

    assert not os.path.isfile(remote_path)
    assert not await FileContent(remote_path, content).check(host)
    try:
        assert await FileContent(remote_path, content).apply(host)
        assert open(remote_path, 'rb').read() == content
    finally:
        os.remove(remote_path)


@pytest.mark.asyncio
async def test_DirectoryPresent():
    host = LocalHost()
    assert await DirectoryPresent('/etc').check(host)

    remote_path = '/tmp/filename'
    assert not os.path.isdir(remote_path)
    assert not await DirectoryPresent(remote_path).check(host)

    try:
        assert await DirectoryPresent(remote_path).apply(host)
        assert os.path.isdir(remote_path)
        assert await DirectoryPresent(remote_path).check(host)
    finally:
        os.rmdir(remote_path)


@pytest.mark.asyncio
async def test_DirectoryAbsent():
    host = LocalHost()
    remote_path = '/tmp/dirname'
    assert await DirectoryAbsent(remote_path).check(host)
    try:
        os.makedirs(remote_path)
        assert not await DirectoryAbsent(remote_path).check(host)
        assert await DirectoryAbsent(remote_path).apply(host)
    finally:
        assert not os.path.isdir(remote_path)


@pytest.mark.asyncio
async def test_DirectoryCopy():
    host = LocalHost()
    local_path = 'tests'
    remote_path = '/tmp/dirname'

    # TODO: handle recursive facts, check() should return False
    assert not await DirectoryCopy(remote_path, local_path).check(host)
    try:
        result = await DirectoryCopy(remote_path, local_path).apply(host)
        assert len(result.result) == 2
        # assert len(result.result[0][0]) > 0
        # assert len(result.result[0][1]) > 0
        # TODO: handle recursive facts, check() should return False
        assert not await DirectoryCopy(remote_path, local_path).check(host)
    finally:
        rmtree(remote_path)


@pytest.mark.asyncio
async def test_DirectoryCopyDelete():
    host = LocalHost()
    local_path = 'tests'
    remote_path = '/tmp/dirname'

    # TODO: handle recursive facts, check() should return False
    assert not await DirectoryCopy(
        remote_path, local_path, delete=True).check(host)
    try:
        result = await DirectoryCopy(
            remote_path, local_path, delete=True).apply(host)
        assert len(result.result) == 2
        # assert len(result.result[0][0]) > 0
        # assert len(result.result[0][1]) > 0
        # TODO: handle recursive facts, check() should return False
        assert not await DirectoryCopy(
            remote_path, local_path, delete=True).check(host)
    finally:
        rmtree(remote_path)
