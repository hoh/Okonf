import pytest

from okonf.connectors import LocalHost
from okonf.facts.users import GroupMember


@pytest.mark.asyncio
async def test_Virtualenv():
    host = LocalHost()
    await host.run("useradd bob")
    await host.run("groupadd coolguys")

    assert await GroupMember('bob', 'coolguys').check(host) is False
    assert await GroupMember('bob', 'coolguys').apply(host) is True
    assert await GroupMember('bob', 'coolguys').check(host) is True
