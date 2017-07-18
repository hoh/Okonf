import logging
from hashlib import sha256
from asyncssh import ProcessError

from okonf.utils import get_local_file_hash


async def get_file_hash(host, path):
    try:
        output = await host.run("sha256sum {}".format(path))
    except (ProcessError, FileNotFoundError):
        return False
    return output.split(' ', 1)[0]


async def get_file_mode(host, path):
    result = await host.run("ls -l -d {}".format(path), check=False)
    mode = result.split(' ', 1)[0]
    return mode


async def file_is_present(host, path):
    return await host.run("ls -d {}".format(path), check=False) != ''


async def file_has_hash(host, path, hash):
    file_hash = await get_file_hash(host, path)
    logging.debug("File hash vs given: '%s' vs '%s", file_hash, hash)
    return file_hash == hash


async def file_is_copy(host, path, local_path):
    file_hash = await get_file_hash(host, path)
    local_hash = get_local_file_hash(local_path)
    return file_hash == local_hash


async def file_contains(host, path, content):
    content_hash = sha256(content).hexdigest()
    return await file_has_hash(host, path, content_hash)


async def file_has_mode(host, path, mode):
    return await get_file_mode(host, path) == '-' + mode
