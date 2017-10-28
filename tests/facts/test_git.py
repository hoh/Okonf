import pytest

from okonf.connectors import LocalHost
from okonf.facts.apt import AptPresent
from okonf.facts.git import GitClone


@pytest.mark.asyncio
async def test_GitClone():
    host = LocalHost()
    repository = 'https://github.com/hoh/Hereby.git'
    directory = '/tmp/gitrepo'

    await AptPresent('git').check_apply(host)

    assert await GitClone(repository, directory).check(host) is False
    assert await GitClone(repository, directory).apply(host) is True
    assert await GitClone(repository, directory).check(host) is True
