import os
import pytest
from hashlib import sha256

from okonf.utils import get_local_file_hash


@pytest.mark.asyncio
async def test_get_local_file_hash():
    filepath = '/tmp/file_for_test'
    content = b"This is the file content\n"
    content_hash = sha256(content).hexdigest().encode()

    try:
        with open(filepath, 'wb') as f:
            f.write(content)
        file_hash = await get_local_file_hash(filepath)
        assert file_hash == content_hash
    finally:
        os.remove(filepath)
