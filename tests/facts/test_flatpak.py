import pytest

from okonf.connectors import LocalHost
from okonf.facts.apt import AptPresent, AptUpdated
from okonf.facts.flatpak import FlatpakPresent, flathub_remote_added, FlatpakUpdated


@pytest.mark.asyncio
async def test_flathub_remote():
    async with LocalHost() as host:
        await AptUpdated().apply(host)
        await AptPresent("ca-certificates").apply(host)
        assert await AptPresent("flatpak").apply(host)
        assert not await flathub_remote_added.check(host)
        assert await flathub_remote_added.apply(host)
        assert await flathub_remote_added.check(host)


@pytest.mark.asyncio
async def test_FlatpakPresent():
    async with LocalHost() as host:
        assert await flathub_remote_added.check(host)

        assert not await FlatpakPresent("org.vim.Vim").check(host)
        # assert not os.path.isfile("/usr/bin/tree")
        assert await FlatpakPresent("org.vim.Vim").apply(host)
        # assert os.path.isfile("/usr/bin/tree")
        assert await FlatpakPresent("org.vim.Vim").check(host)


@pytest.mark.asyncio
async def test_FlatpakUpdated():
    async with LocalHost() as host:
        assert await flathub_remote_added.check(host)

        await FlatpakUpdated().check(host)
        assert await FlatpakUpdated().apply(host)
