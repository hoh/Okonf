import os.path
import pytest

from okonf.connectors import LocalHost
from okonf.modules.apt import AptPresent


@pytest.mark.asyncio
async def test_AptPresent():
    host = LocalHost()
    assert await AptPresent('mount').check(host) is True
    assert await AptPresent('tree').check(host) is False
    assert not os.path.isfile('/usr/bin/tree')
    assert await AptPresent('tree').apply(host) is True
    assert os.path.isfile('/usr/bin/tree')
