import os.path
import pytest

from okonf.connectors import LocalHost
from okonf.modules.python import Virtualenv, PipInstalled


@pytest.mark.asyncio
async def test_Virtualenv():
    host = LocalHost()
    path = '/tmp/virtualenv'

    assert not os.path.exists(path)
    assert await Virtualenv(path).check(host) is False

    assert await Virtualenv(path).apply(host) is True
    assert os.path.isdir(path)
    assert await Virtualenv(path).check(host) is True


@pytest.mark.asyncio
async def test_PipInstalled():
    host = LocalHost()
    packages = ['hereby']
    virtualenv = '/tmp/virtualenv'

    await Virtualenv(virtualenv).check_apply(host)

    assert await PipInstalled(packages, virtualenv).check(host) is False

    assert await PipInstalled(packages, virtualenv).apply(host) is True
    assert await PipInstalled(packages, virtualenv).check(host) is True
