import os.path

import pytest

from okonf.connectors.local import LocalHost
from okonf.facts.apt import AptPresent, AptAbsent, parse_upgradeable
from unittest.mock import patch


@pytest.mark.asyncio
async def test_AptPresent():
    async with LocalHost() as host:
        assert await AptPresent("mount").check(host)
        assert not await AptPresent("tree").check(host)
        assert not os.path.isfile("/usr/bin/tree")
        assert await AptPresent("tree").apply(host)
        assert os.path.isfile("/usr/bin/tree")
        assert await AptAbsent("tree").apply(host)
        assert not os.path.isfile("/usr/bin/tree")


APT_UPGRADABLE = """
Listing... Done
juk/testing 4:20.12.3-1 amd64 [upgradable from: 4:20.12.0-1]
konsole-kpart/testing 4:20.12.3-1 amd64 [upgradable from: 4:20.12.2-1]
""".split(
    "\n"
)


@patch("okonf.connectors.abstract.Executor.check_output")
@pytest.mark.asyncio
async def test_aptPresent_regex(mock_check_output):
    mock_check_output.return_value = """
Desired=Unknown/Install/Remove/Purge/Hold
| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend
|/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)
||/ Name           Version      Architecture Description
+++-==============-============-============-===========================================================
ii  docker-compose 1.25.0-1     all          Punctual, lightweight development environments using Docker
        """
    async with LocalHost() as host:
        assert await AptPresent("docker-compose").check(host)


def test_parse_upgradeable():
    assert list(parse_upgradeable(APT_UPGRADABLE)) == [
        (
            "juk",
            {
                "arch": "amd64",
                "next_version": "4:20.12.3-1",
                "source": "testing",
                "version": "4:20.12.0-1",
            },
        ),
        (
            "konsole-kpart",
            {
                "arch": "amd64",
                "next_version": "4:20.12.3-1",
                "source": "testing",
                "version": "4:20.12.2-1",
            },
        ),
    ]
