import re


RE_UPGRADEABLE = '([^\/]+)\/([^\s]+)\s+([^\s]+)\s+(\w+)\s+' \
                 '\[upgradable from:\s+([^\s]+)\]$'


def _parse_upgradeable(lines):
    for line in lines:
        match = re.match(RE_UPGRADEABLE, line)
        if match:
            name, source, next_version, arch, version = match.groups()
            yield name, {
                'source': source,
                'next_version': next_version,
                'arch': arch,
                'version': version,
            }


async def apt_upgradeable(host, names=set()):
    names_str = ' '.join(names)
    status = await host.run("apt list --upgradeable {}".format(names_str))

    if status.startswith('Listing...\n'):
        status = status[len('Listing...\n'):]

    return {
        name: values
        for name, values in _parse_upgradeable(status.split('\n'))
    }


async def apt_is_upgraded(host):
    upgradeable = await apt_upgradeable()
    return len(upgradeable) == 0


async def apt_is_installed(host, name):
    status = await host.run("dpkg -l {}".format(name), check=False)
    for line in status.split('\n'):
        if re.match(r"ii\s+{}\s+".format(name), line):
            return True
    return False
