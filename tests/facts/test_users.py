import pytest

from okonf.connectors import LocalHost
from okonf.facts.users import GroupMember, UserShell


@pytest.mark.asyncio
async def test_GroupMember():
    async with LocalHost() as host:
        await host.run("useradd testuser")
        await host.run("groupadd testgroup")

        assert not await GroupMember("testuser", "testgroup").check(host)
        assert await GroupMember("testuser", "testgroup").apply(host)
        assert await GroupMember("testuser", "testgroup").check(host)


@pytest.mark.asyncio
async def test_UserShell():
    async with LocalHost() as host:
        await host.run("useradd -s /bin/bash testuser2")

        assert await UserShell("testuser2", "/bin/bash").check(host)
        assert not await UserShell("testuser2", "/bin/sh").check(host)

        # Change shell to sh
        assert await UserShell("testuser2", "/bin/sh").apply(host)
        assert await UserShell("testuser2", "/bin/sh").check(host)
        assert not await UserShell("testuser2", "/bin/bash").check(host)

        # Restore the expected shell
        assert await UserShell("testuser2", "/bin/bash").apply(host)
        assert await UserShell("testuser2", "/bin/bash").check(host)
        assert not await UserShell("testuser2", "/bin/sh").check(host)
