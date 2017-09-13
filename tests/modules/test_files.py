import os
import pytest
from okonf.connectors import LocalHost
from okonf.modules.files import FilePresent, FileAbsent, FileHash


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
