import os
import pytest
from okonf.connectors import LocalHost
from okonf.modules.files import FilePresent


@pytest.mark.asyncio
async def test_FilePresent():
    host = LocalHost()
    assert await FilePresent('/etc/hostname').check(host) is True

    new_file = '/tmp/absent'
    assert not os.path.isfile(new_file)
    assert await FilePresent(new_file).check(host) is False

    try:
        assert await FilePresent(new_file).apply(host) is True
        assert os.path.isfile(new_file)
        assert await FilePresent(new_file).check(host) is True
    finally:
        os.remove(new_file)
