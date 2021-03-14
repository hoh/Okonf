import pytest

from okonf.connectors import LocalHost
from okonf.facts.users import GroupMember, UserShell


@pytest.mark.asyncio
async def test_GroupMember():
    host = LocalHost()
    await host.run("useradd testuser")
    await host.run("groupadd testgroup")

    assert not await GroupMember('testuser', 'testgroup').check(host)
    assert await GroupMember('testuser', 'testgroup').apply(host)
    assert await GroupMember('testuser', 'testgroup').check(host)


@pytest.mark.asyncio
async def test_UserShell():
    host = LocalHost()
    await host.run("useradd testuser")

    assert await UserShell('testuser', '/bin/bash').check()
    assert not await UserShell('testuser', '/bin/sh').check()

    # Change shell to sh
    assert await UserShell('testuser', '/bin/sh').apply()
    assert await UserShell('testuser', '/bin/bash').check()
    assert not await UserShell('testuser', '/bin/sh').check()

    # Restore the expected shell
    assert await UserShell('testuser', '/bin/bash').apply()
    assert await UserShell('testuser', '/bin/bash').check()
    assert not await UserShell('testuser', '/bin/sh').check()


