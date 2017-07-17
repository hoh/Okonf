from tempfile import NamedTemporaryFile

from okonf.utils import get_file_hash
from okonf.facts.files import file_is_present, file_contains, file_hashed


async def file_present(host, path):
    if not await file_is_present(host, path):
        await host.run("touch {}".format(path))


async def file_absent(host, path):
    if await file_is_present(host, path):
        await host.run("rm {}".format(path))


async def file_(host, path, present=True):
    if present:
        return await file_present(host, path)
    else:
        return await file_absent(host, path)


async def file_copy(host, path, local_path: str):
    file_hash = await file_hashed(host, path)
    local_hash = get_file_hash(local_path)

    if file_hash != local_hash:
        await host.put(path, local_path)


async def file_content(host, path, content: bytes, sudo=False):
    if not await file_contains(host, path, content):
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(content)
            tmpfile.seek(0)

            if not sudo:
                await host.put(path, tmpfile.name)
            else:
                await host.put('/tmp/azerty', tmpfile.name)
                await host.run("sudo mv /tmp/azerty {}".format(path))


__all__ = ['file_present', 'file_absent', 'file_', 'file_copy',
           'file_content']