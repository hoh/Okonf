import logging
from hashlib import sha256
from asyncssh import ProcessError


async def file_is_present(host, path):
    return await host.run("ls -d {}".format(path), check=False) != ''


async def file_hashed(host, path):
    try:
        output = await host.run("sha256sum {}".format(path))
    except (ProcessError, FileNotFoundError):
        return False
    return output.split(' ', 1)[0]


async def file_contains(host, path, content):
    file_hash = await file_hashed(host, path)
    content_hash = sha256(content).hexdigest()

    logging.debug("File hash vs content: '%s' vs '%s", file_hash, content_hash)
    return content_hash == file_hash
