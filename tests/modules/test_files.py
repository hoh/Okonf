import os
import pytest
from shutil import rmtree

from okonf.connectors import LocalHost
from okonf.modules.files import FilePresent, FileAbsent, FileHash, FileCopy, \
    FileContent, DirectoryPresent, DirectoryAbsent, DirectoryCopy
from okonf.__main__ import check, check_apply


@pytest.mark.asyncio
async def test_FilePresent():
    host = LocalHost()
    assert await FilePresent('/etc/hostname').check(host) is True

    filename = '/tmp/filename'
    assert not os.path.isfile(filename)
    assert await FilePresent(filename).check(host) is False

    try:
        assert await FilePresent(filename).apply(host) is True
        assert os.path.isfile(filename)
        assert await FilePresent(filename).check(host) is True
    finally:
        os.remove(filename)


@pytest.mark.asyncio
async def test_FileAbsent():
    host = LocalHost()
    filename = '/tmp/filename'
    assert await FileAbsent(filename).check(host) is True
    open(filename, 'wb').write(b'content')
    assert await FileAbsent(filename).check(host) is False
    assert await FileAbsent(filename).apply(host) is True
    assert not os.path.isfile(filename)


@pytest.mark.asyncio
async def test_FileHash():
    host = LocalHost()
    filename = '/tmp/filename'
    expected_hash = b'ed7002b439e9ac845f22357d822bac14' \
                    b'44730fbdb6016d3ec9432297b9ec9f73'

    assert not os.path.isfile(filename)
    assert await FileHash(filename, 'hash').check(host) is False
    try:
        open(filename, 'wb').write(b'content')
        assert await FileHash(filename, '').get_hash(host) == expected_hash
        assert await FileHash(filename, expected_hash).check(host) is True
    finally:
        os.remove(filename)


@pytest.mark.asyncio
async def test_FileCopy():
    host = LocalHost()
    remote_path = '/tmp/filename'
    local_path = 'tests/modules/test_files.py'

    assert not os.path.isfile(remote_path)
    assert await FileCopy(remote_path, local_path).check(host) is False
    try:
        assert await FileCopy(remote_path, local_path).apply(host) is True
        assert open(local_path, 'rb').read() == open(remote_path, 'rb').read()
    finally:
        os.remove(remote_path)


@pytest.mark.asyncio
async def test_FileContent():
    host = LocalHost()
    remote_path = '/tmp/filename'
    content = b'content'

    assert not os.path.isfile(remote_path)
    assert await FileContent(remote_path, content).check(host) is False
    try:
        assert await FileContent(remote_path, content).apply(host) is True
        assert open(remote_path, 'rb').read() == content
    finally:
        os.remove(remote_path)


@pytest.mark.asyncio
async def test_DirectoryPresent():
    host = LocalHost()
    assert await DirectoryPresent('/etc').check(host) is True

    remote_path = '/tmp/filename'
    assert not os.path.isdir(remote_path)
    assert await DirectoryPresent(remote_path).check(host) is False

    try:
        assert await DirectoryPresent(remote_path).apply(host) is True
        assert os.path.isdir(remote_path)
        assert await DirectoryPresent(remote_path).check(host) is True
    finally:
        os.rmdir(remote_path)


@pytest.mark.asyncio
async def test_DirectoryAbsent():
    host = LocalHost()
    remote_path = '/tmp/dirname'
    assert await DirectoryAbsent(remote_path).check(host) is True
    try:
        os.makedirs(remote_path)
        assert await DirectoryAbsent(remote_path).check(host) is False
        assert await DirectoryAbsent(remote_path).apply(host) is True
    finally:
        assert not os.path.isdir(remote_path)


@pytest.mark.asyncio
async def test_DirectoryCopy():
    host = LocalHost()
    local_path = 'tests'
    remote_path = '/tmp/dirname'

    # TODO: handle recursive modules, check() should return False
    assert await check(DirectoryCopy(remote_path, local_path), host) is None
    try:
        result = await check_apply(
            DirectoryCopy(remote_path, local_path), host)
        assert len(result) == 2
        assert len(result[0][0]) > 0
        assert len(result[0][1]) > 0
        # TODO: handle recursive modules, check() should return False
        assert await check(
            DirectoryCopy(remote_path, local_path), host) is None
    finally:
        rmtree(remote_path)
