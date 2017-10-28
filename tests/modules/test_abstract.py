import os
import pytest

from okonf.connectors import LocalHost
from okonf import Collection, Sequence
from okonf.modules.files import FilePresent


@pytest.mark.asyncio
async def test_Collection():
    host = LocalHost()

    filename1 = '/tmp/filename1'
    filename2 = '/tmp/filename2'

    files_present = Collection((
        FilePresent('/etc/hostname'),
        FilePresent('/etc/hosts'),
        FilePresent(filename1),
        FilePresent(filename2),
    ))

    assert os.path.isfile('/etc/hostname')
    assert os.path.isfile('/etc/hosts')
    assert not os.path.isfile(filename1)
    assert not os.path.isfile(filename2)
    assert await files_present.check(host) == [True, True, False, False]

    try:
        assert await files_present\
            .check_apply(host) == [None, None, True, True]

        assert os.path.isfile(filename1)
        assert os.path.isfile(filename2)

        assert await files_present\
            .check(host) == [True, True, True, True]

        assert await files_present\
            .check_apply(host) == [None, None, None, None]
    finally:
        os.remove(filename1)
        os.remove(filename2)


@pytest.mark.asyncio
async def test_Sequence():
    host = LocalHost()

    filename1 = '/tmp/filename1'
    filename2 = '/tmp/filename2'

    files_present = Sequence((
        FilePresent('/etc/hostname'),
        FilePresent('/etc/hosts'),
        FilePresent(filename1),
        FilePresent(filename2),
    ))

    assert os.path.isfile('/etc/hostname')
    assert os.path.isfile('/etc/hosts')
    assert not os.path.isfile(filename1)
    assert not os.path.isfile(filename2)
    assert await files_present\
        .check(host) == [True, True, False, False]

    try:
        assert await files_present\
            .check_apply(host) == [None, None, True, True]

        assert os.path.isfile(filename1)
        assert os.path.isfile(filename2)

        assert await files_present\
            .check(host) == [True, True, True, True]

        assert await files_present\
            .check_apply(host) == [None, None, None, None]
    finally:
        os.remove(filename1)
        os.remove(filename2)
