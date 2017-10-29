import os.path
import pytest

from okonf.connectors import LocalHost
from okonf.facts.apt import AptPresent


@pytest.mark.asyncio
async def test_AptPresent():
    host = LocalHost()
    assert await AptPresent('mount').check(host)
    assert not await AptPresent('tree').check(host)
    assert not os.path.isfile('/usr/bin/tree')
    assert await AptPresent('tree').apply(host)
    assert os.path.isfile('/usr/bin/tree')
