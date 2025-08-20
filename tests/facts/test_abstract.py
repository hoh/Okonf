import os

import pytest

from okonf import Collection, Sequence
from okonf.connectors.local import LocalHost
from okonf.facts.files import FilePresent


@pytest.mark.asyncio
async def test_Collection():
    async with LocalHost() as host:
        filename1 = "/tmp/filename1"
        filename2 = "/tmp/filename2"

        files_present = Collection(
            (
                FilePresent("/etc/hostname"),
                FilePresent("/etc/hosts"),
                FilePresent(filename1),
                FilePresent(filename2),
            )
        )

        assert os.path.isfile("/etc/hostname")
        assert os.path.isfile("/etc/hosts")
        assert not os.path.isfile(filename1)
        assert not os.path.isfile(filename2)
        assert await files_present.check(host) == [True, True, False, False]

        try:
            assert await files_present.apply(host) == [False, False, True, True]

            assert os.path.isfile(filename1)
            assert os.path.isfile(filename2)

            assert await files_present.check(host) == [True, True, True, True]

            assert await files_present.apply(host) == [False, False, False, False]
        finally:
            os.remove(filename1)
            os.remove(filename2)


@pytest.mark.asyncio
async def test_Sequence():
    async with LocalHost() as host:
        filename1 = "/tmp/filename1"
        filename2 = "/tmp/filename2"

        files_present = Sequence(
            (
                FilePresent("/etc/hostname"),
                FilePresent("/etc/hosts"),
                FilePresent(filename1),
                FilePresent(filename2),
            )
        )

        assert os.path.isfile("/etc/hostname")
        assert os.path.isfile("/etc/hosts")
        assert not os.path.isfile(filename1)
        assert not os.path.isfile(filename2)
        assert await files_present.check(host) == [True, True, False, False]

        try:
            assert await files_present.apply(host) == [False, False, True, True]

            assert os.path.isfile(filename1)
            assert os.path.isfile(filename2)

            assert await files_present.check(host) == [True, True, True, True]

            assert await files_present.apply(host) == [False, False, False, False]
        finally:
            os.remove(filename1)
            os.remove(filename2)
