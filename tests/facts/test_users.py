import pytest

from okonf.connectors import LocalHost
from okonf.facts.users import GroupMember


@pytest.mark.asyncio
async def test_GroupMember():
    host = LocalHost()
    await host.run("useradd bob")
    await host.run("groupadd coolguys")

    assert not await GroupMember('bob', 'coolguys').check(host)
    assert await GroupMember('bob', 'coolguys').apply(host)
    assert await GroupMember('bob', 'coolguys').check(host)
